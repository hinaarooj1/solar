import { NextResponse } from 'next/server';
import { getWatchPowerAPISync } from '@/lib/watchpower-api';
import settingsStorage from '@/lib/settings-storage';

export async function GET() {
  try {
    const api = getWatchPowerAPISync();
    const data = await api.getDeviceLastData();
    
    if (data.dat && Array.isArray(data.dat) && data.dat.length > 0) {
      // Convert title/val array to object for easier access
      const deviceData: any = {};
      data.dat.forEach((item: any) => {
        if (item.title && item.val !== undefined) {
          deviceData[item.title] = item.val;
        }
      });
      
      // Extract system settings from the parsed device data using actual field names
      const solarFeedPower = parseFloat(deviceData['Solar Feed To Grid Power'] || '0');
      const pv1Power = parseFloat(deviceData['PV1 Charging Power'] || '0');
      const pv2Power = parseFloat(deviceData['PV2 Charging Power'] || '0');
      const pvPower = pv1Power + (isNaN(pv2Power) ? 0 : pv2Power);
      const loadPower = parseFloat(deviceData['AC Output Active Power'] || '0');
      
      // Grid feeding detection logic (same as Python backend)
      const now = new Date();
      const currentHour = now.getHours();
      const currentTimeStr = now.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit', 
        hour12: true 
      });
      
      const isDaytime = currentHour >= 7 && currentHour <= 17;
      const isProducing = pvPower > 500;
      const isFeeding = solarFeedPower >= 50;
      
      let gridFeedEnabled: boolean;
      let feedStatus: string;
      let feedDisplay: string;
      
      if (isDaytime && isProducing) {
        if (isFeeding) {
          gridFeedEnabled = true;
          feedStatus = "enabled_feeding";
          feedDisplay = `Enabled & Feeding (${Math.round(solarFeedPower)}W) - ${currentTimeStr}`;
        } else {
          gridFeedEnabled = false;
          feedStatus = "disabled";
          feedDisplay = `DISABLED (Feed: ${Math.round(solarFeedPower)}W) - ${currentTimeStr}`;
        }
      } else {
        // Night or not producing - check saved status and feeding status
        const savedGridStatus = await settingsStorage.get("grid_feeding_enabled", true);
        
        if (isFeeding) {
          // If feeding ANY amount → ENABLED
          gridFeedEnabled = true;
          feedStatus = "enabled_feeding";
          feedDisplay = `Enabled & Feeding (${Math.round(solarFeedPower)}W) - ${currentTimeStr}`;
        } else if (savedGridStatus === false) {
          // Saved status says disabled + no feed → DISABLED
          gridFeedEnabled = false;
          feedStatus = "disabled";
          if (isDaytime) {
            feedDisplay = `DISABLED (PV: ${Math.round(pvPower)}W, Load: ${Math.round(loadPower)}W, Feed: ${Math.round(solarFeedPower)}W) - ${currentTimeStr}`;
          } else {
            feedDisplay = `DISABLED (Night) - ${currentTimeStr}`;
          }
        } else {
          // No feed but saved status says enabled → ENABLED (no excess to feed)
          gridFeedEnabled = true;
          feedStatus = "enabled_not_feeding";
          if (isDaytime) {
            feedDisplay = `Enabled (No excess, PV: ${Math.round(pvPower)}W, Load: ${Math.round(loadPower)}W) - ${currentTimeStr}`;
          } else {
            feedDisplay = `Enabled (Night, No Production) - ${currentTimeStr}`;
          }
        }
      }
      
      // Save the determined status for future reference
      await settingsStorage.set("grid_feeding_enabled", gridFeedEnabled);
      
      const settings = {
        grid_feed_enabled: gridFeedEnabled,
        grid_feed_display: feedDisplay,
        feed_status: feedStatus,
        solar_feed_power: solarFeedPower,
        pv_power: pvPower,
        load_status: deviceData['Load Status'] || 'Unknown',
        output_source_priority: deviceData['Output Source Priority'] || 'Solar First',
        charger_source_priority: deviceData['Charger Source Priority'] || 'Solar First', 
        ac_input_range: deviceData['AC Input Range'] || 'Appliance',
        system_status: deviceData['Mode'] || 'Normal',
        // Additional useful fields from actual API
        ac_output_power: parseFloat(deviceData['AC Output Active Power'] || '0'),
        utility_ac_voltage: parseFloat(deviceData['Utility AC Voltage'] || '0'),
        output_load_percent: parseFloat(deviceData['Output Load Percent'] || '0'),
        battery_voltage: parseFloat(deviceData['Battery Voltage'] || '0'),
        battery_capacity: parseFloat(deviceData['Battery Capacity'] || '0'),
        battery_charging_current: parseFloat(deviceData['Battery Charging Current'] || '0'),
        battery_discharge_current: parseFloat(deviceData['Battery Discharge Current'] || '0'),
        ac_output_voltage: parseFloat(deviceData['AC Output Voltage'] || '0'),
        ac_output_frequency: parseFloat(deviceData['AC Output Frequency'] || '0'),
        pv1_voltage: parseFloat(deviceData['PV1 Input Voltage'] || '0'),
        pv2_voltage: parseFloat(deviceData['PV2 Input Voltage'] || '0'),
        pv1_power: parseFloat(deviceData['PV1 Charging Power'] || '0'),
        pv2_power: parseFloat(deviceData['PV2 Charging Power'] || '0'),
        total_generation: parseFloat(deviceData['Total Generation'] || '0'),
        today_generation: parseFloat(deviceData['Today Generation'] || '0'),
        battery_type: deviceData['Battery Type'] || 'Unknown',
      };
      
      return NextResponse.json({ success: true, settings });
    } else {
      return NextResponse.json({ 
        success: false, 
        error: 'No device data available'
      }, { status: 404 });
    }
  } catch (error: any) {
    console.error('Error in /api/system/settings/current:', error.message);
    return NextResponse.json({ 
      success: false, 
      error: error.message
    }, { status: 500 });
  }
}
