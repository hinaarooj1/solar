import { NextRequest, NextResponse } from 'next/server';
import settingsStorage from '@/lib/settings-storage';

interface GridFeedControl {
  enabled: boolean;
}

export async function POST(request: NextRequest) {
  try {
    const body: GridFeedControl = await request.json();
    
    // Update settings storage (same as Python backend)
    await settingsStorage.set("grid_feeding_enabled", body.enabled);
    
    // TODO: Implement actual API call to control grid feeding
    // This would require reverse engineering the WatchPower control protocol
    
    const response = {
      success: true,
      message: `Grid feeding ${body.enabled ? 'enabled' : 'disabled'}`,
      grid_feed_enabled: body.enabled,
      saved: true,
      note: "Setting saved. Email reminders will be sent if disabled. Use WatchPower app for actual hardware control."
    };
    
    return NextResponse.json(response);
  } catch (error: any) {
    console.error('Error in /api/control/grid-feed:', error.message);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}
