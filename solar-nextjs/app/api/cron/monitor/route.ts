import { NextRequest, NextResponse } from 'next/server';
import { getMonitoringService } from '@/lib/monitoring-service';

export const dynamic = 'force-dynamic';

/**
 * Vercel Cron Job - Runs every 5 minutes
 * Monitors system for alerts
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

    console.log('🔄 Cron: Running monitoring checks...');

    const monitoringService = getMonitoringService();
    await monitoringService.runAllChecks();

    console.log('✅ Cron: Monitoring checks completed');

    return NextResponse.json({
      success: true,
      message: 'Monitoring checks completed',
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error('❌ Cron monitoring error:', error.message);
    console.error('Stack trace:', error.stack);
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

