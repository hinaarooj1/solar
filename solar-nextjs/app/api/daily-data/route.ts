import { NextRequest, NextResponse } from 'next/server';
import { getWatchPowerAPI } from '@/lib/watchpower-api';

export async function GET(request: NextRequest) {
  try {
    const api = await getWatchPowerAPI();
    const today = new Date().toISOString().split('T')[0];
    const data = await api.getDailyData(today);
    
    return NextResponse.json({ success: true, data });
  } catch (error: any) {
    console.error('Error in /api/daily-data:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
