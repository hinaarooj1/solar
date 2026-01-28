import { NextRequest, NextResponse } from 'next/server';
import { getMonitoringService } from '@/lib/monitoring-service';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const forceRefresh = searchParams.get('force_refresh') === 'true';
    
    const monitoringService = getMonitoringService();
    const systemData = await monitoringService.getCurrentSystemData();
    
    const EXPECTED_OUTPUT_PRIORITY = "Solar Utility Bat";
    const resetDetected = systemData.outputPriority !== EXPECTED_OUTPUT_PRIORITY && 
                         systemData.outputPriority !== "Unknown";
    
    const resetReasons = [];
    if (resetDetected) {
      resetReasons.push(`Output Priority changed from '${EXPECTED_OUTPUT_PRIORITY}' to '${systemData.outputPriority}'`);
      
      // Trigger monitoring service alert
      await monitoringService.checkSystemReset(systemData.outputPriority);
    }
    
    const response = {
      success: true,
      timestamp: new Date().toISOString(),
      reset_detected: resetDetected,
      reset_reasons: resetReasons,
      settings: {
        output_source_priority: systemData.outputPriority,
        expected_output_priority: EXPECTED_OUTPUT_PRIORITY
      },
      recommendations: resetDetected ? [
        "Open WatchPower app",
        "Set Output Priority back to 'Solar Utility Bat'",
        "Disable LCD Auto Return if enabled",
        "Enable Grid Feeding if it was disabled"
      ] : [],
      note: "Alerts sent via Email, Telegram, and Discord when reset is detected"
    };
    
    return NextResponse.json(response);
  } catch (error: any) {
    console.error('Error in /api/system/check-reset:', error.message);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}










