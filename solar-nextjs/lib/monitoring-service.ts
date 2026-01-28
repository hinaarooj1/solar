import { getWatchPowerAPI } from './watchpower-api';
import { getEmailService, DailySummaryData } from './email-service';
import { getTelegramService } from './telegram-service';
import { getDiscordService } from './discord-service';
import settingsStorage from './settings-storage';

interface MonitoringState {
  lastGridFeedCheck: Date | null;
  lastLoadSheddingAlertTime: Date | null;
  lastResetAlertTime: Date | null;
  lastDailySummaryDate: string | null;
  lastDataTimestamp: Date;
  lastSystemOfflineAlertTime: Date | null;
  isLoadShedding: boolean;
  systemResetDetected: boolean;
  systemOnline: boolean;
  lastKnownOutputPriority: string | null;
  gridFeedingEnabled: boolean;
  previousGridFeedStatus: boolean;
}

export class MonitoringService {
  private state: MonitoringState;
  private config: {
    gridFeedAlertIntervalHours: number;
    loadSheddingVoltageThreshold: number;
    systemOfflineThresholdMinutes: number;
    lowProductionThresholdWatts: number;
  };

  constructor() {
    this.state = {
      lastGridFeedCheck: null,
      lastLoadSheddingAlertTime: null,
      lastResetAlertTime: null,
      lastDailySummaryDate: null,
      lastDataTimestamp: new Date(),
      lastSystemOfflineAlertTime: null,
      isLoadShedding: false,
      systemResetDetected: false,
      systemOnline: true,
      lastKnownOutputPriority: null,
      gridFeedingEnabled: true,
      previousGridFeedStatus: true,
    };

    this.config = {
      gridFeedAlertIntervalHours: parseInt(process.env.GRID_FEED_ALERT_INTERVAL_HOURS || '1'),
      loadSheddingVoltageThreshold: parseFloat(process.env.LOAD_SHEDDING_VOLTAGE_THRESHOLD || '180'),
      systemOfflineThresholdMinutes: parseInt(process.env.SYSTEM_OFFLINE_THRESHOLD_MINUTES || '10'),
      lowProductionThresholdWatts: parseFloat(process.env.LOW_PRODUCTION_THRESHOLD_WATTS || '500'),
    };

    // Initialize grid feed status asynchronously
    this.initializeGridFeedStatus();

    console.log('✅ Monitoring service initialized');
  }

  /**
   * Initialize grid feed status from storage
   */
  private async initializeGridFeedStatus(): Promise<void> {
    try {
      const savedStatus = await settingsStorage.get('grid_feeding_enabled', true);
      this.state.gridFeedingEnabled = savedStatus;
      this.state.previousGridFeedStatus = savedStatus;
    } catch (error) {
      console.error('Error loading grid feed status:', error);
    }
  }

  /**
   * Update data timestamp (called when API data is successfully fetched)
   */
  updateDataTimestamp(): void {
    this.state.lastDataTimestamp = new Date();
    if (!this.state.systemOnline) {
      console.log('✅ System is back online!');
      this.state.systemOnline = true;
      this.state.lastSystemOfflineAlertTime = null;
    }
  }

  /**
   * Get current system data from WatchPower API
   */
  async getCurrentSystemData(): Promise<{ outputPriority: string; gridVoltage: number; success: boolean }> {
    try {
      const api = await getWatchPowerAPI();
      const today = new Date().toISOString().split('T')[0];
      const data = await api.getDailyData(today);

      const rows = data?.dat?.row || [];
      if (rows.length === 0) {
        return { outputPriority: 'Unknown', gridVoltage: 0.0, success: false };
      }

      // Update timestamp on successful API call
      this.updateDataTimestamp();

      const latestRow = rows[rows.length - 1];
      const fields = latestRow.field || [];

      const outputPriority = (fields.length > 38 && fields[38]) ? String(fields[38]) : 'Unknown';
      const utilityVoltage = (fields.length > 6 && fields[6]) ? parseFloat(fields[6]) : 0.0;
      const generatorVoltage = (fields.length > 8 && fields[8]) ? parseFloat(fields[8]) : 0.0;
      const gridVoltage = utilityVoltage === 0.0 ? generatorVoltage : utilityVoltage;

      return { outputPriority, gridVoltage, success: true };
    } catch (error: any) {
      console.error('Error fetching system data:', error.message);
      return { outputPriority: 'Unknown', gridVoltage: 0.0, success: false };
    }
  }

