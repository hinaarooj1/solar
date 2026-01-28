import { NextRequest, NextResponse } from 'next/server';
import { getWatchPowerAPI } from '@/lib/watchpower-api';

export async function GET(request: NextRequest) {
  try {
    const api = await getWatchPowerAPI();
    const devices = await api.getDevices();
    
    return NextResponse.json({ success: true, devices });
  } catch (error: any) {
    console.error('Error in /api/devices:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
