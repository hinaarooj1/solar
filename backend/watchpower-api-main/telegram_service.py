import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram notification service using Telegram Bot API (100% FREE)"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        
        if not all([self.bot_token, self.chat_id]):
            logger.warning("Telegram configuration incomplete. Telegram notifications will be disabled.")
        else:
            logger.info("Telegram service initialized successfully")
    
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send Telegram message"""
        try:
            if not self.bot_token or not self.chat_id:
                logger.error("Telegram not configured")
                return False
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
    
    def send_grid_feed_disabled_alert(self) -> bool:
        """Send Telegram when grid feeding is disabled"""
        message = """
🚨 *URGENT: Solar System Alert*

*Grid Feeding: JUST DISABLED* 🔴

Your solar system is no longer feeding excess power to the grid.

⚠️ *Impact:*
• Excess solar energy will be wasted
• No revenue from grid export
• Reduced system efficiency

💡 *Action Required:*
Open WatchPower app and enable grid feeding immediately!

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Immediate Alert
        """.strip()
        
        return self.send_message(message)
    
    def send_grid_feed_reminder(self) -> bool:
        """Send Telegram reminder for disabled grid feeding"""
        message = """
⚠️ *Solar System Reminder*

*Grid Feeding: STILL DISABLED*

Your system is not feeding power to the grid.

💡 *Recommended Action:*
Enable grid feeding in WatchPower app to maximize ROI.

━━━━━━━━━━━━━━━━━━
🤖 Hourly Reminder - Solar Dashboard
        """.strip()
        
        return self.send_message(message)
    
    def send_load_shedding_alert(self, voltage: float) -> bool:
        """Send Telegram when load shedding is detected"""
        message = f"""
⚡ *URGENT: Load Shedding Alert*

*Grid Power: DISCONNECTED* 🔴

📊 Grid Voltage: {voltage}V (Below normal)

✅ Your solar system is handling the load
⚠️ Monitor for extended outages

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Critical Alert
        """.strip()
        
        return self.send_message(message)
    
    def send_system_offline_alert(self, minutes: int) -> bool:
        """Send Telegram when system goes offline"""
        message = f"""
🚨 *CRITICAL: System Offline*

*Solar System: NOT RESPONDING* ❌

⏱️ Last seen: {minutes} minutes ago

🔧 *Check immediately:*
• Inverter power status
• WiFi/network connection
• Error codes on display
• System breakers/fuses

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Critical Alert
        """.strip()
        
        return self.send_message(message)
    
    def send_system_reset_alert(self, output_priority: str) -> bool:
        """Send Telegram when inverter Output Priority has changed from normal value"""
        
        message = f"""
🚨 *CRITICAL: Inverter Reset Detected!*

*Inverter Settings Have Been Reset* ⚠️

This typically happens after a power cut or PV surge.

📋 *Detected Changes:*
• Output Priority changed to '{output_priority}' (expected: 'Solar Utility Bat')

💡 *Action Required:*
1. Open WatchPower app immediately
2. Restore your preferred settings:
   - Set Output Priority back to 'Solar Utility Bat'
   - Disable LCD Auto Return if enabled
   - Enable Grid Feeding if it was disabled

⚠️ *Note:* System may not be operating optimally until settings are restored!

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - System Reset Alert
        """.strip()
        
        return self.send_message(message)
    
    def send_daily_summary(self, summary_data: dict) -> bool:
        """Send daily summary via Telegram"""
        date = summary_data.get("date", "Unknown")
        production_kwh = summary_data.get("production_kwh", 0)
        load_kwh = summary_data.get("load_kwh", 0)
        grid_contribution_kwh = summary_data.get("grid_contribution_kwh", 0)
        load_shedding_hours = summary_data.get("load_shedding_hours", 0)
        system_off_hours = summary_data.get("system_off_hours", 0)
        missing_data_hours = summary_data.get("missing_data_hours", 0)
        
        message = f"""
📊 *Daily Solar Summary - {date}*

☀️ *SOLAR PRODUCTION*
━━━━━━━━━━━━━━━━━━━━━━━━
Total Production: *{production_kwh} kWh*

