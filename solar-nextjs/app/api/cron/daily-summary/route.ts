import { NextRequest, NextResponse } from 'next/server';
import { getMonitoringService } from '@/lib/monitoring-service';

export const dynamic = 'force-dynamic';

/**
 * Vercel Cron Job - Runs daily at 7 PM UTC (midnight PKT)
 * Sends daily summary report for yesterday
 */
export async function GET(request: NextRequest) {
  try {
    // Verify this request is from Vercel Cron
    const authHeader = request.headers.get('authorization');
    const cronSecret = process.env.CRON_SECRET;

    if (authHeader !== `Bearer ${cronSecret}`) {
      console.error('❌ Unauthorized cron request');
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    console.log('🌙 Cron: Running daily summary...');

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
    const dateStr = `${year}-${month}-${day}`;

    console.log(`📊 Fetching daily summary for ${dateStr} (PKT timezone)...`);
    console.log(`🕐 Current PKT time: ${pktTime.toISOString()}`);

    const summary = await monitoringService.getDailyStats(dateStr);

    if (!summary) {
      console.error(`❌ Failed to fetch daily stats for ${dateStr}`);
      return NextResponse.json(
        {
          success: false,
          message: `Failed to fetch daily stats for ${dateStr}`,
          date: dateStr,
        },
        { status: 500 }
      );
    }

    await monitoringService.sendDailySummary(summary);

    console.log(`✅ Cron: Daily summary sent for ${dateStr}`);

    return NextResponse.json({
      success: true,
      message: 'Daily summary sent successfully',
      date: dateStr,
      summary,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error('❌ Cron daily summary error:', error.message);
    return NextResponse.json(
      {
        success: false,
        error: error.message,
        timestamp: new Date().toISOString(),
      },
      { status: 500 }
    );
  }
}

