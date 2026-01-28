# 🚨 Automatic Mode Alert System - Setup & Usage Guide

## 🎯 What This Does

Your solar system now has **24/7 automatic monitoring** that sends instant alerts to Email, Telegram, and Discord when:

- ⚡ **Electricity Disconnects** (Battery Mode)
- ✅ **Electricity Restores** (Line Mode)  
- ⏸️ **System Goes to Standby** (Power Off)

**No manual action needed!** The system monitors itself every 5 minutes.

---

## 🚀 Quick Start

### 1. **Backend is Ready**
All code is already implemented. Just restart your backend:

```bash
cd backend/watchpower-api-main
python fastapi_app.py
```

### 2. **Monitoring Service Starts Automatically**
You'll see in the logs:
```
🔄 Starting monitoring service...
⏰ Running periodic monitoring checks...
📊 Fetching system data...
✅ Periodic check: System Mode = 'Line Mode'
✅ Periodic check: Grid Voltage = 230.0V
✅ Periodic monitoring cycle completed successfully
⏳ Waiting 5 minutes for next check...
```

### 3. **Wait for Alerts**
When electricity cuts:
```
🔄 System mode changed: Line Mode → Battery Mode
🔋 WARNING: Electricity Disconnected - Running on Battery Power!
✅ Mode change alert sent via Email: Battery Mode
✅ Mode change alert sent via Telegram: Battery Mode
✅ Mode change alert sent via Discord: Battery Mode
```

---

## 📧 Configure Notification Channels

### Email (Required)
In your `.env` file:
```env
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
ALERT_EMAIL=recipient@example.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
```

### Telegram (Optional - 100% FREE)
1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
```

### Discord (Optional - 100% FREE)
1. Create a webhook in your Discord channel
2. Add to `.env`:
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

---

## 📱 What You'll Receive

### Email Example:
```
Subject: 🔋 WARNING: Solar System Mode Changed - Battery Mode

Solar System Mode Change Alert

Status: Battery Mode 🔴
Message: Electricity Disconnected - Running on Battery Power!
Time: 2025-10-11 14:30:00

━━━━━━━━━━━━━━━━━━

Mode Details:
🔋 Battery Mode

What this means:

⚡ Electricity is disconnected
🔋 System running on battery power
⚠️ Load shedding detected
💡 Your backup system is protecting your home

Action: Monitor battery levels and wait for grid restoration.

━━━━━━━━━━━━━━━━━━
Real-time Alert - Solar Dashboard
Monitoring your solar system 24/7
```

### Telegram Example:
```
🔋 WARNING: Solar System Mode Changed

Status: Battery Mode 🔴
Message: Electricity Disconnected - Running on Battery Power!
Time: 2025-10-11 14:30:00

━━━━━━━━━━━━━━━━━━

Mode Details:
🔋 Battery Mode

What this means:

⚡ Electricity is disconnected
🔋 System running on battery power
⚠️ Load shedding detected
💡 Your backup system is protecting your home

Action: Monitor battery levels and wait for grid restoration.
```

### Discord Example:
Rich embed with:
- 🔴 Red color for Battery Mode
- 🟢 Green color for Line Mode
- 🟠 Orange color for Standby Mode
- Structured fields with mode details
- Action recommendations

---

## 🔍 Monitoring Dashboard

### System Controls Page Shows:

#### When Electricity is Connected (Line Mode):
```
✅ Health Score: 95
🟢 Electricity Connected - Grid Power Active

Grid Voltage: 230V
System Mode: Line Mode ⚡ Connected to Grid
```

#### When Electricity is Disconnected (Battery Mode):
```
⚠️ Health Score: 75
🔴 Electricity Disconnected - Running on Battery Power

Grid Voltage: Not Available (red text)
System Mode: Battery Mode 🔋 Running on Battery
```

#### When System is Off (Standby Mode):
```
⚠️ Health Score: 50
🟠 System in Standby Mode - Power Off

Grid Voltage: Not Available (red text)
System Mode: Standby Mode ⏸️ System Off
```

---

## 🕒 Monitoring Schedule

### Every 5 Minutes:
1. Fetch current system data
2. Check system mode
3. Compare with previous mode
4. **IF CHANGED:** Send alerts to all channels
5. Check grid voltage
6. Check output priority  
7. Check for other issues
8. Wait 5 minutes
9. Repeat

### Daily at 12:00 AM PKT:
- Sends daily summary to all channels

---

## 🛠️ Troubleshooting

### No Alerts Received?

**Check Backend Logs:**
```bash
# Should see every 5 minutes:
✅ Periodic check: System Mode = 'Line Mode'
```

**When Mode Changes:**
```bash
# Should see:
🔄 System mode changed: Line Mode → Battery Mode
✅ Mode change alert sent via Email: Battery Mode
✅ Mode change alert sent via Telegram: Battery Mode
✅ Mode change alert sent via Discord: Battery Mode
```

**If You See Errors:**
```bash
# Email error:
❌ Email service error: ...
# Check EMAIL_USER, EMAIL_PASSWORD, ALERT_EMAIL in .env

# Telegram error:
❌ Telegram service error: ...
# Check TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID in .env

# Discord error:
❌ Discord service error: ...
# Check DISCORD_WEBHOOK_URL in .env
```

### Grid Voltage Shows "Not Available"?

This is **normal** when:
- Electricity is disconnected (Battery Mode)
- System is in Standby
- `utility_ac_voltage` is 0 or null

The backend logs will show:
```
⚠️ Grid voltage data not available (voltage: 0.0V)
```

This prevents false load shedding alerts.

---

## ✨ Benefits

### Automatic:
- ✅ No manual refresh needed
- ✅ Works 24/7 in background
- ✅ Instant notifications

### Multi-Channel:
- ✅ Email (always works)
- ✅ Telegram (instant mobile notifications)
- ✅ Discord (team notifications)

### Smart:
- ✅ Only alerts on actual changes
- ✅ Different urgency levels
- ✅ Detailed explanations
- ✅ Action recommendations

### Reliable:
- ✅ Error handling for each channel
- ✅ One failure doesn't affect others
- ✅ All errors logged
- ✅ Service keeps running

---

## 🎉 You're All Set!

Just restart your backend and the automatic monitoring will begin!

When electricity cuts or restores, you'll get instant notifications on all configured channels.

**Check your backend logs to see it working!** 📊