⚡ *ENERGY USAGE*
━━━━━━━━━━━━━━━━━━━━━━━━
Total Consumption: *{load_kwh} kWh*

🔋 *GRID CONTRIBUTION*
━━━━━━━━━━━━━━━━━━━━━━━━
Energy Fed to Grid: *{grid_contribution_kwh} kWh*

🔌 *LOAD SHEDDING*
━━━━━━━━━━━━━━━━━━━━━━━━
Battery/Solar Runtime: *{load_shedding_hours}*

⏸️ *SYSTEM OFF TIME*
━━━━━━━━━━━━━━━━━━━━━━━━
Total Off Duration: *{system_off_hours}*
  • Standby Mode: {summary_data.get("standby_hours", 0)}
  • Missing Data: {missing_data_hours}

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Daily Summary
Generated at {summary_data.get("timestamp", "Unknown")}
        """.strip()
        
        return self.send_message(message)
    
    def send_mode_alert(self, mode: str, message_text: str, timestamp: str) -> bool:
        """Send alert when system mode changes"""
        if mode == "Battery Mode":
            emoji = "🔋"
            urgency = "WARNING"
            color_indicator = "🔴"
        elif mode == "Line Mode":
            emoji = "⚡"
            urgency = "INFO"
            color_indicator = "🟢"
        elif mode == "Standby Mode":
            emoji = "⏸️"
            urgency = "ALERT"
            color_indicator = "🟠"
        else:
            emoji = "ℹ️"
            urgency = "NOTICE"
            color_indicator = "⚪"
        
        message = f"""
{emoji} *{urgency}: Solar System Mode Changed*

*Status:* {mode} {color_indicator}
*Message:* {message_text}
*Time:* {timestamp}

━━━━━━━━━━━━━━━━━━

*Mode Details:*
{emoji} {mode}

{message_text}

*What this means:*
"""
        
        if mode == "Battery Mode":
            message += """
⚡ Electricity is disconnected
🔋 System running on battery power
⚠️ Load shedding detected
💡 Your backup system is protecting your home

*Action:* Monitor battery levels and wait for grid restoration.
"""
        elif mode == "Line Mode":
            message += """
✅ Electricity has been restored
⚡ Grid power is now active
🔋 Batteries will start recharging
💡 System back to normal operation

*Action:* No action needed - System operating normally.
"""
        elif mode == "Standby Mode":
            message += """
⏸️ System in standby mode
🔴 Power is off
⚠️ No power generation or consumption
💡 System may need attention

*Action:* Check your solar system and inverter status.
"""
        
        message += """

━━━━━━━━━━━━━━━━━━
🤖 Real-time Alert - Solar Dashboard
Monitoring your solar system 24/7
        """.strip()
        
        return self.send_message(message)
    
    def send_api_failure_alert(self, failure_duration_minutes: int, consecutive_failures: int) -> bool:
        """Send alert when most recent API call fails (system offline/network disconnected)"""
        # Format duration nicely
        hrs = failure_duration_minutes // 60
        mins = failure_duration_minutes % 60
        duration_str = f"{hrs} hr {mins} min" if hrs > 0 else f"{mins} min"
        
        message = f"""
🚨 *CRITICAL: Solar System NOT RESPONDING*

*Your solar system API has FAILED to return data!*

━━━━━━━━━━━━━━━━━━

⚠️ *API FAILURE DETECTED:*
• Consecutive Failures: *{consecutive_failures}*
• Duration: *{duration_str}*
• Last Successful Check: {duration_str} ago
• Status: System OFFLINE or Network Disconnected

━━━━━━━━━━━━━━━━━━

🔍 *WHAT THIS MEANS:*

The monitoring system cannot communicate with your inverter.

*Possible reasons:*
• System is completely powered off
• WiFi/Network connection lost
• Inverter in deep standby mode
• Communication hardware failure
• WatchPower server issues

━━━━━━━━━━━━━━━━━━

🔧 *IMMEDIATE ACTION REQUIRED:*

1. Check inverter display - Is it ON? ✅
2. Check WiFi connection - Is inverter connected? ✅
3. Check internet connectivity ✅
4. Verify network cables and power ✅
5. Open WatchPower app - Can you see live data? ✅
6. Check inverter error codes/warnings ✅

