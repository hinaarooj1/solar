import { NextRequest, NextResponse } from 'next/server';
import { getTelegramService } from '@/lib/telegram-service';

export async function GET(request: NextRequest) {
  try {
    const telegramService = getTelegramService();
    const success = await telegramService.sendTestMessage();
    
    if (success) {
      return NextResponse.json({
        success: true,
        message: "Test Telegram message sent successfully",
        recipient: process.env.TELEGRAM_CHAT_ID
      });
    } else {
      return NextResponse.json({
        success: false,
        message: "Failed to send Telegram - check configuration"
      });
    }
  } catch (error: any) {
    console.error('Error in /api/notifications/test-telegram:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  return GET(request);
}










