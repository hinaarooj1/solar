import nodemailer from 'nodemailer';

export interface EmailConfig {
  user: string;
  password: string;
  recipient: string;
  host: string;
  port: number;
}

export interface DailySummaryData {
  date: string;
  production_kwh: number;
  load_kwh: number;
  grid_contribution_kwh: number;
  load_shedding_hours: string;
  system_off_hours: string;
  standby_hours: string;
  missing_data_hours: string;
  timestamp: string;
}

export class EmailService {
  private transporter: nodemailer.Transporter | null = null;
  private config: EmailConfig;

  constructor(config: EmailConfig) {
    this.config = config;
    
    if (config.user && config.password && config.recipient) {
      this.transporter = nodemailer.createTransport({
        host: config.host,
        port: config.port,
        secure: false,
        auth: {
          user: config.user,
          pass: config.password,
        },
      });
      console.log('✅ Email service initialized');
    } else {
      console.warn('⚠️ Email service not configured');
    }
  }

  async sendEmail(subject: string, body: string): Promise<boolean> {
    if (!this.transporter) {
      console.error('❌ Email not configured');
      return false;
    }

    try {
      await this.transporter.sendMail({
        from: this.config.user,
        to: this.config.recipient,
        subject,
        text: body,
      });

      console.log(`✅ Email sent: ${subject}`);
      return true;
    } catch (error: any) {
      console.error(`❌ Failed to send email: ${error.message}`);
      return false;
    }
  }

  async sendSystemResetAlert(outputPriority: string): Promise<boolean> {
    const subject = '🚨 CRITICAL: Inverter Settings Reset Detected!';
    const body = `
CRITICAL: Inverter Reset Detected!

Inverter Settings Have Been Reset ⚠️

This typically happens after a power cut or PV surge.

📋 Detected Changes:
• Output Priority changed to '${outputPriority}' (expected: 'Solar Utility Bat')

💡 Action Required:
1. Open WatchPower app immediately
2. Restore your preferred settings:
   - Set Output Priority back to 'Solar Utility Bat'
   - Disable LCD Auto Return if enabled
   - Enable Grid Feeding if it was disabled

⚠️ Note: System may not be operating optimally until settings are restored!

━━━━━━━━━━━━━━━━━━
Solar Dashboard - System Reset Alert
    `.trim();

    return this.sendEmail(subject, body);
  }

  async sendLoadSheddingAlert(voltage: number): Promise<boolean> {
    const subject = '⚡ ALERT: Load Shedding Detected!';
    const body = `
Load Shedding Alert!

⚡ Grid Power Lost ⚡

Current Grid Voltage: ${voltage}V (Below threshold)

Your solar system has switched to battery/solar mode.

System Status:
• Grid: Disconnected
• Running on: Battery + Solar
• Time: ${new Date().toLocaleString()}

The system will automatically switch back when grid power is restored.

━━━━━━━━━━━━━━━━━━
Solar Dashboard - Load Shedding Alert
    `.trim();

    return this.sendEmail(subject, body);
  }

  async sendGridFeedDisabledAlert(): Promise<boolean> {
    const subject = '🔌 URGENT: Solar Grid Feeding DISABLED';
    const body = `
URGENT: Grid Feeding Disabled!

Your solar system is NO LONGER feeding excess power back to the grid.

This means:
❌ Lost revenue opportunity
❌ Excess power is being wasted
❌ Not maximizing your solar ROI

💡 Action Required:
Open the WatchPower app and enable "Grid Feeding" immediately.

You'll receive reminders every hour until this is fixed.

━━━━━━━━━━━━━━━━━━
Solar Dashboard - Grid Feed Alert
    `.trim();

    return this.sendEmail(subject, body);
  }

  async sendDailySummary(summary: DailySummaryData): Promise<boolean> {
    const subject = `📊 Daily Solar Summary - ${summary.date}`;
    const body = `
Daily Solar Summary for ${summary.date}

☀️ SOLAR PRODUCTION
━━━━━━━━━━━━━━━━━━━━━━━━
Total Production: ${summary.production_kwh} kWh

⚡ ENERGY USAGE
━━━━━━━━━━━━━━━━━━━━━━━━
Total Consumption: ${summary.load_kwh} kWh

🔋 GRID CONTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━
Energy Fed to Grid: ${summary.grid_contribution_kwh} kWh

🔌 LOAD SHEDDING
━━━━━━━━━━━━━━━━━━━━━━━━
Battery/Solar Runtime: ${summary.load_shedding_hours}

⏸️ SYSTEM OFF TIME
━━━━━━━━━━━━━━━━━━━━━━━━
Total Off Duration: ${summary.system_off_hours}
  • Standby Mode: ${summary.standby_hours}
  • Missing Data: ${summary.missing_data_hours}

━━━━━━━━━━━━━━━━━━━━━━━━
Solar Dashboard - Daily Summary
Generated at ${summary.timestamp}
    `.trim();

    return this.sendEmail(subject, body);
  }

  async sendSystemShutdownAlert(lastSeenMinutes: number): Promise<boolean> {
    const subject = "🚨 CRITICAL: Solar System Offline";
    const body = `
CRITICAL: System Offline

Solar System: NOT RESPONDING ❌

⏱️ Last seen: ${lastSeenMinutes} minutes ago

🔧 Check immediately:
• Inverter power status
• WiFi/network connection
• Error codes on display
• System breakers/fuses

━━━━━━━━━━━━━━━━━━
Solar Dashboard - Critical Alert
    `.trim();
    
    return this.sendEmail(subject, body);
  }

  async sendLowProductionAlert(currentProduction: number, expectedMin: number, timeRange: string): Promise<boolean> {
    const subject = "⚠️ Solar System - Low Production Warning";
    const body = `
Solar System Warning

Low Production During Peak Hours

📊 Current Production: ${currentProduction}W
📊 Expected Minimum: ${expectedMin}W
⏰ Time Range: ${timeRange}

🔧 Possible causes:
• Panel shading or obstruction
• Dust/dirt on panels
• System malfunction

💡 Recommended Action:
Check panels and system status

━━━━━━━━━━━━━━━━━━
Solar Dashboard - Production Alert
    `.trim();
    
    return this.sendEmail(subject, body);
  }

  async sendTestEmail(): Promise<boolean> {
    const subject = '✅ Solar Dashboard Connected!';
    const body = `
Solar Dashboard Connected!

Your email notifications are now active! 🎉

You'll receive instant alerts for:
🔌 Grid feeding status changes
⚡ Load shedding detection
🚨 System offline warnings
☀️ Low production alerts
🔄 System reset detection

Reminder Interval: Every 1 hour ⏰

━━━━━━━━━━━━━━━━━━
Test Email - Solar Dashboard
    `.trim();

    return this.sendEmail(subject, body);
  }
}

// Singleton instance
let emailService: EmailService | null = null;

export function getEmailService(): EmailService {
  if (!emailService) {
    const config: EmailConfig = {
      user: process.env.EMAIL_USER || '',
      password: process.env.EMAIL_PASSWORD || '',
      recipient: process.env.ALERT_EMAIL || '',
      host: process.env.EMAIL_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.EMAIL_PORT || '587'),
    };

    emailService = new EmailService(config);
  }

  return emailService;
}