⏰ You'll receive hourly reminders until API connection resumes.

━━━━━━━━━━━━━━━━━━
🤖 CRITICAL Alert - Solar Dashboard
Real-time Monitoring Active
        """.strip()
        
        return self.send_message(message)
    
    def send_api_recovery_alert(self, total_failures: int) -> bool:
        """Send notification when API data resumes after failure"""
        message = f"""
✅ *RESOLVED: Solar System Connection Restored*

*Your solar system API is now responding normally!*

━━━━━━━━━━━━━━━━━━

🎉 *CONNECTION RESTORED:*
• API Status: *ONLINE* ✅
• Data Flow: *RESUMED* ✅
• Total Failures During Outage: {total_failures}

━━━━━━━━━━━━━━━━━━

🔍 *WHAT HAPPENED:*

The monitoring system has successfully reconnected to your inverter.
Data collection and monitoring are now back to normal.

System is operating normally again.

━━━━━━━━━━━━━━━━━━

💡 *NEXT STEPS:*

• Monitor dashboard to verify all metrics are updating
• Check if any settings were affected during offline period
• Review missed data on DailyStats page

No further action needed - system is back online!

━━━━━━━━━━━━━━━━━━
🤖 Recovery Alert - Solar Dashboard
Monitoring Resumed
        """.strip()
        
        return self.send_message(message)
    
    def send_test_message(self) -> bool:
        """Send test Telegram message"""
        message = """
✅ *Solar Dashboard Connected!*

Your Telegram notifications are now active! 🎉

You'll receive instant alerts for:
🔌 Grid feeding status changes
⚡ Load shedding detection
🚨 System offline warnings
☀️ Low production alerts
🔄 System reset detection

Reminder Interval: Every 1 hour ⏰

