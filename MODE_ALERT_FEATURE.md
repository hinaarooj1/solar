# 🚨 Automatic Mode Alert Feature - Complete Implementation

## 🎯 Overview
**Fully Automatic** multi-channel alerts when solar system mode changes.

The monitoring service automatically checks system mode **every 5 minutes** and sends instant alerts to Email, Telegram, and Discord when it detects a mode change.

**No manual action required** - the system monitors itself 24/7!

---

## ✅ How It Works

### Automatic Monitoring Flow:

```
Every 5 Minutes (Automatic):
   ↓
Monitoring Service Fetches System Data
   ↓
Extracts: System Mode, Grid Voltage, Output Priority
   ↓
Compares Current Mode vs Previous Mode
   ↓
IF MODE CHANGED:
   ↓
Sends Multi-Channel Alerts:
   • 📧 Email
   • 📱 Telegram  
   • 💬 Discord
   ↓
Logs sent to backend
User receives notifications instantly!
```

---

## 📋 Backend Implementation

### 1. **Monitoring Service** (monitoring_service.py)

#### New State Variables:
```python
self.current_system_mode = None
self.previous_system_mode = None
```

#### New Method: `check_system_mode_change()`
```python
async def check_system_mode_change(self, current_mode: str):
    """
    Check if system mode has changed and send multi-channel alerts
    Monitors: Line Mode, Battery Mode, Standby Mode
    """
```

