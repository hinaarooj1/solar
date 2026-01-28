import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailService:
    """Email notification service using SMTP"""
    
    def __init__(self):
        # Support both old and new environment variable names for compatibility
        self.sender_email = os.getenv("EMAIL_USER") or os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.recipient_email = os.getenv("ALERT_EMAIL") or os.getenv("EMAIL_RECIPIENT")
        self.smtp_server = os.getenv("EMAIL_HOST") or os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_PORT") or os.getenv("SMTP_PORT", 587))
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            missing = []
            if not self.sender_email: missing.append("EMAIL_USER/EMAIL_SENDER")
            if not self.sender_password: missing.append("EMAIL_PASSWORD")
            if not self.recipient_email: missing.append("ALERT_EMAIL/EMAIL_RECIPIENT")
            logger.warning(f"Email configuration incomplete. Missing: {', '.join(missing)}. Email notifications will be disabled.")
        else:
            logger.info(f"✅ Email service initialized successfully (from: {self.sender_email}, to: {self.recipient_email})")
    
    def send_email(
        self,
        subject: str,
        body: str,
        *,
        is_html: bool = False,
        recipient_email: Optional[str] = None,
    ) -> bool:
        """Send email"""
        try:
            actual_recipient = recipient_email or self.recipient_email
            if not all([self.sender_email, self.sender_password, actual_recipient]):
                logger.error("Email not configured")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = actual_recipient
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {actual_recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_grid_feed_disabled_alert(self, recipient_email: Optional[str] = None) -> bool:
        """Send email when grid feeding is disabled"""
        subject = "🚨 URGENT: Solar Grid Feeding DISABLED"
        body = """
URGENT: Solar System Alert

Grid Feeding: JUST DISABLED 🔴

Your solar system is no longer feeding excess power to the grid.

⚠️ Impact:
• Excess solar energy will be wasted
• No revenue from grid export
• Reduced system efficiency

💡 Action Required:
Open WatchPower app and enable grid feeding immediately!

━━━━━━━━━━━━━━━━━━
Solar Dashboard - Immediate Alert
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_grid_feed_reminder(self, recipient_email: Optional[str] = None) -> bool:
        """Send email reminder for disabled grid feeding"""
        subject = "⚠️ Solar System Reminder - Grid Feeding Still Disabled"
        body = """
Solar System Reminder

Grid Feeding: STILL DISABLED

Your system is not feeding power to the grid.

💡 Recommended Action:
Enable grid feeding in WatchPower app to maximize ROI.

━━━━━━━━━━━━━━━━━━
Hourly Reminder - Solar Dashboard
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_load_shedding_alert(
        self,
        voltage: float,
        duration_minutes: int,
        recipient_email: Optional[str] = None,
    ) -> bool:
        """Send email when load shedding is detected"""
        subject = "⚡ URGENT: Load Shedding Alert"
        body = f"""
URGENT: Load Shedding Alert

Grid Power: DISCONNECTED 🔴

📊 Grid Voltage: {voltage}V (Below normal)

✅ Your solar system is handling the load
⚠️ Monitor for extended outages

━━━━━━━━━━━━━━━━━━
Solar Dashboard - Critical Alert
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_system_shutdown_alert(
        self,
        last_seen_minutes: int,
        recipient_email: Optional[str] = None,
    ) -> bool:
        """Send email when system goes offline"""
        subject = "🚨 CRITICAL: Solar System Offline"
        body = f"""
CRITICAL: System Offline

Solar System: NOT RESPONDING ❌

⏱️ Last seen: {last_seen_minutes} minutes ago

🔧 Check immediately:
• Inverter power status
• WiFi/network connection
• Error codes on display
• System breakers/fuses

━━━━━━━━━━━━━━━━━━
Solar Dashboard - Critical Alert
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_low_production_alert(
        self,
        current_production: float,
        expected_min: float,
        time_range: str,
        recipient_email: Optional[str] = None,
    ) -> bool:
        """Send email for low production warning"""
        subject = "⚠️ Solar System - Low Production Warning"
        body = f"""
Solar System Warning

Low Production During Peak Hours

📊 Current Production: {current_production}W
📊 Expected Minimum: {expected_min}W
⏰ Time Range: {time_range}

🔧 Possible causes:
• Panel shading or obstruction
• Dust/dirt on panels
• System malfunction

💡 Recommended Action:
Check panels and system status

━━━━━━━━━━━━━━━━━━
Solar Dashboard - Production Alert
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_system_reset_alert(
        self,
        output_priority: str,
        recipient_email: Optional[str] = None,
    ) -> bool:
        """Send email when inverter Output Priority has changed from normal value"""
        
        subject = "🚨 CRITICAL: Inverter Settings Reset Detected!"
        body = f"""
CRITICAL: Inverter Reset Detected!

Inverter Settings Have Been Reset ⚠️

This typically happens after a power cut or PV surge.

📋 Detected Changes:
• Output Priority changed to '{output_priority}' (expected: 'Solar Utility Bat')

💡 Action Required:
1. Open WatchPower app immediately
2. Restore your preferred settings:
   - Set Output Priority back to 'Solar Utility Bat'
   - Disable LCD Auto Return if enabled
   - Enable Grid Feeding if it was disabled

⚠️ Note: System may not be operating optimally until settings are restored!

━━━━━━━━━━━━━━━━━━
Solar Dashboard - System Reset Alert
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_daily_summary(
        self,
        summary_data: dict,
        recipient_email: Optional[str] = None,
    ) -> bool:
        """Send daily summary email"""
        date = summary_data.get("date", "Unknown")
        production_kwh = summary_data.get("production_kwh", 0)
        load_kwh = summary_data.get("load_kwh", 0)
        grid_contribution_kwh = summary_data.get("grid_contribution_kwh", 0)
        load_shedding_hours = summary_data.get("load_shedding_hours", 0)
        system_off_hours = summary_data.get("system_off_hours", 0)
        missing_data_hours = summary_data.get("missing_data_hours", 0)
        
        subject = f"📊 Daily Solar Summary - {date}"
        body = f"""
Daily Solar Summary for {date}

☀️ SOLAR PRODUCTION
━━━━━━━━━━━━━━━━━━━━━━━━
Total Production: {production_kwh} kWh

⚡ ENERGY USAGE
━━━━━━━━━━━━━━━━━━━━━━━━
Total Consumption: {load_kwh} kWh

🔋 GRID CONTRIBUTION
━━━━━━━━━━━━━━━━━━━━━━━━
Energy Fed to Grid: {grid_contribution_kwh} kWh

🔌 LOAD SHEDDING
━━━━━━━━━━━━━━━━━━━━━━━━
Battery/Solar Runtime: {load_shedding_hours}

⏸️ SYSTEM OFF TIME
━━━━━━━━━━━━━━━━━━━━━━━━
Total Off Duration: {system_off_hours}
  • Standby Mode: {summary_data.get("standby_hours", 0)}
  • Missing Data: {missing_data_hours}

━━━━━━━━━━━━━━━━━━━━━━━━
Solar Dashboard - Daily Summary
Generated at {summary_data.get("timestamp", "Unknown")}
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_mode_alert(
        self,
        mode: str,
        message: str,
        timestamp: str,
        recipient_email: Optional[str] = None,
    ) -> bool:
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
        
        subject = f"{emoji} {urgency}: Solar System Mode Changed - {mode}"
        body = f"""
Solar System Mode Change Alert

Status: {mode} {color_indicator}
Message: {message}
Time: {timestamp}

━━━━━━━━━━━━━━━━━━

Mode Details:
{emoji} {mode}

{message}

What this means:
"""
        
        if mode == "Battery Mode":
            body += """
⚡ Electricity is disconnected
🔋 System running on battery power
⚠️ Load shedding detected
💡 Your backup system is protecting your home

Action: Monitor battery levels and wait for grid restoration.
"""
        elif mode == "Line Mode":
            body += """
✅ Electricity has been restored
⚡ Grid power is now active
🔋 Batteries will start recharging
💡 System back to normal operation

Action: No action needed - System operating normally.
"""
        elif mode == "Standby Mode":
            body += """
⏸️ System in standby mode
🔴 Power is off
⚠️ No power generation or consumption
💡 System may need attention

Action: Check your solar system and inverter status.
"""
        
        body += """

━━━━━━━━━━━━━━━━━━
Real-time Alert - Solar Dashboard
Monitoring your solar system 24/7
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_api_failure_alert(
        self,
        failure_duration_minutes: int,
        consecutive_failures: int,
        recipient_email: Optional[str] = None,
    ) -> bool:
        """Send alert when most recent API call fails (system offline/network disconnected)"""
        # Format duration nicely
        hrs = failure_duration_minutes // 60
        mins = failure_duration_minutes % 60
        duration_str = f"{hrs} hr {mins} min" if hrs > 0 else f"{mins} min"
        
        subject = f"🚨 CRITICAL: Solar System API Failure - No Data for {duration_str}"
        
        body = f"""
🚨 CRITICAL: Solar System NOT RESPONDING

Your solar system API has FAILED to return data!

━━━━━━━━━━━━━━━━━━

⚠️ API FAILURE DETECTED:
• Consecutive Failures: {consecutive_failures}
• Duration: {duration_str}
• Last Successful Check: {duration_str} ago
• Status: System OFFLINE or Network Disconnected

━━━━━━━━━━━━━━━━━━

🔍 WHAT THIS MEANS:

The monitoring system cannot communicate with your inverter.

Possible reasons:
• System is completely powered off
• WiFi/Network connection lost
• Inverter in deep standby mode
• Communication hardware failure
• WatchPower server issues

━━━━━━━━━━━━━━━━━━

🔧 IMMEDIATE ACTION REQUIRED:

1. Check inverter display - Is it ON? ✅
2. Check WiFi connection - Is inverter connected? ✅
3. Check internet connectivity ✅
4. Verify network cables and power ✅
5. Open WatchPower app - Can you see live data? ✅
6. Check inverter error codes/warnings ✅

⏰ You'll receive hourly reminders until API connection resumes.

━━━━━━━━━━━━━━━━━━
CRITICAL Alert - Solar Dashboard
Real-time Monitoring Active
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_api_recovery_alert(
        self,
        total_failures: int,
        recipient_email: Optional[str] = None,
    ) -> bool:
        """Send notification when API data resumes after failure"""
        subject = "✅ Solar System Back Online - API Connection Restored"
        
        body = f"""
✅ RESOLVED: Solar System Connection Restored

Your solar system API is now responding normally!

━━━━━━━━━━━━━━━━━━

🎉 CONNECTION RESTORED:
• API Status: ONLINE ✅
• Data Flow: RESUMED ✅
• Total Failures During Outage: {total_failures}

━━━━━━━━━━━━━━━━━━

🔍 WHAT HAPPENED:

The monitoring system has successfully reconnected to your inverter.
Data collection and monitoring are now back to normal.

System is operating normally again.

━━━━━━━━━━━━━━━━━━

💡 NEXT STEPS:

• Monitor dashboard to verify all metrics are updating
• Check if any settings were affected during offline period
• Review missed data on DailyStats page

No further action needed - system is back online!

━━━━━━━━━━━━━━━━━━
Recovery Alert - Solar Dashboard
Monitoring Resumed
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)
    
    def send_test_email(self, recipient_email: Optional[str] = None) -> bool:
        """Send test email"""
        subject = "✅ Solar Dashboard Connected!"
        body = """
Solar Dashboard Connected!

Your email notifications are now active! 🎉

You'll receive instant alerts for:
🔌 Grid feeding status changes
⚡ Load shedding detection
🚨 System offline warnings
☀️ Low production alerts
🔄 System reset detection

Reminder Interval: Every 1 hour ⏰

━━━━━━━━━━━━━━━━━━
Test Email - Solar Dashboard
        """.strip()
        
        return self.send_email(subject, body, recipient_email=recipient_email)


# Global email service instance
email_service = EmailService()