  /**
   * Check if system has gone offline
   */
  async checkSystemOffline(): Promise<void> {
    try {
      const now = new Date();
      const timeSinceLastData = now.getTime() - this.state.lastDataTimestamp.getTime();
      const thresholdMs = this.config.systemOfflineThresholdMinutes * 60 * 1000;

      if (timeSinceLastData > thresholdMs && this.state.systemOnline) {
        // System has gone offline
        this.state.systemOnline = false;
        const minutesOffline = Math.floor(timeSinceLastData / 60000);

        console.log(`🚨 System offline detected! Last seen ${minutesOffline} minutes ago`);

        const emailService = getEmailService();
        const telegramService = getTelegramService();
        const discordService = getDiscordService();

        await Promise.allSettled([
          emailService.sendSystemShutdownAlert(minutesOffline),
          telegramService.sendSystemOfflineAlert(minutesOffline),
          discordService.sendSystemOfflineAlert(minutesOffline),
        ]);

        this.state.lastSystemOfflineAlertTime = now;
      }
    } catch (error: any) {
      console.error('Error in system offline check:', error.message);
    }
  }

  /**
   * Check for system reset (Output Priority change)
   */
  async checkSystemReset(outputPriority: string): Promise<void> {
    try {
      const EXPECTED_OUTPUT_PRIORITY = 'Solar Utility Bat';
      const now = new Date();

      if (outputPriority === 'Unknown') return;

      const isReset = outputPriority !== EXPECTED_OUTPUT_PRIORITY;

      if (isReset) {
        const shouldSendAlert =
          !this.state.systemResetDetected ||
          !this.state.lastResetAlertTime ||
          now.getTime() - this.state.lastResetAlertTime.getTime() >= 60 * 60 * 1000; // 1 hour

        if (shouldSendAlert) {
          console.log(`🚨 System reset detected! Priority: ${outputPriority}`);

          const emailService = getEmailService();
          const telegramService = getTelegramService();
          const discordService = getDiscordService();

          await Promise.allSettled([
            emailService.sendSystemResetAlert(outputPriority),
            telegramService.sendSystemResetAlert(outputPriority),
            discordService.sendSystemResetAlert(outputPriority),
          ]);

          this.state.systemResetDetected = true;
          this.state.lastResetAlertTime = now;
        }
      } else {
        this.state.systemResetDetected = false;
        this.state.lastResetAlertTime = null;
      }

      this.state.lastKnownOutputPriority = outputPriority;
    } catch (error: any) {
      console.error('Error in system reset check:', error.message);
    }
  }

  /**
   * Check for load shedding (voltage drop)
   */
  async checkLoadShedding(gridVoltage: number): Promise<void> {
    try {
      const now = new Date();
      const isVoltageBelow = gridVoltage > 0 && gridVoltage < this.config.loadSheddingVoltageThreshold;

      if (isVoltageBelow) {
        const shouldSendAlert =
          !this.state.isLoadShedding ||
          !this.state.lastLoadSheddingAlertTime ||
          now.getTime() - this.state.lastLoadSheddingAlertTime.getTime() >= 5 * 60 * 60 * 1000; // 5 hours

        if (shouldSendAlert) {
          console.log(`⚡ Load shedding detected! Voltage: ${gridVoltage}V`);

          const emailService = getEmailService();
          const telegramService = getTelegramService();
          const discordService = getDiscordService();

          await Promise.allSettled([
            emailService.sendLoadSheddingAlert(gridVoltage),
            telegramService.sendLoadSheddingAlert(gridVoltage),
            discordService.sendLoadSheddingAlert(gridVoltage),
          ]);

          this.state.isLoadShedding = true;
          this.state.lastLoadSheddingAlertTime = now;
        }
      } else if (gridVoltage > this.config.loadSheddingVoltageThreshold) {
        if (this.state.isLoadShedding) {
          console.log(`✅ Grid power restored. Voltage: ${gridVoltage}V`);
        }
        this.state.isLoadShedding = false;
        this.state.lastLoadSheddingAlertTime = null;
      }
    } catch (error: any) {
      console.error('Error in load shedding check:', error.message);
    }
  }

