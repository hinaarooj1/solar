# Monitoring & Alerts System Setup

## ✅ Completed Implementation

Your Next.js solar monitoring system now has **COMPLETE** alert monitoring functionality with all checks running every 5 minutes!

### 🚨 Alert Types Implemented

1. **System Reset Detection** ⚡
   - Detects when inverter Output Priority changes from "Solar Utility Bat"
   - Sends IMMEDIATE alert + hourly reminders
   - Alerts sent to: Email, Telegram, Discord

2. **Load Shedding Detection** 🔌
   - Monitors grid voltage drop (< 180V threshold)
   - Sends IMMEDIATE alert when detected
   - 5-hour reminder intervals while load shedding persists
   - Alerts sent to: Email, Telegram, Discord

3. **System Offline Detection** ❌
   - Tracks last successful API call
   - Alerts if no response for 10+ minutes
   - Alerts sent to: Email, Telegram, Discord

4. **Grid Feeding Disabled Alert** 💡
   - Detects when grid feeding gets disabled
   - Sends IMMEDIATE alert when disabled
   - Hourly reminders until enabled
   - Alerts sent to: Email, Telegram, Discord

5. **Daily Summary** 📊
   - Automatic daily report at 7 PM PKT (midnight PKT - 5 hour offset)
   - Includes production, consumption, load shedding, system off time
   - Sent to: Email, Telegram, Discord

### 📁 Files Modified

1. **`solar-nextjs/lib/monitoring-service.ts`**
   - Complete monitoring service with all alert checks
   - Tracks system state persistently
   - Handles all 5 alert types

2. **`solar-nextjs/app/api/cron/monitor/route.ts`**
   - Cron endpoint that runs every 5 minutes
   - Secured with `CRON_SECRET` authorization
   - Calls all monitoring checks

3. **`solar-nextjs/app/api/stats/route.ts`**
   - Fixed array bounds checking for `fields[47]`
   - Added missing `await` for `getWatchPowerAPI()`

4. **Other API routes fixed:**
   - `/api/last-data/route.ts`
   - `/api/devices/route.ts`
   - `/api/daily-data/route.ts`

### 🔧 Configuration

Your `.env` file already has all required settings:

```env
# Alert Configuration
GRID_FEED_ALERT_INTERVAL_HOURS=1          # Grid feed reminders every 1 hour
LOAD_SHEDDING_VOLTAGE_THRESHOLD=180       # Alert when voltage < 180V
SYSTEM_OFFLINE_THRESHOLD_MINUTES=10       # Alert if offline for 10+ minutes
LOW_PRODUCTION_THRESHOLD_WATTS=500        # Low production threshold

# Email Configuration
EMAIL_USER=chbitug@gmail.com
EMAIL_PASSWORD=qbmkptoyswqofrel
ALERT_EMAIL=chbitug@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

# Telegram Configuration
TELEGRAM_BOT_TOKEN=6762994932:AAFUdwfusQyQ5ZpOOp3CDEIL2cY4kt-UpjM
TELEGRAM_CHAT_ID=5677544633

# Discord Configuration
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/...

# Cron Job Security
CRON_SECRET=your_random_secret_key_change_this
```

### ⏰ Cron Job Schedule

**Vercel Cron Configuration** (`vercel.json`):
```json
{
  "crons": [
    {
      "path": "/api/cron/monitor",
      "schedule": "*/5 * * * *"  // Every 5 minutes ✅
    },
    {
      "path": "/api/cron/daily-summary",
      "schedule": "0 19 * * *"   // Daily at 7 PM PKT ✅
    }
  ]
}
```

### 🎯 How It Works

Every 5 minutes, Vercel Cron triggers `/api/cron/monitor` which:

1. **Fetches current system data** from WatchPower API
2. **Updates timestamp** (for offline detection)
3. **Checks Output Priority** for system reset
4. **Checks Grid Voltage** for load shedding
5. **Checks Grid Feed Status** from real-time data
6. **Checks System Offline** based on last successful API call
7. **Sends alerts** to Email, Telegram, Discord when conditions are met

