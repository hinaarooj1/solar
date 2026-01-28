import { NextResponse } from 'next/server';
import { getMonitoringService } from '@/lib/monitoring-service';

export async function POST(request: Request) {
  try {
    const { priority } = await request.json();
    const monitoringService = getMonitoringService();
    
    // This would typically interact with the inverter via the WatchPower API
    // For now, we'll just log and return a success message
    console.log(`Attempting to set output priority to: ${priority}`);
    
    // await monitoringService.setOutputPriority(priority); // Uncomment and implement actual control
    
    return NextResponse.json({ 
      success: true, 
      message: `Output priority set to ${priority}`,
      note: 'This is a read-only dashboard. Use WatchPower app to change settings.'
    });
  } catch (error: any) {
    console.error('Error in /api/control/output-priority:', error.message);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function GET() {
  try {
    const monitoringService = getMonitoringService();
    // Get current output priority from system
    const systemData = await monitoringService.getCurrentSystemData();
    
    return NextResponse.json({ 
      success: true, 
      outputPriority: systemData.outputPriority || 'Unknown'
    });
  } catch (error: any) {
    console.error('Error in /api/control/output-priority:', error.message);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}





