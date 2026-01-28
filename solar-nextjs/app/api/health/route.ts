import { NextRequest, NextResponse } from 'next/server';
import { getMonitoringService } from '@/lib/monitoring-service';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const monitoringService = getMonitoringService();
    const systemData = await monitoringService.getCurrentSystemData();

    const healthScore = systemData.gridVoltage > 180 ? 95 : 75;
    const status = healthScore >= 90 ? 'Online' : 'Warning';

    return NextResponse.json({
      success: true,
      status,
      health_score: healthScore,
      utility_ac_voltage: systemData.gridVoltage,
      output_source_priority: systemData.outputPriority,
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error('Error in /api/health:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

