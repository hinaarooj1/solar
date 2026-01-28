import { NextRequest, NextResponse } from 'next/server';
import { getDiscordService } from '@/lib/discord-service';

export async function GET(request: NextRequest) {
  try {
    const discordService = getDiscordService();
    const success = await discordService.sendTestMessage();
    
    if (success) {
      return NextResponse.json({
        success: true,
        message: "Test Discord message sent successfully",
        webhook: "Configured"
      });
    } else {
      return NextResponse.json({
        success: false,
        message: "Failed to send Discord - check webhook configuration"
      });
    }
  } catch (error: any) {
    console.error('Error in /api/notifications/test-discord:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  return GET(request);
}










