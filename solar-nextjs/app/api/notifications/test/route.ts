import { NextRequest, NextResponse } from 'next/server';
import { getEmailService } from '@/lib/email-service';
import { getTelegramService } from '@/lib/telegram-service';
import { getDiscordService } from '@/lib/discord-service';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const emailService = getEmailService();
    const telegramService = getTelegramService();
    const discordService = getDiscordService();

    const results = await Promise.allSettled([
      emailService.sendTestEmail(),
      telegramService.sendTestMessage(),
      discordService.sendTestMessage(),
    ]);

    const emailSuccess = results[0].status === 'fulfilled' && results[0].value;
    const telegramSuccess = results[1].status === 'fulfilled' && results[1].value;
    const discordSuccess = results[2].status === 'fulfilled' && results[2].value;

    return NextResponse.json({
      success: true,
      message: 'Test notifications sent',
      results: {
        email: emailSuccess,
        telegram: telegramSuccess,
        discord: discordSuccess,
      },
    });
  } catch (error: any) {
    console.error('Error sending test notifications:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  return POST(request);
}

