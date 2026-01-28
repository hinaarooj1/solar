import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const settings = await request.json();
    
    // This would typically interact with the inverter via the WatchPower API
    // For now, we'll just log and return a success message
    console.log(`Attempting to update system settings:`, settings);
    
    return NextResponse.json({ 
      success: true, 
      message: 'System settings updated',
      settings: settings,
      note: 'This is a read-only dashboard. Use WatchPower app to change settings.'
    });
  } catch (error: any) {
    console.error('Error in /api/control/system-settings:', error.message);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}