  /**
   * Check grid feed status and send alerts
   */
  async checkGridFeed(gridFeedEnabled: boolean): Promise<void> {
    try {
      const now = new Date();
      
      // Check if status changed from enabled to disabled
      const wentFromOnToOff = this.state.previousGridFeedStatus && !gridFeedEnabled;
      
      if (wentFromOnToOff) {
        // Grid feeding just got disabled - send immediate alert
        console.log('⚠️ Grid feeding just got DISABLED - sending immediate alert!');

        const emailService = getEmailService();
        const telegramService = getTelegramService();
        const discordService = getDiscordService();

        await Promise.allSettled([
          emailService.sendGridFeedDisabledAlert(),
          telegramService.sendGridFeedDisabledAlert(),
          discordService.sendGridFeedDisabledAlert(),
        ]);

        this.state.lastGridFeedCheck = now;
      } else if (!gridFeedEnabled) {
        // Grid feeding still disabled - send periodic reminders
        const shouldSendReminder =
          !this.state.lastGridFeedCheck ||
          now.getTime() - this.state.lastGridFeedCheck.getTime() >=
            this.config.gridFeedAlertIntervalHours * 60 * 60 * 1000;

        if (shouldSendReminder) {
          console.log('⚠️ Grid feeding disabled - sending periodic reminder');

          const emailService = getEmailService();
          const telegramService = getTelegramService();
          const discordService = getDiscordService();

          await Promise.allSettled([
            emailService.sendGridFeedDisabledAlert(),
            telegramService.sendGridFeedDisabledAlert(),
            discordService.sendGridFeedDisabledAlert(),
          ]);

          this.state.lastGridFeedCheck = now;
        }
      } else {
        // Grid feeding is enabled - reset alerts
        this.state.lastGridFeedCheck = null;
      }

      // Update state
      this.state.previousGridFeedStatus = this.state.gridFeedingEnabled;
      this.state.gridFeedingEnabled = gridFeedEnabled;
      
      // Save to storage
      await settingsStorage.set('grid_feeding_enabled', gridFeedEnabled);
    } catch (error: any) {
      console.error('Error in grid feed check:', error.message);
    }
  }

  /**
   * Get daily statistics for a specific date
   */
  async getDailyStats(dateStr: string): Promise<DailySummaryData | null> {
    try {
      const api = await getWatchPowerAPI();
      const data = await api.getDailyData(dateStr);

      const rows = data?.dat?.row || [];
      let totalProductionWh = 0;
      let totalLoadWh = 0;
      let batteryModeHours = 0;
      let standbyModeHours = 0;
      const intervalHours = 5 / 60; // 5 minutes

      for (const rec of rows) {
        const fields = rec.field || [];
        if (fields.length < 22) continue;

        const timestamp = fields[1];
        if (!timestamp || !timestamp.startsWith(dateStr)) continue;

        const pvPower = fields[11] ? parseFloat(fields[11]) : 0.0;
        const loadPower = fields[21] ? parseFloat(fields[21]) : 0.0;
        const mode = (fields.length > 47 && fields[47]) ? String(fields[47]) : '';

        totalProductionWh += pvPower * intervalHours;
        totalLoadWh += loadPower * intervalHours;

        if (mode === 'Battery Mode') {
          batteryModeHours += intervalHours;
        } else if (mode === 'Standby Mode') {
          standbyModeHours += intervalHours;
        }
      }

      const expectedDataPoints = 288; // 24 * 60 / 5
      const actualDataPoints = rows.filter(
        (r) => r.field && r.field.length >= 22 && r.field[1] && r.field[1].startsWith(dateStr)
      ).length;
      const missingDataPoints = Math.max(0, expectedDataPoints - actualDataPoints);
      const missingDataHours = (missingDataPoints * 5) / 60;

      const productionKwh = Math.round((totalProductionWh / 1000) * 100) / 100;
      const loadKwh = Math.round((totalLoadWh / 1000) * 100) / 100;
      const gridContributionKwh = Math.round(((totalProductionWh - totalLoadWh) / 1000) * 100) / 100;

      const formatHours = (decimalHours: number): string => {
        const hrs = Math.floor(decimalHours);
        const mins = Math.round((decimalHours - hrs) * 60);
        return `${hrs} hr ${mins} min`;
      };

      const totalSystemOff = standbyModeHours + missingDataHours;

      return {
        date: dateStr,
        production_kwh: productionKwh,
        load_kwh: loadKwh,
        grid_contribution_kwh: gridContributionKwh,
        load_shedding_hours: formatHours(batteryModeHours),
        standby_hours: formatHours(standbyModeHours),
        missing_data_hours: formatHours(missingDataHours),
        system_off_hours: formatHours(totalSystemOff),
        timestamp: new Date().toLocaleString('en-US', { timeZone: 'Asia/Karachi' }) + ' PKT',
      };
    } catch (error: any) {
      console.error('Error fetching daily stats:', error.message);
      return null;
    }
  }

