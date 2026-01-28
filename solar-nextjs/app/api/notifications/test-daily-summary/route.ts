import { NextRequest, NextResponse } from 'next/server';
import { getMonitoringService } from '@/lib/monitoring-service';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const monitoringService = getMonitoringService();

    // Get yesterday's date in PKT timezone
    const now = new Date();
    
    // Convert to PKT (UTC+5)
    const pktOffset = 5 * 60; // PKT is UTC+5
    const localOffset = now.getTimezoneOffset(); // Get local offset in minutes
    const pktTime = new Date(now.getTime() + (pktOffset + localOffset) * 60 * 1000);
    
    // Get yesterday in PKT
    const yesterday = new Date(pktTime);
    yesterday.setDate(yesterday.getDate() - 1);
    
    // Format as YYYY-MM-DD
    const year = yesterday.getFullYear();
    const month = String(yesterday.getMonth() + 1).padStart(2, '0');
    const day = String(yesterday.getDate()).padStart(2, '0');
    const yesterdayStr = `${year}-${month}-${day}`;

    console.log(`📊 Testing daily summary for ${yesterdayStr} (PKT timezone)...`);
    console.log(`🕐 Current PKT time: ${pktTime.toISOString()}`);

    const summary = await monitoringService.getDailyStats(yesterdayStr);

    if (!summary) {
      return NextResponse.json(
        {
          success: false,
          message: `Failed to fetch daily stats for ${yesterdayStr}`,
          date: yesterdayStr,
        },
        { status: 500 }
      );
    }

    await monitoringService.sendDailySummary(summary);

    return NextResponse.json({
      success: true,
      message: 'Daily summary sent to all channels',
      date: yesterdayStr,
      data: summary,
      channels: ['email', 'telegram', 'discord'],
    });
  } catch (error: any) {
    console.error('Error in test daily summary:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

