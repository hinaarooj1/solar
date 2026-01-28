import { NextRequest, NextResponse } from 'next/server';
import { getWatchPowerAPI } from '@/lib/watchpower-api';

export async function GET(request: NextRequest) {
  try {
    const api = await getWatchPowerAPI();
    const data = await api.getDeviceLastData();
    
    return NextResponse.json({ success: true, data });
  } catch (error: any) {
    console.error('Error in /api/last-data:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}