  /**
   * Send daily summary
   */
  async sendDailySummary(summary: DailySummaryData): Promise<void> {
    try {
      console.log(`📊 Sending daily summary for ${summary.date}`);

      const emailService = getEmailService();
      const telegramService = getTelegramService();
      const discordService = getDiscordService();

      await Promise.allSettled([
        emailService.sendDailySummary(summary),
        telegramService.sendDailySummary(summary),
        discordService.sendDailySummary(summary),
      ]);

      console.log('✅ Daily summary sent to all channels');
    } catch (error: any) {
      console.error('Error sending daily summary:', error.message);
    }
  }

  /**
   * Run all monitoring checks
   */
  async runAllChecks(): Promise<void> {
    try {
      console.log('⏰ Running monitoring checks...');

      // Fetch current system data
      const systemData = await this.getCurrentSystemData();
      
      if (systemData.success) {
        // Check for system reset
        if (systemData.outputPriority !== 'Unknown') {
          await this.checkSystemReset(systemData.outputPriority);
        }

        // Check for load shedding
        if (systemData.gridVoltage > 0) {
          await this.checkLoadShedding(systemData.gridVoltage);
        }

        // Check grid feed status
        const gridFeedEnabled = await this.getGridFeedStatus();
        await this.checkGridFeed(gridFeedEnabled);
      }

      // Always check for system offline (even if API call failed)
      await this.checkSystemOffline();

      console.log('✅ Monitoring checks completed');
    } catch (error: any) {
      console.error('Error in monitoring checks:', error.message);
    }
  }

  /**
   * Get current grid feed status from system settings
   */
  async getGridFeedStatus(): Promise<boolean> {
    try {
      const api = await getWatchPowerAPI();
      const data = await api.getDeviceLastData();

      if (!data.dat || !Array.isArray(data.dat) || data.dat.length === 0) {
        // No data available, return saved status
        return await settingsStorage.get('grid_feeding_enabled', true);
      }

      // Convert title/val array to object
      const deviceData: any = {};
      data.dat.forEach((item: any) => {
        if (item.title && item.val !== undefined) {
          deviceData[item.title] = item.val;
        }
      });

      const solarFeedPower = parseFloat(deviceData['Solar Feed To Grid Power'] || '0');
      const pv1Power = parseFloat(deviceData['PV1 Charging Power'] || '0');
      const pv2Power = parseFloat(deviceData['PV2 Charging Power'] || '0');
      const pvPower = pv1Power + (isNaN(pv2Power) ? 0 : pv2Power);

      const now = new Date();
      const currentHour = now.getHours();
      const isDaytime = currentHour >= 7 && currentHour <= 17;
      const isProducing = pvPower > 500;
      const isFeeding = solarFeedPower >= 50;

      let gridFeedEnabled: boolean;

      if (isDaytime && isProducing) {
        gridFeedEnabled = isFeeding;
      } else {
        const savedGridStatus = await settingsStorage.get('grid_feeding_enabled', true);
        if (isFeeding) {
          gridFeedEnabled = true;
        } else if (savedGridStatus === false) {
          gridFeedEnabled = false;
        } else {
          gridFeedEnabled = true;
        }
      }

      return gridFeedEnabled;
    } catch (error: any) {
      console.error('Error getting grid feed status:', error.message);
      return await settingsStorage.get('grid_feeding_enabled', true);
    }
  }
}

// Singleton instance
let monitoringService: MonitoringService | null = null;

export function getMonitoringService(): MonitoringService {
  if (!monitoringService) {
    monitoringService = new MonitoringService();
  }
  return monitoringService;
}

