import os
import requests
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordService:
    """Discord notification service using Discord Webhooks (100% FREE)"""
    
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        if not self.webhook_url:
            logger.warning("Discord webhook not configured. Discord notifications will be disabled.")
        else:
            logger.info("Discord service initialized successfully")
    
    def send_message(self, content: str, embed: dict = None) -> bool:
        """Send Discord message via webhook"""
        try:
            if not self.webhook_url:
                logger.error("Discord webhook not configured")
                return False
            
            payload = {}
            
            if embed:
                payload["embeds"] = [embed]
            else:
                payload["content"] = content
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info("Discord message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Discord message: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send Discord message: {str(e)}")
            return False
    
    def send_grid_feed_disabled_alert(self) -> bool:
        """Send Discord embed when grid feeding is disabled"""
        embed = {
            "title": "🚨 URGENT: Solar System Alert",
            "description": "**Grid Feeding: JUST DISABLED** 🔴\n\nYour solar system is no longer feeding excess power to the grid.",
            "color": 15158332,  # Red color
            "fields": [
                {
                    "name": "⚠️ Impact",
                    "value": "• Excess solar energy will be wasted\n• No revenue from grid export\n• Reduced system efficiency",
                    "inline": False
                },
                {
                    "name": "💡 Action Required",
                    "value": "Open WatchPower app and enable grid feeding immediately!",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Solar Dashboard - Immediate Alert"
            },
            "timestamp": None
        }
        
        return self.send_message(None, embed)
    
    def send_grid_feed_reminder(self) -> bool:
        """Send Discord reminder for disabled grid feeding"""
        embed = {
            "title": "⚠️ Solar System Reminder",
            "description": "**Grid Feeding: STILL DISABLED**\n\nYour system is not feeding power to the grid.",
            "color": 16753920,  # Orange color
            "fields": [
                {
                    "name": "💡 Recommended Action",
                    "value": "Enable grid feeding in WatchPower app to maximize ROI.",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Hourly Reminder - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_load_shedding_alert(self, voltage: float) -> bool:
        """Send Discord when load shedding is detected"""
        embed = {
            "title": "⚡ URGENT: Load Shedding Alert",
            "description": "**Grid Power: DISCONNECTED** 🔴",
            "color": 15158332,  # Red color
            "fields": [
                {
                    "name": "📊 Grid Voltage",
                    "value": f"{voltage}V (Below normal)",
                    "inline": True
                },
                {
                    "name": "Status",
                    "value": "✅ Solar system handling load\n⚠️ Monitor for extended outages",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Solar Dashboard - Critical Alert"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_system_offline_alert(self, minutes: int) -> bool:
        """Send Discord when system goes offline"""
        embed = {
            "title": "🚨 CRITICAL: System Offline",
            "description": "**Solar System: NOT RESPONDING** ❌",
            "color": 10038562,  # Dark red color
            "fields": [
                {
                    "name": "⏱️ Last Seen",
                    "value": f"{minutes} minutes ago",
                    "inline": True
                },
                {
                    "name": "🔧 Check immediately",
                    "value": "• Inverter power status\n• WiFi/network connection\n• Error codes on display\n• System breakers/fuses",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Solar Dashboard - Critical Alert"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_system_reset_alert(self, output_priority: str) -> bool:
        """Send Discord when inverter Output Priority has changed from normal value"""
        
        embed = {
            "title": "🚨 CRITICAL: Inverter Reset Detected!",
            "description": "**Inverter Settings Have Been Reset** ⚠️\n\nThis typically happens after a power cut or PV surge.",
            "color": 15158332,  # Red color
            "fields": [
                {
                    "name": "📋 Detected Changes",
                    "value": f"• Output Priority changed to '{output_priority}' (expected: 'Solar Utility Bat')",
                    "inline": False
                },
                {
                    "name": "💡 Action Required",
                    "value": "1. Open WatchPower app immediately\n2. Restore your preferred settings:\n   - Set Output Priority back to 'Solar Utility Bat'\n   - Disable LCD Auto Return if enabled\n   - Enable Grid Feeding if it was disabled",
                    "inline": False
                },
                {
                    "name": "⚠️ Note",
                    "value": "System may not be operating optimally until settings are restored!",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Solar Dashboard - System Reset Alert"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_daily_summary(self, summary_data: dict) -> bool:
        """Send daily summary via Discord"""
        date = summary_data.get("date", "Unknown")
        production_kwh = summary_data.get("production_kwh", 0)
        load_kwh = summary_data.get("load_kwh", 0)
        grid_contribution_kwh = summary_data.get("grid_contribution_kwh", 0)
        load_shedding_hours = summary_data.get("load_shedding_hours", 0)
        system_off_hours = summary_data.get("system_off_hours", 0)
        missing_data_hours = summary_data.get("missing_data_hours", 0)
        
        embed = {
            "title": f"📊 Daily Solar Summary - {date}",
            "description": "Your daily solar system performance report",
            "color": 3447003,  # Blue color
            "fields": [
                {
                    "name": "☀️ Solar Production",
                    "value": f"**{production_kwh} kWh**",
                    "inline": True
                },
                {
                    "name": "⚡ Energy Usage",
                    "value": f"**{load_kwh} kWh**",
                    "inline": True
                },
                {
                    "name": "🔋 Grid Contribution",
                    "value": f"**{grid_contribution_kwh} kWh**",
                    "inline": True
                },
                {
                    "name": "🔌 Load Shedding",
                    "value": f"Battery/Solar Runtime: **{load_shedding_hours}**",
                    "inline": False
                },
                {
                    "name": "⏸️ System Off Time",
                    "value": f"Total: **{system_off_hours}**\n• Standby Mode: {summary_data.get('standby_hours', 0)}\n• Missing Data: {missing_data_hours}",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Solar Dashboard - Generated at {summary_data.get('timestamp', 'Unknown')}"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_mode_alert(self, mode: str, message_text: str, timestamp: str) -> bool:
        """Send alert when system mode changes"""
        if mode == "Battery Mode":
            emoji = "🔋"
            urgency = "WARNING"
            color = 15158332  # Red
        elif mode == "Line Mode":
            emoji = "⚡"
            urgency = "INFO"
            color = 5763719  # Green
        elif mode == "Standby Mode":
            emoji = "⏸️"
            urgency = "ALERT"
            color = 16753920  # Orange
        else:
            emoji = "ℹ️"
            urgency = "NOTICE"
            color = 7506394  # Gray
        
        # Build description based on mode
        what_this_means = ""
        if mode == "Battery Mode":
            what_this_means = "⚡ Electricity is disconnected\n🔋 System running on battery power\n⚠️ Load shedding detected\n💡 Your backup system is protecting your home\n\n**Action:** Monitor battery levels and wait for grid restoration."
        elif mode == "Line Mode":
            what_this_means = "✅ Electricity has been restored\n⚡ Grid power is now active\n🔋 Batteries will start recharging\n💡 System back to normal operation\n\n**Action:** No action needed - System operating normally."
        elif mode == "Standby Mode":
            what_this_means = "⏸️ System in standby mode\n🔴 Power is off\n⚠️ No power generation or consumption\n💡 System may need attention\n\n**Action:** Check your solar system and inverter status."
        
        embed = {
            "title": f"{emoji} {urgency}: Solar System Mode Changed",
            "description": f"**Status:** {mode}\n**Message:** {message_text}\n**Time:** {timestamp}",
            "color": color,
            "fields": [
                {
                    "name": f"{emoji} What this means:",
                    "value": what_this_means,
                    "inline": False
                }
            ],
            "footer": {
                "text": "Real-time Alert - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_api_failure_alert(self, failure_duration_minutes: int, consecutive_failures: int) -> bool:
        """Send alert when most recent API call fails (system offline/network disconnected)"""
        # Format duration nicely
        hrs = failure_duration_minutes // 60
        mins = failure_duration_minutes % 60
        duration_str = f"{hrs} hr {mins} min" if hrs > 0 else f"{mins} min"
        
        embed = {
            "title": "🚨 CRITICAL: Solar System NOT RESPONDING",
            "description": "**Your solar system API has FAILED to return data!**",
            "color": 10038562,  # Dark red color
            "fields": [
                {
                    "name": "⚠️ API Failure Detected",
                    "value": f"**Consecutive Failures:** {consecutive_failures}\n**Duration:** {duration_str}\n**Last Successful Check:** {duration_str} ago\n**Status:** System OFFLINE or Network Disconnected",
                    "inline": False
                },
                {
                    "name": "🔍 What This Means",
                    "value": "The monitoring system cannot communicate with your inverter.\n\n**Possible reasons:**\n• System is completely powered off\n• WiFi/Network connection lost\n• Inverter in deep standby mode\n• Communication hardware failure\n• WatchPower server issues",
                    "inline": False
                },
                {
                    "name": "🔧 Immediate Action Required",
                    "value": "1. Check inverter display - Is it ON? ✅\n2. Check WiFi connection - Is inverter connected? ✅\n3. Check internet connectivity ✅\n4. Verify network cables and power ✅\n5. Open WatchPower app - Can you see live data? ✅\n6. Check inverter error codes/warnings ✅",
                    "inline": False
                },
                {
                    "name": "⏰ Reminder",
                    "value": "You'll receive hourly reminders until API connection resumes.",
                    "inline": False
                }
            ],
            "footer": {
                "text": "CRITICAL Alert - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_api_recovery_alert(self, total_failures: int) -> bool:
        """Send notification when API data resumes after failure"""
        embed = {
            "title": "✅ Solar System Back Online",
            "description": "**Your solar system API is now responding normally!**",
            "color": 5763719,  # Green color
            "fields": [
                {
                    "name": "🎉 Connection Restored",
                    "value": f"**API Status:** ONLINE ✅\n**Data Flow:** RESUMED ✅\n**Total Failures During Outage:** {total_failures}",
                    "inline": False
                },
                {
                    "name": "🔍 What Happened",
                    "value": "The monitoring system has successfully reconnected to your inverter.\nData collection and monitoring are now back to normal.\n\nSystem is operating normally again.",
                    "inline": False
                },
                {
                    "name": "💡 Next Steps",
                    "value": "• Monitor dashboard to verify all metrics are updating\n• Check if any settings were affected during offline period\n• Review missed data on DailyStats page\n\nNo further action needed - system is back online!",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Recovery Alert - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_test_message(self) -> bool:
        """Send test Discord message"""
        embed = {
            "title": "✅ Solar Dashboard Connected!",
            "description": "Your Discord notifications are now active! 🎉",
            "color": 5763719,  # Green color
            "fields": [
                {
                    "name": "You'll receive instant alerts for:",
                    "value": "🔌 Grid feeding status changes\n⚡ Load shedding detection\n🚨 System offline warnings\n☀️ Low production alerts\n🔄 System reset detection",
                    "inline": False
                },
                {
                    "name": "Reminder Interval",
                    "value": "Every 1 hour ⏰",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Test Message - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)


# Global Discord service instance
discord_service = DiscordService()


from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordService:
    """Discord notification service using Discord Webhooks (100% FREE)"""
    
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        
        if not self.webhook_url:
            logger.warning("Discord webhook not configured. Discord notifications will be disabled.")
        else:
            logger.info("Discord service initialized successfully")
    
    def send_message(self, content: str, embed: dict = None) -> bool:
        """Send Discord message via webhook"""
        try:
            if not self.webhook_url:
                logger.error("Discord webhook not configured")
                return False
            
            payload = {}
            
            if embed:
                payload["embeds"] = [embed]
            else:
                payload["content"] = content
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                logger.info("Discord message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Discord message: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send Discord message: {str(e)}")
            return False
    
    def send_grid_feed_disabled_alert(self) -> bool:
        """Send Discord embed when grid feeding is disabled"""
        embed = {
            "title": "🚨 URGENT: Solar System Alert",
            "description": "**Grid Feeding: JUST DISABLED** 🔴\n\nYour solar system is no longer feeding excess power to the grid.",
            "color": 15158332,  # Red color
            "fields": [
                {
                    "name": "⚠️ Impact",
                    "value": "• Excess solar energy will be wasted\n• No revenue from grid export\n• Reduced system efficiency",
                    "inline": False
                },
                {
                    "name": "💡 Action Required",
                    "value": "Open WatchPower app and enable grid feeding immediately!",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Solar Dashboard - Immediate Alert"
            },
            "timestamp": None
        }
        
        return self.send_message(None, embed)
    
    def send_grid_feed_reminder(self) -> bool:
        """Send Discord reminder for disabled grid feeding"""
        embed = {
            "title": "⚠️ Solar System Reminder",
            "description": "**Grid Feeding: STILL DISABLED**\n\nYour system is not feeding power to the grid.",
            "color": 16753920,  # Orange color
            "fields": [
                {
                    "name": "💡 Recommended Action",
                    "value": "Enable grid feeding in WatchPower app to maximize ROI.",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Hourly Reminder - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_load_shedding_alert(self, voltage: float) -> bool:
        """Send Discord when load shedding is detected"""
        embed = {
            "title": "⚡ URGENT: Load Shedding Alert",
            "description": "**Grid Power: DISCONNECTED** 🔴",
            "color": 15158332,  # Red color
            "fields": [
                {
                    "name": "📊 Grid Voltage",
                    "value": f"{voltage}V (Below normal)",
                    "inline": True
                },
                {
                    "name": "Status",
                    "value": "✅ Solar system handling load\n⚠️ Monitor for extended outages",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Solar Dashboard - Critical Alert"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_system_offline_alert(self, minutes: int) -> bool:
        """Send Discord when system goes offline"""
        embed = {
            "title": "🚨 CRITICAL: System Offline",
            "description": "**Solar System: NOT RESPONDING** ❌",
            "color": 10038562,  # Dark red color
            "fields": [
                {
                    "name": "⏱️ Last Seen",
                    "value": f"{minutes} minutes ago",
                    "inline": True
                },
                {
                    "name": "🔧 Check immediately",
                    "value": "• Inverter power status\n• WiFi/network connection\n• Error codes on display\n• System breakers/fuses",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Solar Dashboard - Critical Alert"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_system_reset_alert(self, output_priority: str) -> bool:
        """Send Discord when inverter Output Priority has changed from normal value"""
        
        embed = {
            "title": "🚨 CRITICAL: Inverter Reset Detected!",
            "description": "**Inverter Settings Have Been Reset** ⚠️\n\nThis typically happens after a power cut or PV surge.",
            "color": 15158332,  # Red color
            "fields": [
                {
                    "name": "📋 Detected Changes",
                    "value": f"• Output Priority changed to '{output_priority}' (expected: 'Solar Utility Bat')",
                    "inline": False
                },
                {
                    "name": "💡 Action Required",
                    "value": "1. Open WatchPower app immediately\n2. Restore your preferred settings:\n   - Set Output Priority back to 'Solar Utility Bat'\n   - Disable LCD Auto Return if enabled\n   - Enable Grid Feeding if it was disabled",
                    "inline": False
                },
                {
                    "name": "⚠️ Note",
                    "value": "System may not be operating optimally until settings are restored!",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Solar Dashboard - System Reset Alert"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_daily_summary(self, summary_data: dict) -> bool:
        """Send daily summary via Discord"""
        date = summary_data.get("date", "Unknown")
        production_kwh = summary_data.get("production_kwh", 0)
        load_kwh = summary_data.get("load_kwh", 0)
        grid_contribution_kwh = summary_data.get("grid_contribution_kwh", 0)
        load_shedding_hours = summary_data.get("load_shedding_hours", 0)
        system_off_hours = summary_data.get("system_off_hours", 0)
        missing_data_hours = summary_data.get("missing_data_hours", 0)
        
        embed = {
            "title": f"📊 Daily Solar Summary - {date}",
            "description": "Your daily solar system performance report",
            "color": 3447003,  # Blue color
            "fields": [
                {
                    "name": "☀️ Solar Production",
                    "value": f"**{production_kwh} kWh**",
                    "inline": True
                },
                {
                    "name": "⚡ Energy Usage",
                    "value": f"**{load_kwh} kWh**",
                    "inline": True
                },
                {
                    "name": "🔋 Grid Contribution",
                    "value": f"**{grid_contribution_kwh} kWh**",
                    "inline": True
                },
                {
                    "name": "🔌 Load Shedding",
                    "value": f"Battery/Solar Runtime: **{load_shedding_hours}**",
                    "inline": False
                },
                {
                    "name": "⏸️ System Off Time",
                    "value": f"Total: **{system_off_hours}**\n• Standby Mode: {summary_data.get('standby_hours', 0)}\n• Missing Data: {missing_data_hours}",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"Solar Dashboard - Generated at {summary_data.get('timestamp', 'Unknown')}"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_mode_alert(self, mode: str, message_text: str, timestamp: str) -> bool:
        """Send alert when system mode changes"""
        if mode == "Battery Mode":
            emoji = "🔋"
            urgency = "WARNING"
            color = 15158332  # Red
        elif mode == "Line Mode":
            emoji = "⚡"
            urgency = "INFO"
            color = 5763719  # Green
        elif mode == "Standby Mode":
            emoji = "⏸️"
            urgency = "ALERT"
            color = 16753920  # Orange
        else:
            emoji = "ℹ️"
            urgency = "NOTICE"
            color = 7506394  # Gray
        
        # Build description based on mode
        what_this_means = ""
        if mode == "Battery Mode":
            what_this_means = "⚡ Electricity is disconnected\n🔋 System running on battery power\n⚠️ Load shedding detected\n💡 Your backup system is protecting your home\n\n**Action:** Monitor battery levels and wait for grid restoration."
        elif mode == "Line Mode":
            what_this_means = "✅ Electricity has been restored\n⚡ Grid power is now active\n🔋 Batteries will start recharging\n💡 System back to normal operation\n\n**Action:** No action needed - System operating normally."
        elif mode == "Standby Mode":
            what_this_means = "⏸️ System in standby mode\n🔴 Power is off\n⚠️ No power generation or consumption\n💡 System may need attention\n\n**Action:** Check your solar system and inverter status."
        
        embed = {
            "title": f"{emoji} {urgency}: Solar System Mode Changed",
            "description": f"**Status:** {mode}\n**Message:** {message_text}\n**Time:** {timestamp}",
            "color": color,
            "fields": [
                {
                    "name": f"{emoji} What this means:",
                    "value": what_this_means,
                    "inline": False
                }
            ],
            "footer": {
                "text": "Real-time Alert - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_api_failure_alert(self, failure_duration_minutes: int, consecutive_failures: int) -> bool:
        """Send alert when most recent API call fails (system offline/network disconnected)"""
        # Format duration nicely
        hrs = failure_duration_minutes // 60
        mins = failure_duration_minutes % 60
        duration_str = f"{hrs} hr {mins} min" if hrs > 0 else f"{mins} min"
        
        embed = {
            "title": "🚨 CRITICAL: Solar System NOT RESPONDING",
            "description": "**Your solar system API has FAILED to return data!**",
            "color": 10038562,  # Dark red color
            "fields": [
                {
                    "name": "⚠️ API Failure Detected",
                    "value": f"**Consecutive Failures:** {consecutive_failures}\n**Duration:** {duration_str}\n**Last Successful Check:** {duration_str} ago\n**Status:** System OFFLINE or Network Disconnected",
                    "inline": False
                },
                {
                    "name": "🔍 What This Means",
                    "value": "The monitoring system cannot communicate with your inverter.\n\n**Possible reasons:**\n• System is completely powered off\n• WiFi/Network connection lost\n• Inverter in deep standby mode\n• Communication hardware failure\n• WatchPower server issues",
                    "inline": False
                },
                {
                    "name": "🔧 Immediate Action Required",
                    "value": "1. Check inverter display - Is it ON? ✅\n2. Check WiFi connection - Is inverter connected? ✅\n3. Check internet connectivity ✅\n4. Verify network cables and power ✅\n5. Open WatchPower app - Can you see live data? ✅\n6. Check inverter error codes/warnings ✅",
                    "inline": False
                },
                {
                    "name": "⏰ Reminder",
                    "value": "You'll receive hourly reminders until API connection resumes.",
                    "inline": False
                }
            ],
            "footer": {
                "text": "CRITICAL Alert - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_api_recovery_alert(self, total_failures: int) -> bool:
        """Send notification when API data resumes after failure"""
        embed = {
            "title": "✅ Solar System Back Online",
            "description": "**Your solar system API is now responding normally!**",
            "color": 5763719,  # Green color
            "fields": [
                {
                    "name": "🎉 Connection Restored",
                    "value": f"**API Status:** ONLINE ✅\n**Data Flow:** RESUMED ✅\n**Total Failures During Outage:** {total_failures}",
                    "inline": False
                },
                {
                    "name": "🔍 What Happened",
                    "value": "The monitoring system has successfully reconnected to your inverter.\nData collection and monitoring are now back to normal.\n\nSystem is operating normally again.",
                    "inline": False
                },
                {
                    "name": "💡 Next Steps",
                    "value": "• Monitor dashboard to verify all metrics are updating\n• Check if any settings were affected during offline period\n• Review missed data on DailyStats page\n\nNo further action needed - system is back online!",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Recovery Alert - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)
    
    def send_test_message(self) -> bool:
        """Send test Discord message"""
        embed = {
            "title": "✅ Solar Dashboard Connected!",
            "description": "Your Discord notifications are now active! 🎉",
            "color": 5763719,  # Green color
            "fields": [
                {
                    "name": "You'll receive instant alerts for:",
                    "value": "🔌 Grid feeding status changes\n⚡ Load shedding detection\n🚨 System offline warnings\n☀️ Low production alerts\n🔄 System reset detection",
                    "inline": False
                },
                {
                    "name": "Reminder Interval",
                    "value": "Every 1 hour ⏰",
                    "inline": False
                }
            ],
            "footer": {
                "text": "Test Message - Solar Dashboard"
            }
        }
        
        return self.send_message(None, embed)


# Global Discord service instance
discord_service = DiscordService()

