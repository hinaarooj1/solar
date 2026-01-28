import { NextRequest, NextResponse } from 'next/server';
import { getWatchPowerAPISync } from '@/lib/watchpower-api';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const forceRefresh = searchParams.get('force_refresh') === 'true';
    
    const api = getWatchPowerAPISync();
    const data = await api.getDeviceLastData();
    
    if (!data.dat || !Array.isArray(data.dat) || data.dat.length === 0) {
      return NextResponse.json(
        { error: 'No data available from system' },
        { status: 503 }
      );
    }
    
    // Convert title/val array to object for easier access
    const deviceData: any = {};
    data.dat.forEach((item: any) => {
      if (item.title && item.val !== undefined) {
        deviceData[item.title] = item.val;
      }
    });
    
    // Extract key metrics using actual field names from WatchPower API
    const utilityVoltage = parseFloat(deviceData['Utility AC Voltage'] || '0');
    const generatorVoltage = parseFloat(deviceData['Generator AC Voltage'] || '0');
    const actualGridVoltage = utilityVoltage === 0 ? generatorVoltage : utilityVoltage;
    
    const utilityFrequency = parseFloat(deviceData['Utility AC Frequency'] || '0');
    const generatorFrequency = parseFloat(deviceData['Generator AC Frequency'] || '0');
    const actualGridFrequency = utilityFrequency === 0 ? generatorFrequency : utilityFrequency;
    
    const pvVoltage = parseFloat(deviceData['PV1 Input Voltage'] || '0');
    const pv1Power = parseFloat(deviceData['PV1 Charging Power'] || '0');
    const pv2Power = parseFloat(deviceData['PV2 Charging Power'] || '0');
    const pvPower = pv1Power + (isNaN(pv2Power) ? 0 : pv2Power);
    
    const acOutputVoltage = parseFloat(deviceData['AC Output Voltage'] || '0');
    const acOutputFrequency = parseFloat(deviceData['AC Output Frequency'] || '0');
    const acOutputPower = parseFloat(deviceData['AC Output Active Power'] || '0');
    const outputLoadPercent = parseFloat(deviceData['Output Load Percent'] || '0');
    const systemMode = deviceData['Mode'] || 'Unknown';
    
    // Health assessment
    let healthScore = 100;
    const warnings: string[] = [];
    const errors: string[] = [];
    
    // Check grid voltage
    if (actualGridVoltage > 0 && actualGridVoltage < 180) {
      warnings.push(`Low grid voltage: ${actualGridVoltage.toFixed(1)}V`);
      healthScore -= 15;
    } else if (actualGridVoltage > 250) {
      warnings.push(`High grid voltage: ${actualGridVoltage.toFixed(1)}V`);
      healthScore -= 10;
    }
    
    // Check grid frequency
    if (actualGridFrequency > 0 && (actualGridFrequency < 48 || actualGridFrequency > 52)) {
      warnings.push(`Grid frequency out of range: ${actualGridFrequency.toFixed(1)}Hz`);
      healthScore -= 10;
    }
    
    // Check system mode
    if (systemMode === "Fault Mode") {
      errors.push("System in fault mode");
      healthScore -= 50;
    } else if (systemMode === "Standby Mode") {
      warnings.push("System in standby mode");
      healthScore -= 5;
    }
    
    // Check load
    if (outputLoadPercent > 90) {
      warnings.push(`High load: ${outputLoadPercent}%`);
      healthScore -= 10;
    }
    
    // Determine status
    let status: string;
    if (errors.length > 0) {
      status = 'Critical';
    } else if (warnings.length > 0) {
      status = 'Warning';
    } else {
      status = 'Online';
    }
    
    const healthResponse = {
      timestamp: new Date().toISOString(),
      status,
      health_score: Math.max(0, healthScore),
      utility_ac_voltage: actualGridVoltage,
      utility_ac_frequency: actualGridFrequency,
      pv_input_voltage: pvVoltage,
      pv_charging_power: pvPower,
      ac_output_voltage: acOutputVoltage,
      ac_output_frequency: acOutputFrequency,
      ac_output_power: acOutputPower,
      output_load_percent: outputLoadPercent,
      system_mode: systemMode,
      warnings,
      errors
    };
    
    return NextResponse.json(healthResponse);
  } catch (error: any) {
    console.error('Error in /api/system/health:', error.message);
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
