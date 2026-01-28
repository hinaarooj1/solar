import { NextResponse } from 'next/server';

// Default alert configuration
const DEFAULT_ALERTS_CONFIG = {
  grid_feed_alert_interval_hours: parseInt(process.env.GRID_FEED_ALERT_INTERVAL_HOURS || '1'),
  load_shedding_voltage_threshold: parseInt(process.env.LOAD_SHEDDING_VOLTAGE_THRESHOLD || '180'),
  system_offline_threshold_minutes: parseInt(process.env.SYSTEM_OFFLINE_THRESHOLD_MINUTES || '10'),
  low_production_threshold_watts: parseInt(process.env.LOW_PRODUCTION_THRESHOLD_WATTS || '500'),
  low_production_check_start: process.env.LOW_PRODUCTION_CHECK_START || '11:00',
  low_production_check_end: process.env.LOW_PRODUCTION_CHECK_END || '15:00',
};

export async function GET() {
  try {
    return NextResponse.json({ 
      success: true, 
      config: DEFAULT_ALERTS_CONFIG 
    });
  } catch (error: any) {
    console.error('Error in /api/alerts/config:', error.message);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const newConfig = await request.json();
    
    // In a real implementation, you would save this to a database or file
    // For now, we'll just return the updated config
    console.log('Alert configuration updated:', newConfig);
    
    return NextResponse.json({ 
      success: true, 
      message: 'Alert configuration updated',
      config: { ...DEFAULT_ALERTS_CONFIG, ...newConfig }
    });
  } catch (error: any) {
    console.error('Error in /api/alerts/config:', error.message);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}