**Features:**
- Compares current mode with previous mode
- Sends alerts when mode changes
- Sends to all 3 channels (Email, Telegram, Discord)
- Error handling for each channel (doesn't crash if one fails)
- Logs all activities

#### Updated Method: `get_current_system_data()`
Now also extracts:
```python
system_mode = str(fields[47])  # Extract from field 47
```

Returns:
```python
{
    "output_priority": "Solar Utility Bat",
    "grid_voltage": 230.0,
    "system_mode": "Line Mode"  # ← NEW
}
```

#### Updated Method: `run_periodic_checks()`
Added automatic mode checking:
```python
# Check for system mode changes
system_mode = system_data.get("system_mode", "Unknown")
if system_mode != "Unknown":
    await self.check_system_mode_change(system_mode)
    logger.info(f"✅ System Mode = '{system_mode}'")
```

---

### 2. **Email Service** (email_service.py)

#### New Method: `send_mode_alert()`
```python
def send_mode_alert(self, mode: str, message: str, timestamp: str) -> bool
```

**Email Examples:**

**Subject:** `🔋 WARNING: Solar System Mode Changed - Battery Mode`

**Body:**
```
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

---

### 3. **Telegram Service** (telegram_service.py)

#### New Method: `send_mode_alert()`
```python
def send_mode_alert(self, mode: str, message_text: str, timestamp: str) -> bool
```

Sends formatted Markdown message with:
- Mode emoji and color indicator
- Detailed explanation
- Action items

---

### 4. **Discord Service** (discord_service.py)

#### New Method: `send_mode_alert()`
```python
def send_mode_alert(self, mode: str, message_text: str, timestamp: str) -> bool
```

Sends rich Discord embed with:
- Color-coded embeds (Red/Green/Orange)
- Structured fields
- Action recommendations

---

### 5. **API Models** (api_models.py)

#### New Model: `ModeAlertRequest`
```python
class ModeAlertRequest(BaseModel):
    mode: Literal["Battery Mode", "Line Mode", "Standby Mode"]
    message: str
    timestamp: datetime
```

---

### 6. **FastAPI Endpoint** (fastapi_app.py)

#### New Endpoint: `POST /notifications/mode-alert`
```python
@app.post("/notifications/mode-alert")
async def send_mode_alert_endpoint(request: ModeAlertRequest)
```

**Purpose:** Manual trigger endpoint (optional - not used in automatic monitoring)

---

## 🖥️ Frontend Implementation

### SystemControls.js

#### Visual Indicators Only:

1. **Grid Voltage Display:**
   - Shows "Not Available" (red) when voltage is 0 or null
   - Prevents backend warning about missing voltage data

2. **Mode Status Alerts:**
   - 🟢 Green Alert (Line Mode): "⚡ Electricity Connected"
   - 🔴 Red Alert (Battery Mode): "🔋 Electricity Disconnected"  
   - 🟠 Orange Alert (Standby Mode): "⏸️ System in Standby Mode"

3. **Color-Coded Health Score Box:**
   - Background and border change based on current mode

4. **Enhanced System Mode Section:**
   - Dynamic colors (green/red/orange)
   - Mode-specific icons and descriptions

**No manual detection** - Just displays current state from backend!

---

## 🔔 Alert Scenarios

### Scenario 1: Electricity Cut (Line Mode → Battery Mode)
```
14:25:00 - Monitoring service runs (5-min check)
14:25:01 - Detects mode: Battery Mode (was: Line Mode)
14:25:02 - Sends Email: "🔋 WARNING: Electricity Disconnected"
14:25:03 - Sends Telegram: "⚡ URGENT: Load Shedding Alert"
14:25:04 - Sends Discord: Rich embed with red color
14:25:05 - User receives all 3 notifications instantly!
```

### Scenario 2: Electricity Restored (Battery Mode → Line Mode)
```
15:10:00 - Monitoring service runs (5-min check)
15:10:01 - Detects mode: Line Mode (was: Battery Mode)
15:10:02 - Sends Email: "⚡ INFO: Electricity Restored"
15:10:03 - Sends Telegram: "✅ Grid Power Connected"
15:10:04 - Sends Discord: Rich embed with green color
15:10:05 - User receives confirmation via all channels!
```

### Scenario 3: System Goes to Standby
```
23:50:00 - Monitoring service runs (5-min check)
23:50:01 - Detects mode: Standby Mode (was: Line Mode)
23:50:02 - Sends Email: "⏸️ ALERT: System in Standby Mode"
23:50:03 - Sends Telegram: "🔴 System Power Off"
23:50:04 - Sends Discord: Rich embed with orange color
23:50:05 - User alerted to check system!
```

---

## 📦 Files Modified

### Backend:
- ✅ `backend/watchpower-api-main/monitoring_service.py` ← **Main automatic logic here**
- ✅ `backend/watchpower-api-main/api_models.py`
- ✅ `backend/watchpower-api-main/email_service.py`
- ✅ `backend/watchpower-api-main/telegram_service.py`
- ✅ `backend/watchpower-api-main/discord_service.py`
- ✅ `backend/watchpower-api-main/fastapi_app.py`

### Frontend:
- ✅ `solarapp/src/pages/SystemControls.js` (display only)
- ✅ `solarapp/src/constants.js`

---

## 🚀 Deployment

### Just restart your backend:
```bash
cd backend/watchpower-api-main
python fastapi_app.py
```

The monitoring service will automatically start and check every 5 minutes!

---

## 📊 Monitoring Service Log Output

```
⏰ Running periodic monitoring checks...
📊 Fetching system data...
✅ Periodic check: System Mode = 'Line Mode'
✅ Periodic check: Output Priority = 'Solar Utility Bat'
✅ Periodic check: Grid Voltage = 230.0V
✅ Periodic monitoring cycle completed successfully
⏳ Waiting 5 minutes for next check...

[5 minutes later - electricity cuts]

⏰ Running periodic monitoring checks...
📊 Fetching system data...
🔄 System mode changed: Line Mode → Battery Mode
🔋 WARNING: Electricity Disconnected - Running on Battery Power!
✅ Mode change alert sent via Email: Battery Mode
✅ Mode change alert sent via Telegram: Battery Mode
✅ Mode change alert sent via Discord: Battery Mode
✅ Periodic check: System Mode = 'Battery Mode'
✅ Periodic monitoring cycle completed successfully
⏳ Waiting 5 minutes for next check...
```

---

## 🎯 Key Features

### Automatic Detection:
- ✅ Runs every 5 minutes automatically
- ✅ No manual refresh needed
- ✅ Works 24/7 in background
- ✅ Monitors mode changes continuously

### Multi-Channel Alerts:
- ✅ Email with detailed explanation
- ✅ Telegram with Markdown formatting
- ✅ Discord with rich colored embeds

### Robust Error Handling:
- ✅ Each channel has try-catch
- ✅ One channel failure doesn't affect others
- ✅ All errors logged
- ✅ Service keeps running even if alerts fail

### Smart Notifications:
- ✅ Only sends on mode **change** (not every check)
- ✅ Different messages for different transitions
- ✅ Special message when electricity restores from battery mode
- ✅ Urgency levels (INFO, WARNING, ALERT)

---

## 🔧 Testing

### 1. Check Logs:
```bash
# Backend logs will show:
✅ Periodic check: System Mode = 'Line Mode'
```

### 2. Wait for Mode Change:
When electricity cuts or restores, you'll see:
```bash
🔄 System mode changed: Line Mode → Battery Mode
✅ Mode change alert sent via Email: Battery Mode
✅ Mode change alert sent via Telegram: Battery Mode
✅ Mode change alert sent via Discord: Battery Mode
```

### 3. Check Your Channels:
You'll receive instant notifications on:
- 📧 Email inbox
- 📱 Telegram app
- 💬 Discord channel

---

## 💡 Additional Features

### Grid Voltage Handling:
- Shows "Not Available" in UI when voltage is 0/null
- Backend logs warning instead of error
- Prevents false load shedding alerts

### UI Visual Indicators:
- Real-time mode display with colored alerts
- Health score box changes color based on mode
- System mode section shows current status

---

## 🎉 Summary

The system now **automatically monitors** and **instantly alerts** you about:

1. ⚡ **Electricity Disconnected** (Battery Mode)
   - Email, Telegram, Discord alerts sent
   - UI shows red warning

2. ✅ **Electricity Restored** (Line Mode)
   - Email, Telegram, Discord confirmations sent
   - UI shows green success

3. ⏸️ **System Off** (Standby Mode)
   - Email, Telegram, Discord alerts sent
   - UI shows orange warning

**All automatic - No manual intervention needed!**

---

## 📞 Support

If you don't receive alerts, check:
1. Backend logs for errors
2. Email/Telegram/Discord credentials in `.env`
3. Monitoring service is running
4. Check spam folder (for emails)
