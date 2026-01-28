import axios from 'axios';
import { DailySummaryData } from './email-service';

export interface DiscordConfig {
  webhookUrl: string;
}

interface DiscordEmbed {
  title: string;
  description: string;
  color: number;
  fields?: Array<{
    name: string;
    value: string;
    inline?: boolean;
  }>;
  footer?: {
    text: string;
  };
}

export class DiscordService {
  private webhookUrl: string;

  constructor(config: DiscordConfig) {
    this.webhookUrl = config.webhookUrl;

    if (config.webhookUrl) {
      console.log('✅ Discord service initialized');
    } else {
      console.warn('⚠️ Discord service not configured');
    }
  }

  async sendMessage(content: string | null, embed?: DiscordEmbed): Promise<boolean> {
    if (!this.webhookUrl) {
      console.error('❌ Discord not configured');
      return false;
    }

    try {
      const payload: any = {};
      if (content) payload.content = content;
      if (embed) payload.embeds = [embed];

      await axios.post(this.webhookUrl, payload);

      console.log('✅ Discord message sent');
      return true;
    } catch (error: any) {
      console.error(`❌ Failed to send Discord: ${error.message}`);
      return false;
    }
  }

  async sendSystemResetAlert(outputPriority: string): Promise<boolean> {
    const embed: DiscordEmbed = {
      title: '🚨 CRITICAL: Inverter Reset Detected!',
      description: '**Inverter Settings Have Been Reset** ⚠️\n\nThis typically happens after a power cut or PV surge.',
      color: 15158332, // Red
      fields: [
        {
          name: '📋 Detected Changes',
          value: `• Output Priority changed to '${outputPriority}' (expected: 'Solar Utility Bat')`,
          inline: false,
        },
        {
          name: '💡 Action Required',
          value: '1. Open WatchPower app immediately\n2. Restore your preferred settings:\n   - Set Output Priority back to \'Solar Utility Bat\'\n   - Disable LCD Auto Return if enabled\n   - Enable Grid Feeding if it was disabled',
          inline: false,
        },
        {
          name: '⚠️ Note',
          value: 'System may not be operating optimally until settings are restored!',
          inline: false,
        },
      ],
      footer: {
        text: 'Solar Dashboard - System Reset Alert',
      },
    };

    return this.sendMessage(null, embed);
  }

  async sendLoadSheddingAlert(voltage: number): Promise<boolean> {
    const embed: DiscordEmbed = {
      title: '⚡ ALERT: Load Shedding Detected!',
      description: '**Grid Power Lost** ⚡',
      color: 16750848, // Orange
      fields: [
        {
          name: '⚡ Current Grid Voltage',
          value: `**${voltage}V** (Below threshold)`,
          inline: true,
        },
        {
          name: '🔋 System Status',
          value: 'Running on Battery + Solar',
          inline: true,
        },
        {
          name: 'ℹ️ Information',
          value: 'The system will automatically switch back when grid power is restored.',
          inline: false,
        },
      ],
      footer: {
        text: 'Solar Dashboard - Load Shedding Alert',
      },
    };

    return this.sendMessage(null, embed);
  }

  async sendGridFeedDisabledAlert(): Promise<boolean> {
    const embed: DiscordEmbed = {
      title: '🔌 URGENT: Grid Feeding DISABLED',
      description: 'Your solar system is **NO LONGER** feeding excess power back to the grid.',
      color: 16750848, // Orange
      fields: [
        {
          name: '❌ This means',
          value: '• Lost revenue opportunity\n• Excess power is being wasted\n• Not maximizing your solar ROI',
          inline: false,
        },
        {
          name: '💡 Action Required',
          value: 'Open the WatchPower app and enable "Grid Feeding" immediately.',
          inline: false,
        },
      ],
      footer: {
        text: 'Solar Dashboard - Grid Feed Alert',
      },
    };

    return this.sendMessage(null, embed);
  }

  async sendGridFeedReminder(): Promise<boolean> {
    const embed: DiscordEmbed = {
      title: "⚠️ Solar System Reminder",
      description: "**Grid Feeding: STILL DISABLED**\n\nYour system is not feeding power to the grid.",
      color: 16753920, // Orange color
      fields: [
        {
          name: "💡 Recommended Action",
          value: "Enable grid feeding in WatchPower app to maximize ROI.",
          inline: false
        }
      ],
      footer: {
        text: "Hourly Reminder - Solar Dashboard"
      }
    };
    
    return this.sendMessage(null, embed);
  }

  async sendSystemOfflineAlert(minutes: number): Promise<boolean> {
    const embed: DiscordEmbed = {
      title: "🚨 CRITICAL: System Offline",
      description: "**Solar System: NOT RESPONDING** ❌",
      color: 10038562, // Dark red color
      fields: [
        {
          name: "⏱️ Last Seen",
          value: `${minutes} minutes ago`,
          inline: true
        },
        {
          name: "🔧 Check immediately",
          value: "• Inverter power status\n• WiFi/network connection\n• Error codes on display\n• System breakers/fuses",
          inline: false
        }
      ],
      footer: {
        text: "Solar Dashboard - Critical Alert"
      }
    };
    
    return this.sendMessage(null, embed);
  }

  async sendDailySummary(summary: DailySummaryData): Promise<boolean> {
    const embed: DiscordEmbed = {
      title: `📊 Daily Solar Summary - ${summary.date}`,
      description: 'Your daily solar system performance report',
      color: 3447003, // Blue
      fields: [
        {
          name: '☀️ Solar Production',
          value: `**${summary.production_kwh} kWh**`,
          inline: true,
        },
        {
          name: '⚡ Energy Usage',
          value: `**${summary.load_kwh} kWh**`,
          inline: true,
        },
        {
          name: '🔋 Grid Contribution',
          value: `**${summary.grid_contribution_kwh} kWh**`,
          inline: true,
        },
        {
          name: '🔌 Load Shedding',
          value: `Battery/Solar Runtime: **${summary.load_shedding_hours}**`,
          inline: false,
        },
        {
          name: '⏸️ System Off Time',
          value: `Total: **${summary.system_off_hours}**\n• Standby Mode: ${summary.standby_hours}\n• Missing Data: ${summary.missing_data_hours}`,
          inline: false,
        },
      ],
      footer: {
        text: `Solar Dashboard - Generated at ${summary.timestamp}`,
      },
    };

    return this.sendMessage(null, embed);
  }

  async sendTestMessage(): Promise<boolean> {
    const embed: DiscordEmbed = {
      title: '✅ Solar Dashboard Connected!',
      description: 'Your Discord notifications are now active! 🎉',
      color: 5763719, // Green
      fields: [
        {
          name: "You'll receive instant alerts for:",
          value: '🔌 Grid feeding status changes\n⚡ Load shedding detection\n🚨 System offline warnings\n☀️ Low production alerts\n🔄 System reset detection',
          inline: false,
        },
        {
          name: 'Reminder Interval',
          value: 'Every 1 hour ⏰',
          inline: false,
        },
      ],
      footer: {
        text: 'Test Message - Solar Dashboard',
      },
    };

    return this.sendMessage(null, embed);
  }
}

// Singleton instance
let discordService: DiscordService | null = null;

export function getDiscordService(): DiscordService {
  if (!discordService) {
    const config: DiscordConfig = {
      webhookUrl: process.env.DISCORD_WEBHOOK_URL || '',
    };

    discordService = new DiscordService(config);
  }

  return discordService;
}

