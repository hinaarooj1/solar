import asyncio
from datetime import datetime, timedelta, time
import pytz
from typing import Optional
import os
import logging
from dotenv import load_dotenv
from email_service import email_service
from telegram_service import telegram_service
from discord_service import discord_service
from settings_storage import settings_storage

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringService:
    """Background monitoring service for solar system alerts"""
    
    def __init__(self):
        self.last_grid_feed_check = None
        self.last_data_timestamp = datetime.now()
        
        # Load saved settings from storage
        self.grid_feeding_enabled = settings_storage.get("grid_feeding_enabled", True)
        self.previous_grid_feed_status = self.grid_feeding_enabled  # Track previous state
        self.is_load_shedding = False
        self.last_load_shedding_alert_time = None  # Track when last load shedding alert was sent
        self.system_online = True
        
        # Track system reset detection
        self.system_reset_detected = False
        self.last_known_output_priority = None
        self.last_reset_alert_time = None  # Track when last alert was sent
        
        # Track system mode changes
        self.current_system_mode = None
        self.previous_system_mode = None
        
        # Track missing data detection (based on most recent API call)
        self.api_data_failing = False
        self.last_missing_data_alert_time = None
        self.consecutive_api_failures = 0
        
        # Shutdown control
        self.shutdown_requested = False
        
        # Daily summary tracking
        self.last_daily_summary_date = None  # Track when last summary was sent
        self.pkt_timezone = pytz.timezone('Asia/Karachi')  # PKT timezone (GMT+5)
        
        # Load configuration from environment
        self.grid_feed_interval_hours = int(os.getenv("GRID_FEED_ALERT_INTERVAL_HOURS", 6))
        self.load_shedding_voltage_threshold = float(os.getenv("LOAD_SHEDDING_VOLTAGE_THRESHOLD", 180))
        self.system_offline_threshold_minutes = int(os.getenv("SYSTEM_OFFLINE_THRESHOLD_MINUTES", 10))
        self.low_production_threshold = float(os.getenv("LOW_PRODUCTION_THRESHOLD_WATTS", 500))
        
    def update_data_timestamp(self):
        """Update last seen timestamp when data is received"""
        self.last_data_timestamp = datetime.now()
        if not self.system_online:
            logger.info("System is back online!")
            self.system_online = True
    
    def set_grid_feeding_status(self, enabled: bool):
        """Update grid feeding status and save to storage"""
        # Check if status changed from enabled to disabled
        status_changed = self.previous_grid_feed_status != enabled
        went_from_on_to_off = self.previous_grid_feed_status and not enabled
        
        # Update current status
        self.previous_grid_feed_status = self.grid_feeding_enabled
        self.grid_feeding_enabled = enabled
        settings_storage.set("grid_feeding_enabled", enabled)
        
        if enabled:
            self.last_grid_feed_check = None  # Reset reminder timer
            logger.info("Grid feeding enabled - reminders paused")
        else:
            # If grid feeding just got disabled, send immediate alert
            if went_from_on_to_off:
                logger.warning("⚠️ Grid feeding just got DISABLED - sending immediate alert!")
                
                # Try email - don't crash if it fails
                try:
                    email_service.send_grid_feed_disabled_alert()
                    logger.info("✅ Grid feed disabled alert sent via Email")
                except Exception as e:
                    logger.error(f"❌ Email alert failed: {str(e)}")
                
                # Try Telegram - don't crash if it fails
                try:
                    telegram_service.send_grid_feed_disabled_alert()
                    logger.info("✅ Grid feed disabled alert sent via Telegram")
                except Exception as e:
                    logger.error(f"❌ Telegram alert failed: {str(e)}")
                
                # Try Discord - don't crash if it fails
                try:
                    discord_service.send_grid_feed_disabled_alert()
                    logger.info("✅ Grid feed disabled alert sent via Discord")
                except Exception as e:
                    logger.error(f"❌ Discord alert failed: {str(e)}")
                
                self.last_grid_feed_check = datetime.now()  # Start timer
            else:
                logger.info("Grid feeding disabled - reminders activated")
    
    async def check_grid_feed_reminder(self):
        """Check if grid feed reminder should be sent"""
        try:
            if self.grid_feeding_enabled:
                return  # No reminder needed
            
            now = datetime.now()
            
            # Check if enough time has passed since last reminder
            if self.last_grid_feed_check is None:
                # First time check - send initial reminder
                self._send_grid_feed_reminders()
                self.last_grid_feed_check = now
                logger.info(f"Grid feed reminder sent (initial)")
            else:
                time_since_last_check = now - self.last_grid_feed_check
                if time_since_last_check >= timedelta(hours=self.grid_feed_interval_hours):
                    self._send_grid_feed_reminders()
                    self.last_grid_feed_check = now
                    logger.info(f"Grid feed reminder sent (interval: {self.grid_feed_interval_hours}h)")
        except Exception as e:
            logger.error(f"Error in grid feed reminder check: {str(e)}")
    
    def _send_grid_feed_reminders(self):
        """Send grid feed reminders to all channels with error handling"""
        # Try email - don't crash if it fails
        try:
            email_service.send_grid_feed_reminder()
            logger.info("✅ Grid feed reminder sent via Email")
        except Exception as e:
            logger.error(f"❌ Email reminder failed: {str(e)}")
        
        # Try Telegram - don't crash if it fails
        try:
            telegram_service.send_grid_feed_reminder()
            logger.info("✅ Grid feed reminder sent via Telegram")
        except Exception as e:
            logger.error(f"❌ Telegram reminder failed: {str(e)}")
        
        # Try Discord - don't crash if it fails
        try:
            discord_service.send_grid_feed_reminder()
            logger.info("✅ Grid feed reminder sent via Discord")
        except Exception as e:
            logger.error(f"❌ Discord reminder failed: {str(e)}")
    
    async def check_load_shedding(self, utility_voltage: float):
        """
        Check for load shedding based on voltage
        Sends alerts every 5 hours while the condition persists
        """
        try:
            # Only check if voltage is greater than 0 (system is active)
            # 0V means system is off or in standby, not load shedding
            voltage_below_threshold = utility_voltage > 0 and utility_voltage < self.load_shedding_voltage_threshold
            
            now = datetime.now()
            
            if voltage_below_threshold:
                # Load shedding is active
                should_send_alert = False
                
                if not self.is_load_shedding:
                    # First time detecting load shedding - send immediate alert
                    should_send_alert = True
                    self.is_load_shedding = True
                    logger.warning(f"⚡ LOAD SHEDDING DETECTED! Voltage: {utility_voltage}V")
                elif self.last_load_shedding_alert_time is None:
                    # No previous alert time recorded - send alert
                    should_send_alert = True
                else:
                    # Check if 5 hours have passed since last alert
                    time_since_last_alert = now - self.last_load_shedding_alert_time
                    if time_since_last_alert >= timedelta(hours=5):
                        should_send_alert = True
                        logger.warning(f"⏰ 5-hour reminder: Load shedding still active ({utility_voltage}V)")
                
                # Send alerts if needed (with error handling for each channel)
                if should_send_alert:
                    duration = 0  # Could calculate actual duration if needed
                    
                    # Try email - don't crash if it fails
                    try:
                        email_service.send_load_shedding_alert(utility_voltage, duration)
                        logger.info("✅ Load shedding alert sent via Email")
                    except Exception as e:
                        logger.error(f"❌ Email alert failed: {str(e)}")
                    
                    # Try Telegram - don't crash if it fails
                    try:
                        telegram_service.send_load_shedding_alert(utility_voltage)
                        logger.info("✅ Load shedding alert sent via Telegram")
                    except Exception as e:
                        logger.error(f"❌ Telegram alert failed: {str(e)}")
                    
                    # Try Discord - don't crash if it fails
                    try:
                        discord_service.send_load_shedding_alert(utility_voltage)
                        logger.info("✅ Load shedding alert sent via Discord")
                    except Exception as e:
                        logger.error(f"❌ Discord alert failed: {str(e)}")
                    
                    self.last_load_shedding_alert_time = now
                    
            else:
                # Voltage is normal or system is off
                if self.is_load_shedding and utility_voltage > self.load_shedding_voltage_threshold:
                    # Load shedding ended
                    self.is_load_shedding = False
                    self.last_load_shedding_alert_time = None  # Reset alert timer
                    logger.info(f"✅ Grid power restored. Voltage: {utility_voltage}V")
                    
        except Exception as e:
            logger.error(f"Error in load shedding check: {str(e)}")
    
    async def check_system_offline(self):
        """Check if system has gone offline"""
        try:
            now = datetime.now()
            time_since_last_data = now - self.last_data_timestamp
            threshold = timedelta(minutes=self.system_offline_threshold_minutes)
            
            if time_since_last_data > threshold and self.system_online:
                # System has gone offline
                self.system_online = False
                minutes_offline = int(time_since_last_data.total_seconds() / 60)
                
                # Try email - don't crash if it fails
                try:
                    email_service.send_system_shutdown_alert(minutes_offline)
                    logger.info("✅ System offline alert sent via Email")
                except Exception as e:
                    logger.error(f"❌ Email alert failed: {str(e)}")
                
                # Try Telegram - don't crash if it fails
                try:
                    telegram_service.send_system_offline_alert(minutes_offline)
                    logger.info("✅ System offline alert sent via Telegram")
                except Exception as e:
                    logger.error(f"❌ Telegram alert failed: {str(e)}")
                
                # Try Discord - don't crash if it fails
                try:
                    discord_service.send_system_offline_alert(minutes_offline)
                    logger.info("✅ System offline alert sent via Discord")
                except Exception as e:
                    logger.error(f"❌ Discord alert failed: {str(e)}")
                
                logger.critical(f"System offline detected! Last seen {minutes_offline} minutes ago")
        except Exception as e:
            logger.error(f"Error in system offline check: {str(e)}")
    
    async def check_low_production(self, current_production: float, current_time: str):
        """Check if production is unusually low during peak hours"""
        try:
            # Parse time range from environment
            time_range = os.getenv("LOW_PRODUCTION_CHECK_START", "11:00") + "-" + os.getenv("LOW_PRODUCTION_CHECK_END", "15:00")
            start_time = os.getenv("LOW_PRODUCTION_CHECK_START", "11:00")
            end_time = os.getenv("LOW_PRODUCTION_CHECK_END", "15:00")
            
            # Check if current time is within peak hours
            now = datetime.now()
            current_hour_min = now.strftime("%H:%M")
            
            if start_time <= current_hour_min <= end_time:
                if current_production < self.low_production_threshold:
                    logger.warning(
                        f"Low production during peak hours: {current_production}W "
                        f"(threshold: {self.low_production_threshold}W)"
                    )
                    # Note: Only send email once per day to avoid spam
                    # Implementation can be enhanced with daily tracking
        except Exception as e:
            logger.error(f"Error in low production check: {str(e)}")
    
    async def check_system_mode_change(self, current_mode: str):
        """
        Check if system mode has changed and send multi-channel alerts
        Monitors: Line Mode, Battery Mode, Standby Mode
        """
        try:
            if not current_mode or current_mode == "Unknown":
                return
            
            # Update current mode
            self.current_system_mode = current_mode
            
            # Check if mode has changed
            if self.previous_system_mode and self.previous_system_mode != current_mode:
                logger.info(f"🔄 System mode changed: {self.previous_system_mode} → {current_mode}")
                
                # Prepare alert message
                timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Determine message based on mode transition
                if current_mode == "Battery Mode":
                    message = "Electricity Disconnected - Running on Battery Power!"
                    urgency = "WARNING"
                    emoji = "🔋"
                elif current_mode == "Line Mode":
                    if self.previous_system_mode == "Battery Mode":
                        message = "Electricity Restored - Grid Power Connected!"
                    else:
                        message = "Grid Power is Active"
                    urgency = "INFO"
                    emoji = "⚡"
                elif current_mode == "Standby Mode":
                    message = "System in Standby Mode - Power Off!"
                    urgency = "ALERT"
                    emoji = "⏸️"
                else:
                    message = f"System mode changed to {current_mode}"
                    urgency = "NOTICE"
                    emoji = "ℹ️"
                
                logger.warning(f"{emoji} {urgency}: {message}")
                
                # Send alerts to all channels
                # Email
                try:
                    email_success = email_service.send_mode_alert(current_mode, message, timestamp_str)
                    if email_success:
                        logger.info(f"✅ Mode change alert sent via Email: {current_mode}")
                    else:
                        logger.error(f"❌ Failed to send Email alert for mode: {current_mode}")
                except Exception as e:
                    logger.error(f"❌ Email service error: {str(e)}")
                
                # Telegram
                try:
                    telegram_success = telegram_service.send_mode_alert(current_mode, message, timestamp_str)
                    if telegram_success:
                        logger.info(f"✅ Mode change alert sent via Telegram: {current_mode}")
                    else:
                        logger.error(f"❌ Failed to send Telegram alert for mode: {current_mode}")
                except Exception as e:
                    logger.error(f"❌ Telegram service error: {str(e)}")
                
                # Discord
                try:
                    discord_success = discord_service.send_mode_alert(current_mode, message, timestamp_str)
                    if discord_success:
                        logger.info(f"✅ Mode change alert sent via Discord: {current_mode}")
                    else:
                        logger.error(f"❌ Failed to send Discord alert for mode: {current_mode}")
                except Exception as e:
                    logger.error(f"❌ Discord service error: {str(e)}")
            
            # Update previous mode for next check
            self.previous_system_mode = current_mode
            
        except Exception as e:
            logger.error(f"Error in system mode change check: {str(e)}")
    
    async def check_missing_data(self, api_data_success: bool):
        """
        Check if most recent API call failed (system offline/disconnected from network)
        Sends immediate alert when API fails, with hourly reminders while it keeps failing
        """
        try:
            import datetime as dt_module
            
            now = dt_module.datetime.now()
            
            if not api_data_success:
                # Most recent API call failed or returned empty data
                self.consecutive_api_failures += 1
                
                should_send_alert = False
                
                if not self.api_data_failing:
                    # First failure - send immediate alert
                    should_send_alert = True
                    self.api_data_failing = True
                    logger.critical(f"🚨 CRITICAL: API data fetch FAILED! System may be offline or disconnected")
                elif self.last_missing_data_alert_time is None:
                    # No previous alert sent
                    should_send_alert = True
                else:
                    # Check if 1 hour has passed since last alert
                    time_since_last_alert = now - self.last_missing_data_alert_time
                    if time_since_last_alert >= dt_module.timedelta(hours=1):
                        should_send_alert = True
                        logger.warning(f"⏰ 1-hour reminder: API still failing (consecutive failures: {self.consecutive_api_failures})")
                
                # Send alerts if needed
                if should_send_alert:
                    failure_duration = self.consecutive_api_failures * 5  # Each check is 5 minutes apart
                    failure_hours = failure_duration / 60
                    
                    # Email
                    try:
                        email_success = email_service.send_api_failure_alert(
                            failure_duration_minutes=failure_duration,
                            consecutive_failures=self.consecutive_api_failures
                        )
                        if email_success:
                            logger.info(f"✅ API failure alert sent via Email (failures: {self.consecutive_api_failures})")
                        else:
                            logger.error(f"❌ Failed to send Email alert for API failure")
                    except Exception as e:
                        logger.error(f"❌ Email service error: {str(e)}")
                    
                    # Telegram
                    try:
                        telegram_success = telegram_service.send_api_failure_alert(
                            failure_duration_minutes=failure_duration,
                            consecutive_failures=self.consecutive_api_failures
                        )
                        if telegram_success:
                            logger.info(f"✅ API failure alert sent via Telegram (failures: {self.consecutive_api_failures})")
                        else:
                            logger.error(f"❌ Failed to send Telegram alert for API failure")
                    except Exception as e:
                        logger.error(f"❌ Telegram service error: {str(e)}")
                    
                    # Discord
                    try:
                        discord_success = discord_service.send_api_failure_alert(
                            failure_duration_minutes=failure_duration,
                            consecutive_failures=self.consecutive_api_failures
                        )
                        if discord_success:
                            logger.info(f"✅ API failure alert sent via Discord (failures: {self.consecutive_api_failures})")
                        else:
                            logger.error(f"❌ Failed to send Discord alert for API failure")
                    except Exception as e:
                        logger.error(f"❌ Discord service error: {str(e)}")
                    
                    self.last_missing_data_alert_time = now
                    
            else:
                # API call succeeded - data is flowing
                if self.api_data_failing:
                    # Data resumed after being down
                    logger.info(f"✅ API data collection RESUMED after {self.consecutive_api_failures} consecutive failures")
                    
                    # Send recovery notification
                    try:
                        email_service.send_api_recovery_alert(self.consecutive_api_failures)
                        logger.info("✅ API recovery notification sent via Email")
                    except Exception as e:
                        logger.error(f"❌ Email recovery alert error: {str(e)}")
                    
                    try:
                        telegram_service.send_api_recovery_alert(self.consecutive_api_failures)
                        logger.info("✅ API recovery notification sent via Telegram")
                    except Exception as e:
                        logger.error(f"❌ Telegram recovery alert error: {str(e)}")
                    
                    try:
                        discord_service.send_api_recovery_alert(self.consecutive_api_failures)
                        logger.info("✅ API recovery notification sent via Discord")
                    except Exception as e:
                        logger.error(f"❌ Discord recovery alert error: {str(e)}")
                    
                    # Reset failure tracking
                    self.api_data_failing = False
                    self.consecutive_api_failures = 0
                    self.last_missing_data_alert_time = None
                else:
                    # Reset consecutive failures counter when data is flowing normally
                    self.consecutive_api_failures = 0
                    
        except Exception as e:
            logger.error(f"Error in missing data check: {str(e)}")
    
    async def check_system_reset(self, output_priority: str):
        """
        Check if inverter Output Priority has changed from normal "Solar Utility Bat"
        Sends alerts every hour while the condition persists
        """
        try:
            # Define the expected/normal value
            EXPECTED_OUTPUT_PRIORITY = "Solar Utility Bat"
            
            # Check if Output Priority has changed from expected value
            reset_detected = output_priority != EXPECTED_OUTPUT_PRIORITY and output_priority != "Unknown"
            
            now = datetime.now()
            
            if reset_detected:
                # System is in reset state
                should_send_alert = False
                
                if not self.system_reset_detected:
                    # First time detecting reset - send immediate alert
                    should_send_alert = True
                    self.system_reset_detected = True
                    logger.critical(f"🚨 INVERTER RESET DETECTED! Output Priority changed to: '{output_priority}'")
                elif self.last_reset_alert_time is None:
                    # No previous alert time recorded - send alert
                    should_send_alert = True
                else:
                    # Check if 1 hour has passed since last alert
                    time_since_last_alert = now - self.last_reset_alert_time
                    if time_since_last_alert >= timedelta(hours=1):
                        should_send_alert = True
                        logger.warning(f"⏰ Hourly reminder: Output Priority still at '{output_priority}' (1 hour since last alert)")
                
                # Send alerts if needed
                if should_send_alert:
                    # Try email - don't crash if it fails
                    try:
                        email_service.send_system_reset_alert(output_priority)
                        logger.info("✅ System reset alert sent via Email")
                    except Exception as e:
                        logger.error(f"❌ Email alert failed: {str(e)}")
                    
                    # Try Telegram - don't crash if it fails
                    try:
                        telegram_service.send_system_reset_alert(output_priority)
                        logger.info("✅ System reset alert sent via Telegram")
                    except Exception as e:
                        logger.error(f"❌ Telegram alert failed: {str(e)}")
                    
                    # Try Discord - don't crash if it fails
                    try:
                        discord_service.send_system_reset_alert(output_priority)
                        logger.info("✅ System reset alert sent via Discord")
                    except Exception as e:
                        logger.error(f"❌ Discord alert failed: {str(e)}")
                    
                    self.last_reset_alert_time = now
                    logger.info(f"System reset alert cycle completed")
                
            else:
                # System is back to normal
                if self.system_reset_detected:
                    logger.info("✅ System settings restored to normal - Output Priority back to 'Solar Utility Bat'")
                    self.system_reset_detected = False
                    self.last_reset_alert_time = None  # Reset alert timer
            
            # Update last known value
            self.last_known_output_priority = output_priority
            
        except Exception as e:
            logger.error(f"Error in system reset check: {str(e)}")
    
    async def get_current_system_data(self):
        """Fetch current system data including output priority, voltage, and system mode"""
        try:
            import datetime
            from watchpower_api import WatchPowerAPI
            import os
            
            # Get credentials from environment
            SERIAL_NUMBER = os.getenv("SERIAL_NUMBER")
            WIFI_PN = os.getenv("WIFI_PN")
            DEV_CODE = int(os.getenv("DEV_CODE"))
            DEV_ADDR = int(os.getenv("DEV_ADDR"))
            
            # Import the API manager from fastapi_app
            # We'll use a simple approach to avoid circular imports
            from fastapi_app import api_manager
            
            data = api_manager.handle_api_call(
                api_manager.wp.get_daily_data,
                day=datetime.date.today(),
                serial_number=SERIAL_NUMBER,
                wifi_pn=WIFI_PN,
                dev_code=DEV_CODE,
                dev_addr=DEV_ADDR
            )
            
            rows = data.get("dat", {}).get("row", [])
            if rows:
                latest_row = rows[-1]
                fields = latest_row.get("field", [])
                
                # Extract output priority (field 38)
                output_priority = str(fields[38]) if len(fields) > 38 and fields[38] else "Unknown"
                
                # Extract voltage data (fields 6 and 8)
                utility_voltage = float(fields[6]) if len(fields) > 6 and fields[6] else 0.0
                generator_voltage = float(fields[8]) if len(fields) > 8 and fields[8] else 0.0
                
                # Use generator voltage if utility is 0 (common in Pakistan)
                actual_grid_voltage = generator_voltage if utility_voltage == 0.0 else utility_voltage
                
                # Extract system mode (field 47)
                system_mode = str(fields[47]) if len(fields) > 47 and fields[47] else "Unknown"
                
                return {
                    "output_priority": output_priority,
                    "grid_voltage": actual_grid_voltage,
                    "system_mode": system_mode
                }
            
            return {
                "output_priority": "Unknown",
                "grid_voltage": 0.0,
                "system_mode": "Unknown"
            }
        except Exception as e:
            logger.error(f"Error fetching system data: {str(e)}")
            return {
                "output_priority": "Unknown",
                "grid_voltage": 0.0,
                "system_mode": "Unknown"
            }
    
    async def fetch_daily_stats(self, date_str: str):
        """Fetch and calculate daily statistics from the API"""
        try:
            import datetime as dt_module
            
            SERIAL_NUMBER = os.getenv("SERIAL_NUMBER")
            WIFI_PN = os.getenv("WIFI_PN")
            DEV_CODE = int(os.getenv("DEV_CODE"))
            DEV_ADDR = int(os.getenv("DEV_ADDR"))
            
            from fastapi_app import api_manager
            
            day = dt_module.datetime.strptime(date_str, "%Y-%m-%d").date()
            
            data = api_manager.handle_api_call(
                api_manager.wp.get_daily_data,
                day=day,
                serial_number=SERIAL_NUMBER,
                wifi_pn=WIFI_PN,
                dev_code=DEV_CODE,
                dev_addr=DEV_ADDR
            )
            
            rows = data.get("dat", {}).get("row", [])
            
            # Calculate stats similar to DailyStats.js
            total_production_wh = 0
            total_load_wh = 0
            battery_mode_hours = 0
            standby_mode_hours = 0
            interval_hours = 5 / 60  # 5 minutes
            
            for rec in rows:
                fields = rec.get("field", [])
                if len(fields) < 22:
                    continue
                
                timestamp = fields[1]
                if not timestamp.startswith(date_str):
                    continue
                
                # Parse power values
                try:
                    pv_power = float(fields[11]) if fields[11] not in ["", None] else 0.0
                except:
                    pv_power = 0.0
                    
                try:
                    load_power = float(fields[21]) if fields[21] not in ["", None] else 0.0
                except:
                    load_power = 0.0
                    
                try:
                    mode = str(fields[47]) if len(fields) > 47 and fields[47] not in ["", None] else ""
                except:
                    mode = ""
                
                # Calculate energy
                total_production_wh += pv_power * interval_hours
                total_load_wh += load_power * interval_hours
                
                # Track modes
                if mode == "Battery Mode":
                    battery_mode_hours += interval_hours
                elif mode == "Standby Mode":
                    standby_mode_hours += interval_hours
            
            # Calculate missing data
            expected_data_points = 288  # 24 * 60 / 5 = 288 data points per day
            actual_data_points = len([rec for rec in rows if rec.get("field", [])[1].startswith(date_str) if len(rec.get("field", [])) >= 22])
            missing_data_points = max(0, expected_data_points - actual_data_points)
            missing_data_hours = (missing_data_points * 5) / 60
            
            # Convert to kWh and format
            production_kwh = round(total_production_wh / 1000, 2)
            load_kwh = round(total_load_wh / 1000, 2)
            grid_contribution_kwh = round((total_production_wh - total_load_wh) / 1000, 2)
            
            # Format hours
            def format_hours(decimal_hours):
                hrs = int(decimal_hours)
                mins = round((decimal_hours - hrs) * 60)
                return f"{hrs} hr {mins} min"
            
            total_system_off = standby_mode_hours + missing_data_hours
            
            return {
                "date": date_str,
                "production_kwh": production_kwh,
                "load_kwh": load_kwh,
                "grid_contribution_kwh": grid_contribution_kwh,
                "load_shedding_hours": format_hours(battery_mode_hours),
                "standby_hours": format_hours(standby_mode_hours),
                "missing_data_hours": format_hours(missing_data_hours),
                "system_off_hours": format_hours(total_system_off),
                "timestamp": datetime.now(self.pkt_timezone).strftime("%Y-%m-%d %H:%M:%S PKT")
            }
            
        except Exception as e:
            logger.error(f"Error fetching daily stats: {str(e)}")
            return None
    
    async def check_and_send_daily_summary(self):
        """Check if it's time to send daily summary (12 AM PKT) and send it"""
        try:
            # Get current time in PKT
            now_pkt = datetime.now(self.pkt_timezone)
            current_date = now_pkt.date()
            current_time = now_pkt.time()
            
            # Check if it's past midnight (between 00:00 and 00:05)
            midnight = time(0, 0)
            five_past_midnight = time(0, 5)
            
            # Check if we should send summary
            if midnight <= current_time < five_past_midnight:
                # Check if we haven't sent summary for today yet
                if self.last_daily_summary_date != current_date:
                    # Get yesterday's date
                    yesterday = current_date - timedelta(days=1)
                    yesterday_str = yesterday.strftime("%Y-%m-%d")
                    
                    logger.info(f"🌙 It's midnight PKT! Preparing daily summary for {yesterday_str}...")
                    
                    # Fetch yesterday's stats
                    summary_data = await self.fetch_daily_stats(yesterday_str)
                    
                    if summary_data:
                        logger.info(f"📊 Sending daily summary for {yesterday_str}...")
                        
                        # Send via Email
                        try:
                            email_service.send_daily_summary(summary_data)
                            logger.info("✅ Daily summary sent via Email")
                        except Exception as e:
                            logger.error(f"❌ Email summary failed: {str(e)}")
                        
                        # Send via Telegram
                        try:
                            telegram_service.send_daily_summary(summary_data)
                            logger.info("✅ Daily summary sent via Telegram")
                        except Exception as e:
                            logger.error(f"❌ Telegram summary failed: {str(e)}")
                        
                        # Send via Discord
                        try:
                            discord_service.send_daily_summary(summary_data)
                            logger.info("✅ Daily summary sent via Discord")
                        except Exception as e:
                            logger.error(f"❌ Discord summary failed: {str(e)}")
                        
                        # Mark that we sent summary for this date
                        self.last_daily_summary_date = current_date
                        logger.info(f"✅ Daily summary sent successfully for {yesterday_str}")
                    else:
                        logger.error(f"❌ Failed to fetch daily stats for {yesterday_str}")
                        
        except Exception as e:
            logger.error(f"Error in daily summary check: {str(e)}")
    
    async def run_periodic_checks(self):
        """Run all periodic monitoring checks (every 5 minutes)"""
        logger.info("🔄 Starting monitoring service...")
        
        try:
            # Test basic functionality first
            logger.info("🧪 Testing monitoring service components...")
            
            while not self.shutdown_requested:
                try:
                    logger.info("⏰ Running periodic monitoring checks...")
                    
                    await self.check_grid_feed_reminder()
                    
                    # Fetch current system data (output priority + voltage + mode)
                    logger.info("📊 Fetching system data...")
                    system_data = await self.get_current_system_data()
                    
                    # Check if API returned valid data
                    api_data_valid = (
                        system_data.get("system_mode") != "Unknown" and 
                        system_data.get("output_priority") != "Unknown"
                    )
                    
                    # Check for missing data (based on most recent API call)
                    await self.check_missing_data(api_data_valid)
                    
                    # Check for system mode changes
                    system_mode = system_data.get("system_mode", "Unknown")
                    if system_mode != "Unknown":
                        await self.check_system_mode_change(system_mode)
                        logger.info(f"✅ Periodic check: System Mode = '{system_mode}'")
                    else:
                        logger.warning("⚠️ System mode data not available")
                    
                    # Check for system reset
                    output_priority = system_data.get("output_priority", "Unknown")
                    if output_priority != "Unknown":
                        await self.check_system_reset(output_priority)
                        logger.info(f"✅ Periodic check: Output Priority = '{output_priority}'")
                    else:
                        logger.warning("⚠️ Output Priority data not available")
                    
                    # Check for load shedding (voltage drop)
                    grid_voltage = system_data.get("grid_voltage", 0.0)
                    if grid_voltage > 0:  # Only check if we have valid voltage data
                        await self.check_load_shedding(grid_voltage)
                        logger.info(f"✅ Periodic check: Grid Voltage = {grid_voltage}V")
                    else:
                        logger.warning(f"⚠️ Grid voltage data not available (voltage: {grid_voltage}V)")
                    
                    # Check if it's time for daily summary (12 AM PKT)
                    await self.check_and_send_daily_summary()
                    
                    logger.info("✅ Periodic monitoring cycle completed successfully")
                    
                    # Wait for next check (with shutdown check)
                    logger.info("⏳ Waiting 6.67 minutes for next check...")
                    for i in range(400):  #  minutes =  seconds
                        if self.shutdown_requested:
                            logger.info("🛑 Shutdown requested, stopping monitoring")
                            break
                        await asyncio.sleep(1)
                        
                except asyncio.CancelledError:
                    logger.info("🛑 Monitoring service cancelled - shutting down gracefully")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in periodic checks: {str(e)}")
                    logger.error(f"❌ Error type: {type(e).__name__}")
                    import traceback
                    logger.error(f"❌ Traceback: {traceback.format_exc()}")
                    if not self.shutdown_requested:
                        logger.info("⏳ Waiting 1 minute before retry...")
                        await asyncio.sleep(60)  # Wait 1 minute before retry
                        
        except asyncio.CancelledError:
            logger.info("🛑 Monitoring service shutdown requested")
        except Exception as e:
            logger.error(f"💥 Critical error in monitoring service: {str(e)}")
            import traceback
            logger.error(f"💥 Traceback: {traceback.format_exc()}")
        finally:
            logger.info("🏁 Monitoring service stopped")
    
    def request_shutdown(self):
        """Request graceful shutdown of monitoring service"""
        self.shutdown_requested = True
        logger.info("Shutdown requested for monitoring service")


# Global monitoring service instance
monitoring_service = MonitoringService()