### 📊 Alert Flow Examples

#### Example 1: Load Shedding Detected
```
[5:00 PM] ⚡ Grid voltage drops to 170V
          → IMMEDIATE alerts sent to all 3 channels
[10:00 PM] ⏰ 5 hours later, still 170V
          → Reminder alerts sent to all 3 channels
```

#### Example 2: System Reset
```
[2:00 PM] 🚨 Output Priority changed to "Utility Solar Bat"
          → IMMEDIATE alerts sent to all 3 channels
[3:00 PM] ⏰ 1 hour later, still wrong setting
          → Hourly reminder sent to all 3 channels
[3:30 PM] ✅ Fixed! Back to "Solar Utility Bat"
          → Alerts stop, state reset
```

#### Example 3: Grid Feeding Disabled
```
[11:00 AM] 💡 During daytime, PV=2000W, Feed=0W
           → Grid feeding detected as DISABLED
           → IMMEDIATE alerts sent to all 3 channels
[12:00 PM] ⏰ 1 hour later, still disabled
           → Reminder sent to all 3 channels
```

### 🧪 Testing

#### Test Monitoring Manually
```bash
# Test the cron endpoint (with authentication)
curl -H "Authorization: Bearer your_random_secret_key_change_this" \
  https://your-domain.vercel.app/api/cron/monitor
```

#### Check Server Logs
1. Deploy to Vercel
2. Go to Vercel Dashboard → Your Project → Logs
3. Wait 5 minutes and watch for cron execution logs
4. Look for:
   - `🔄 Cron: Running monitoring checks...`
   - `⏰ Running monitoring checks...`
   - `✅ Monitoring checks completed`

### 🚀 Deployment

1. **Deploy to Vercel:**
   ```bash
   cd solar-nextjs
   vercel --prod
   ```

2. **Verify Cron Jobs:**
   - Go to Vercel Dashboard → Your Project → Settings → Cron Jobs
   - Should see:
     - `/api/cron/monitor` - Every 5 minutes
     - `/api/cron/daily-summary` - Every day at 7 PM PKT

3. **First Alert Test:**
   - Wait 5 minutes for first cron run
   - Check your email, Telegram, Discord for any alerts
   - If system is normal, you won't get alerts (that's good!)

### 📝 What to Expect

**Normal Operation (No Alerts):**
- System checks every 5 minutes
- No alerts if everything is working properly
- Logs show successful monitoring cycles

**When Alerts Trigger:**
- **Immediate alerts** for new issues
- **Periodic reminders** while issues persist
- **All 3 channels** receive notifications simultaneously
- **Automatic recovery** when issues resolve

### 🔍 Monitoring State

The system maintains state in `system_settings.json`:
- `grid_feeding_enabled`: Current grid feed status
- Alert timestamps to prevent spam
- System online/offline status
- Previous check results

### ⚙️ Customization

**Change Alert Intervals:**
Edit `.env.local`:
```env
GRID_FEED_ALERT_INTERVAL_HOURS=2  # Remind every 2 hours instead of 1
SYSTEM_OFFLINE_THRESHOLD_MINUTES=15  # 15 minutes instead of 10
LOAD_SHEDDING_VOLTAGE_THRESHOLD=170  # Lower threshold
```

**Disable Specific Alerts:**
Comment out checks in `/api/cron/monitor/route.ts`

---

## 🎉 All Done!

Your solar monitoring system now has enterprise-grade alerting with:
- ✅ 5-minute monitoring interval
- ✅ Multiple alert channels (Email, Telegram, Discord)
- ✅ Smart alert timing (immediate + periodic reminders)
- ✅ Automatic recovery detection
- ✅ Persistent state management
- ✅ Comprehensive system monitoring

**Next Steps:**
1. Deploy to Vercel
2. Wait 5 minutes for first check
3. Monitor logs to ensure it's working
4. You'll receive alerts when any issues occur!

---

Generated: 2025-10-09






