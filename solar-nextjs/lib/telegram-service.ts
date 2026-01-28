import axios from 'axios';
import { DailySummaryData } from './email-service';

export interface TelegramConfig {
  botToken: string;
  chatId: string;
}

export class TelegramService {
  private botToken: string;
  private chatId: string;
  private apiUrl: string;

  constructor(config: TelegramConfig) {
    this.botToken = config.botToken;
    this.chatId = config.chatId;
    this.apiUrl = `https://api.telegram.org/bot${this.botToken}`;

    if (config.botToken && config.chatId) {
      console.log('✅ Telegram service initialized');
    } else {
      console.warn('⚠️ Telegram service not configured');
    }
  }

  async sendMessage(message: string): Promise<boolean> {
    if (!this.botToken || !this.chatId) {
      console.error('❌ Telegram not configured');
      return false;
    }

    try {
      await axios.post(`${this.apiUrl}/sendMessage`, {
        chat_id: this.chatId,
        text: message,
        parse_mode: 'Markdown',
      });

      console.log('✅ Telegram message sent');
      return true;
    } catch (error: any) {
      console.error(`❌ Failed to send Telegram: ${error.message}`);
      return false;
    }
  }

  async sendSystemResetAlert(outputPriority: string): Promise<boolean> {
    const message = `
🚨 *CRITICAL: Inverter Reset Detected!*

*Inverter Settings Have Been Reset* ⚠️

This typically happens after a power cut or PV surge.

📋 *Detected Changes:*
• Output Priority changed to '${outputPriority}' (expected: 'Solar Utility Bat')

💡 *Action Required:*
1. Open WatchPower app immediately
2. Restore your preferred settings:
   - Set Output Priority back to 'Solar Utility Bat'
   - Disable LCD Auto Return if enabled
   - Enable Grid Feeding if it was disabled

⚠️ *Note:* System may not be operating optimally until settings are restored!

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - System Reset Alert
    `.trim();

    return this.sendMessage(message);
  }

  async sendLoadSheddingAlert(voltage: number): Promise<boolean> {
    const message = `
⚡ *ALERT: Load Shedding Detected!*

*Grid Power Lost* ⚡

Current Grid Voltage: *${voltage}V* (Below threshold)

Your solar system has switched to battery/solar mode.

*System Status:*
• Grid: Disconnected
• Running on: Battery + Solar
• Time: ${new Date().toLocaleString()}

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Load Shedding Alert
    `.trim();

    return this.sendMessage(message);
  }

  async sendGridFeedDisabledAlert(): Promise<boolean> {
    const message = `
🔌 *URGENT: Grid Feeding DISABLED*

Your solar system is *NO LONGER* feeding excess power back to the grid.

*This means:*
❌ Lost revenue opportunity
❌ Excess power is being wasted
❌ Not maximizing your solar ROI

💡 *Action Required:*
Open the WatchPower app and enable "Grid Feeding" immediately.

You'll receive reminders every hour until this is fixed.

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Grid Feed Alert
    `.trim();

    return this.sendMessage(message);
  }

  async sendSystemOfflineAlert(minutes: number): Promise<boolean> {
    const message = `
🚨 *CRITICAL: System Offline*

*Solar System: NOT RESPONDING* ❌

⏱️ Last seen: ${minutes} minutes ago

🔧 *Check immediately:*
• Inverter power status
• WiFi/network connection
• Error codes on display
• System breakers/fuses

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Critical Alert
    `.trim();
    
    return this.sendMessage(message);
  }

  async sendDailySummary(summary: DailySummaryData): Promise<boolean> {
    const message = `
📊 *Daily Solar Summary - ${summary.date}*

☀️ *SOLAR PRODUCTION*
━━━━━━━━━━━━━━━━━━━━━━━━
Total Production: *${summary.production_kwh} kWh*

⚡ *ENERGY USAGE*
━━━━━━━━━━━━━━━━━━━━━━━━
Total Consumption: *${summary.load_kwh} kWh*

🔋 *GRID CONTRIBUTION*
━━━━━━━━━━━━━━━━━━━━━━━━
Energy Fed to Grid: *${summary.grid_contribution_kwh} kWh*

🔌 *LOAD SHEDDING*
━━━━━━━━━━━━━━━━━━━━━━━━
Battery/Solar Runtime: *${summary.load_shedding_hours}*

⏸️ *SYSTEM OFF TIME*
━━━━━━━━━━━━━━━━━━━━━━━━
Total: *${summary.system_off_hours}*
  • Standby Mode: ${summary.standby_hours}
  • Missing Data: ${summary.missing_data_hours}

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Daily Summary
Generated at ${summary.timestamp}
    `.trim();

    return this.sendMessage(message);
  }

  async sendTestMessage(): Promise<boolean> {
    const message = `
✅ *Solar Dashboard Connected!*

Your Telegram notifications are now active! 🎉

You'll receive instant alerts for:
🔌 Grid feeding status changes
⚡ Load shedding detection
🚨 System offline warnings
☀️ Low production alerts
🔄 System reset detection

Reminder Interval: Every 1 hour ⏰

━━━━━━━━━━━━━━━━━━
🤖 Test Message - Solar Dashboard
    `.trim();

    return this.sendMessage(message);
  }
}

// Singleton instance
let telegramService: TelegramService | null = null;

export function getTelegramService(): TelegramService {
  if (!telegramService) {
    const config: TelegramConfig = {
      botToken: process.env.TELEGRAM_BOT_TOKEN || '',
      chatId: process.env.TELEGRAM_CHAT_ID || '',
    };

    telegramService = new TelegramService(config);
  }

  return telegramService;
}

