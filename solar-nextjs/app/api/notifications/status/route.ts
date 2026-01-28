import { NextRequest, NextResponse } from 'next/server';
import { getEmailService } from '@/lib/email-service';
import { getTelegramService } from '@/lib/telegram-service';
import { getDiscordService } from '@/lib/discord-service';
import { getMonitoringService } from '@/lib/monitoring-service';

export async function GET(request: NextRequest) {
  try {
    const emailService = getEmailService();
    const telegramService = getTelegramService();
    const discordService = getDiscordService();
    const monitoringService = getMonitoringService();
    
    const response = {
      success: true,
      email_configured: !!(process.env.EMAIL_USER && process.env.EMAIL_PASSWORD),
      sender_email: process.env.EMAIL_USER || 'Not configured',
      recipient_email: process.env.ALERT_EMAIL || 'Not configured',
      smtp_server: process.env.EMAIL_HOST || 'smtp.gmail.com',
      smtp_port: parseInt(process.env.EMAIL_PORT || '587'),
      telegram_configured: !!(process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID),
      telegram_chat_id: process.env.TELEGRAM_CHAT_ID || 'Not configured',
      discord_configured: !!process.env.DISCORD_WEBHOOK_URL,
      discord_webhook: process.env.DISCORD_WEBHOOK_URL ? 'Configured' : 'Not configured',
      monitoring_active: true, // Always true in Next.js context
      grid_feeding_enabled: true, // Default value
      is_load_shedding: false, // Default value
      last_data_timestamp: new Date().toISOString()
    };
    
    return NextResponse.json(response);
  } catch (error: any) {
    console.error('Error in /api/notifications/status:', error.message);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}










