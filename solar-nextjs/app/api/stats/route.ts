import { NextRequest, NextResponse } from 'next/server';
import { getWatchPowerAPI } from '@/lib/watchpower-api';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const date = searchParams.get('date') || new Date().toISOString().split('T')[0];

    const api = await getWatchPowerAPI();
    const data = await api.getDailyData(date);

    const rows = data?.dat?.row || [];
    const graph: any[] = [];
    let totalProductionWh = 0;
    let totalLoadWh = 0;

    for (const rec of rows) {
      const fields = rec.field || [];
      if (fields.length < 22) continue;

      const timestamp = fields[1];
      if (!timestamp || !timestamp.startsWith(date)) continue;

      const pvPower = fields[11] ? parseFloat(fields[11]) : 0.0;
      const loadPower = fields[21] ? parseFloat(fields[21]) : 0.0;
      const mode = (fields.length > 47 && fields[47]) ? String(fields[47]) : 'Unknown';

      graph.push({
        time: timestamp.slice(-8), // HH:MM:SS
        pv_power: pvPower,
        load_power: loadPower,
        mode: mode,
      });

      // 5 min interval = 5/60 hours
      totalProductionWh += pvPower * (5 / 60);
      totalLoadWh += loadPower * (5 / 60);
    }

    return NextResponse.json({
      success: true,
      date,
      total_production_kwh: Math.round((totalProductionWh / 1000) * 1000) / 1000,
      total_load_kwh: Math.round((totalLoadWh / 1000) * 1000) / 1000,
      graph,
    });
  } catch (error: any) {
    console.error('Error in /api/stats:', error);
    console.error('Error message:', error.message);
    console.error('Error stack:', error.stack);
    return NextResponse.json(
      { success: false, error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}