━━━━━━━━━━━━━━━━━━
🤖 Test Message - Solar Dashboard
        """.strip()
        
        return self.send_message(message)


# Global Telegram service instance
telegram_service = TelegramService()


from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramService:
    """Telegram notification service using Telegram Bot API (100% FREE)"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        
        if not all([self.bot_token, self.chat_id]):
            logger.warning("Telegram configuration incomplete. Telegram notifications will be disabled.")
        else:
            logger.info("Telegram service initialized successfully")
    
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """Send Telegram message"""
        try:
            if not self.bot_token or not self.chat_id:
                logger.error("Telegram not configured")
                return False
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
    
    def send_grid_feed_disabled_alert(self) -> bool:
        """Send Telegram when grid feeding is disabled"""
        message = """
🚨 *URGENT: Solar System Alert*

*Grid Feeding: JUST DISABLED* 🔴

Your solar system is no longer feeding excess power to the grid.

⚠️ *Impact:*
• Excess solar energy will be wasted
• No revenue from grid export
• Reduced system efficiency

💡 *Action Required:*
Open WatchPower app and enable grid feeding immediately!

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Immediate Alert
        """.strip()
        
        return self.send_message(message)
    
    def send_grid_feed_reminder(self) -> bool:
        """Send Telegram reminder for disabled grid feeding"""
        message = """
⚠️ *Solar System Reminder*

*Grid Feeding: STILL DISABLED*

Your system is not feeding power to the grid.

💡 *Recommended Action:*
Enable grid feeding in WatchPower app to maximize ROI.

━━━━━━━━━━━━━━━━━━
🤖 Hourly Reminder - Solar Dashboard
        """.strip()
        
        return self.send_message(message)
    
    def send_load_shedding_alert(self, voltage: float) -> bool:
        """Send Telegram when load shedding is detected"""
        message = f"""
⚡ *URGENT: Load Shedding Alert*

*Grid Power: DISCONNECTED* 🔴

📊 Grid Voltage: {voltage}V (Below normal)

✅ Your solar system is handling the load
⚠️ Monitor for extended outages

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Critical Alert
        """.strip()
        
        return self.send_message(message)
    
    def send_system_offline_alert(self, minutes: int) -> bool:
        """Send Telegram when system goes offline"""
        message = f"""
🚨 *CRITICAL: System Offline*

*Solar System: NOT RESPONDING* ❌

⏱️ Last seen: {minutes} minutes ago

🔧 *Check immediately:*
• Inverter power status
• WiFi/network connection
• Error codes on display
• System breakers/fuses

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Critical Alert
        """.strip()
        
        return self.send_message(message)
    
    def send_system_reset_alert(self, output_priority: str) -> bool:
        """Send Telegram when inverter Output Priority has changed from normal value"""
        
        message = f"""
🚨 *CRITICAL: Inverter Reset Detected!*

*Inverter Settings Have Been Reset* ⚠️

This typically happens after a power cut or PV surge.

📋 *Detected Changes:*
• Output Priority changed to '{output_priority}' (expected: 'Solar Utility Bat')

💡 *Action Required:*
1. Open WatchPower app immediately
2. Restore your preferred settings:
   - Set Output Priority back to 'Solar Utility Bat'
   - Disable LCD Auto Return if enabled
   - Enable Grid Feeding if it was disabled

⚠️ *Note:* System may not be operating optimally until settings are restored!

━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - System Reset Alert
        """.strip()
        
        return self.send_message(message)
    
    def send_daily_summary(self, summary_data: dict) -> bool:
        """Send daily summary via Telegram"""
        date = summary_data.get("date", "Unknown")
        production_kwh = summary_data.get("production_kwh", 0)
        load_kwh = summary_data.get("load_kwh", 0)
        grid_contribution_kwh = summary_data.get("grid_contribution_kwh", 0)
        load_shedding_hours = summary_data.get("load_shedding_hours", 0)
        system_off_hours = summary_data.get("system_off_hours", 0)
        missing_data_hours = summary_data.get("missing_data_hours", 0)
        
        message = f"""
📊 *Daily Solar Summary - {date}*

☀️ *SOLAR PRODUCTION*
━━━━━━━━━━━━━━━━━━━━━━━━
Total Production: *{production_kwh} kWh*

⚡ *ENERGY USAGE*
━━━━━━━━━━━━━━━━━━━━━━━━
Total Consumption: *{load_kwh} kWh*

🔋 *GRID CONTRIBUTION*
━━━━━━━━━━━━━━━━━━━━━━━━
Energy Fed to Grid: *{grid_contribution_kwh} kWh*

🔌 *LOAD SHEDDING*
━━━━━━━━━━━━━━━━━━━━━━━━
Battery/Solar Runtime: *{load_shedding_hours}*

⏸️ *SYSTEM OFF TIME*
━━━━━━━━━━━━━━━━━━━━━━━━
Total Off Duration: *{system_off_hours}*
  • Standby Mode: {summary_data.get("standby_hours", 0)}
  • Missing Data: {missing_data_hours}

━━━━━━━━━━━━━━━━━━━━━━━━
🤖 Solar Dashboard - Daily Summary
Generated at {summary_data.get("timestamp", "Unknown")}
        """.strip()
        
        return self.send_message(message)
    
    def send_mode_alert(self, mode: str, message_text: str, timestamp: str) -> bool:
        """Send alert when system mode changes"""
        if mode == "Battery Mode":
            emoji = "🔋"
            urgency = "WARNING"
            color_indicator = "🔴"
        elif mode == "Line Mode":
            emoji = "⚡"
            urgency = "INFO"
            color_indicator = "🟢"
        elif mode == "Standby Mode":
            emoji = "⏸️"
            urgency = "ALERT"
            color_indicator = "🟠"
        else:
            emoji = "ℹ️"
            urgency = "NOTICE"
            color_indicator = "⚪"
        
        message = f"""
{emoji} *{urgency}: Solar System Mode Changed*

*Status:* {mode} {color_indicator}
*Message:* {message_text}
*Time:* {timestamp}

━━━━━━━━━━━━━━━━━━

*Mode Details:*
{emoji} {mode}

{message_text}

*What this means:*
"""
        
        if mode == "Battery Mode":
            message += """
⚡ Electricity is disconnected
🔋 System running on battery power
⚠️ Load shedding detected
💡 Your backup system is protecting your home

*Action:* Monitor battery levels and wait for grid restoration.
"""
        elif mode == "Line Mode":
            message += """
✅ Electricity has been restored
⚡ Grid power is now active
🔋 Batteries will start recharging
💡 System back to normal operation

*Action:* No action needed - System operating normally.
"""
        elif mode == "Standby Mode":
            message += """
⏸️ System in standby mode
🔴 Power is off
⚠️ No power generation or consumption
💡 System may need attention

*Action:* Check your solar system and inverter status.
"""
        
        message += """

━━━━━━━━━━━━━━━━━━
🤖 Real-time Alert - Solar Dashboard
Monitoring your solar system 24/7
        """.strip()
        
        return self.send_message(message)
    
    def send_api_failure_alert(self, failure_duration_minutes: int, consecutive_failures: int) -> bool:
        """Send alert when most recent API call fails (system offline/network disconnected)"""
        # Format duration nicely
        hrs = failure_duration_minutes // 60
        mins = failure_duration_minutes % 60
        duration_str = f"{hrs} hr {mins} min" if hrs > 0 else f"{mins} min"
        
        message = f"""
🚨 *CRITICAL: Solar System NOT RESPONDING*

*Your solar system API has FAILED to return data!*

━━━━━━━━━━━━━━━━━━

⚠️ *API FAILURE DETECTED:*
• Consecutive Failures: *{consecutive_failures}*
• Duration: *{duration_str}*
• Last Successful Check: {duration_str} ago
• Status: System OFFLINE or Network Disconnected

━━━━━━━━━━━━━━━━━━

🔍 *WHAT THIS MEANS:*

The monitoring system cannot communicate with your inverter.

*Possible reasons:*
• System is completely powered off
• WiFi/Network connection lost
• Inverter in deep standby mode
• Communication hardware failure
• WatchPower server issues

━━━━━━━━━━━━━━━━━━

🔧 *IMMEDIATE ACTION REQUIRED:*

1. Check inverter display - Is it ON? ✅
2. Check WiFi connection - Is inverter connected? ✅
3. Check internet connectivity ✅
4. Verify network cables and power ✅
5. Open WatchPower app - Can you see live data? ✅
6. Check inverter error codes/warnings ✅

⏰ You'll receive hourly reminders until API connection resumes.

━━━━━━━━━━━━━━━━━━
🤖 CRITICAL Alert - Solar Dashboard
Real-time Monitoring Active
        """.strip()
        
        return self.send_message(message)
    
    def send_api_recovery_alert(self, total_failures: int) -> bool:
        """Send notification when API data resumes after failure"""
        message = f"""
✅ *RESOLVED: Solar System Connection Restored*

*Your solar system API is now responding normally!*

━━━━━━━━━━━━━━━━━━

🎉 *CONNECTION RESTORED:*
• API Status: *ONLINE* ✅
• Data Flow: *RESUMED* ✅
• Total Failures During Outage: {total_failures}

━━━━━━━━━━━━━━━━━━

🔍 *WHAT HAPPENED:*

The monitoring system has successfully reconnected to your inverter.
Data collection and monitoring are now back to normal.

System is operating normally again.

━━━━━━━━━━━━━━━━━━

💡 *NEXT STEPS:*

• Monitor dashboard to verify all metrics are updating
• Check if any settings were affected during offline period
• Review missed data on DailyStats page

No further action needed - system is back online!

━━━━━━━━━━━━━━━━━━
🤖 Recovery Alert - Solar Dashboard
Monitoring Resumed
        """.strip()
        
        return self.send_message(message)
    
    def send_test_message(self) -> bool:
        """Send test Telegram message"""
        message = """
✅ *Solar Dashboard Connected!*

Your Telegram notifications are now active! 🎉

You'll receive instant alerts for:
🔌 Grid feeding status changes
⚡ Load shedding detection
🚨 System offline warnings
☀️ Low production alerts
🔄 System reset detection

Reminder Interval: Every 1 hour ⏰

━━━━━━━━━━━━━━━━━━
🤖 Test Message - Solar Dashboard
        """.strip()
        
        return self.send_message(message)


# Global Telegram service instance
telegram_service = TelegramService()

