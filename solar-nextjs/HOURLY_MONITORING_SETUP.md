# ⏰ Hourly Monitoring Setup (FREE)

## 🎯 Perfect Balance: Hourly Checks

**Why Hourly is Great:**
- ✅ Still catches issues quickly (within 1 hour)
- ✅ Less load on free cron services
- ✅ 100% FREE with cron-job.org
- ✅ More reliable than 5-minute checks
- ✅ Still sends instant alerts when issues occur

---

## 📋 Quick Setup: Hourly Monitoring

### Step 1: Update vercel.json (Already Done!)

Your `vercel.json` now only has the daily summary cron:
```json
{
  "crons": [
    {
      "path": "/api/cron/daily-summary",
      "schedule": "0 19 * * *"
    }
  ]
}
```

### Step 2: Deploy to Vercel

```bash
vercel --prod
```

### Step 3: Set Up Free Cron Service

#### Option A: cron-job.org (Recommended - 100% FREE)

1. **Sign up:** https://cron-job.org/en/signup/
2. **Create Cronjob:**

**Settings:**
```
Title: Solar Monitoring - Hourly Alert Check
URL: https://YOUR-VERCEL-URL.vercel.app/api/cron/monitor
Schedule: 0 * * * *  (Every hour, at minute 0)
Request Method: GET
```

**HTTP Headers:**
```
Authorization: Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM
```

**Notifications:**
- ✅ Enable "Notify me on failures"

3. **Click "Create Cronjob"**
4. **Test:** Click "Run now" to verify it works!

---

#### Option B: UptimeRobot (Also FREE + Bonus Features!)

**Why UptimeRobot is Great:**
- ✅ Also monitors if your site goes down
- ✅ FREE plan: 50 monitors
- ✅ Can check every 5 minutes (but we'll use hourly)
- ✅ Email/SMS/Slack alerts

**Setup:**
1. Sign up: https://uptimerobot.com/
2. Add New Monitor:
   ```
   Monitor Type: HTTP(s)
   Friendly Name: Solar Monitoring Hourly Check
   URL: https://your-vercel-url.vercel.app/api/cron/monitor
   Monitoring Interval: 60 minutes (or 5 if you want)
   Alert Contacts: Your email
   ```
3. **Advanced Settings** → **Custom HTTP Headers:**
   ```
   Authorization: Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM
   ```
4. Save Monitor!

**Bonus:** UptimeRobot will also alert you if your entire Vercel site goes down!

---

## 🕐 Cron Schedule Comparison

| Frequency | Cron Expression | Times/Day | Detection Time | Recommendation |
|-----------|----------------|-----------|----------------|----------------|
| **Every 5 min** | `*/5 * * * *` | 288 | ~5 min | ⚠️ Overkill, high load |
| **Every 15 min** | `*/15 * * * *` | 96 | ~15 min | ✅ Good balance |
| **Every 30 min** | `*/30 * * * *` | 48 | ~30 min | ✅ Good balance |
| **Hourly** | `0 * * * *` | 24 | ~1 hour | ⭐ **RECOMMENDED** |
| **Every 2 hours** | `0 */2 * * *` | 12 | ~2 hours | ⚠️ Too slow for alerts |
| **Daily** | `0 19 * * *` | 1 | ~24 hours | ❌ Too slow |

---

## 🎯 What You Get with Hourly Monitoring

### Your Complete Setup:

**1. Hourly Alert Checks (via external cron)**
- ⏰ Runs every hour
- 🚨 Checks for:
  - Load shedding (voltage drops)
  - System offline (no API response)
  - System reset (inverter settings changed)
  - Grid feeding disabled
- 📧 Sends alerts to Email, Telegram, Discord
- 🔄 Repeats alerts if issues persist

**2. Daily Summary (via Vercel cron)**
- ⏰ Runs at midnight PKT (7 PM UTC)
- 📊 Yesterday's complete stats
- 📧 Sent to Email, Telegram, Discord

---

## 📊 Alert Timing Examples

### With Hourly Checks:

**Scenario 1: Load Shedding**
```
11:00 AM - Load shedding starts (voltage drops)
12:00 PM - ✅ Alert sent! (detected within 1 hour)
5:00 PM  - ⏰ 5-hour reminder (still in load shedding)
```

**Scenario 2: System Offline**
```
2:30 PM - System goes offline
3:00 PM - ✅ Alert sent! (detected within 30 min)
```

**Scenario 3: Grid Feeding Disabled**
```
10:30 AM - Grid feeding gets disabled
11:00 AM - ✅ Alert sent! (detected within 30 min)
12:00 PM - ⏰ Hourly reminder
1:00 PM  - ⏰ Hourly reminder
```

---

## 🆚 5-Minute vs Hourly Comparison

| Aspect | Every 5 Min | Hourly |
|--------|-------------|--------|
| **Detection Time** | ~5 minutes | ~30 minutes average |
| **Load on Services** | High (288 requests/day) | Low (24 requests/day) |
| **Reliability** | May fail due to rate limits | Very reliable |
| **Cost** | FREE (but risky) | 100% FREE & stable |
| **Battery Usage** | Higher server load | Minimal |
| **Real Benefit** | Not much faster | ⭐ Perfect balance |

**Verdict:** Hourly is **better** for most cases because:
- Issues don't need instant detection (1 hour is fine for alerts)
- Much more reliable
- Lower load = fewer failures
- Still catches all problems quickly

---

## 🔧 Environment Variables Reminder

Make sure these are set in **Vercel Dashboard** → **Settings** → **Environment Variables**:

```
# Your CRON_SECRET (KEEP PRIVATE!)
CRON_SECRET = JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM

# WatchPower Credentials
USERNAMES = Ahmarjb
PASSWORD = Ahmar123
SERIAL_NUMBER = 96342404600319
WIFI_PN = W0034053928283
DEV_CODE = 2488
DEV_ADDR = 1

# Email Config
EMAIL_USER = chbitug@gmail.com
EMAIL_PASSWORD = qbmkptoyswqofrel
ALERT_EMAIL = chbitug@gmail.com
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587

# Telegram Config
TELEGRAM_BOT_TOKEN = 6762994932:AAFUdwfusQyQ5ZpOOp3CDEIL2cY4kt-UpjM
TELEGRAM_CHAT_ID = 5677544633

# Discord Config
DISCORD_WEBHOOK_URL = https://discordapp.com/api/webhooks/...

# Alert Configuration
GRID_FEED_ALERT_INTERVAL_HOURS = 1
LOAD_SHEDDING_VOLTAGE_THRESHOLD = 180
SYSTEM_OFFLINE_THRESHOLD_MINUTES = 10
LOW_PRODUCTION_THRESHOLD_WATTS = 500
```

---

## 🧪 Testing Your Setup

### 1. Test Manually (PowerShell):
```powershell
$headers = @{
    "Authorization" = "Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM"
}
Invoke-WebRequest -Uri "https://your-vercel-url.vercel.app/api/cron/monitor" -Headers $headers -Method GET
```

### 2. Test via cron-job.org:
- Click "Run now" on your cron job
- Check execution log (should show HTTP 200)

### 3. Check Vercel Logs:
- Dashboard → Logs → Filter by `/api/cron/monitor`
- Should see: `✅ Monitoring checks completed`

### 4. Test Alerts from Controls Page:
- Go to `/controls`
- Click test buttons for Email/Telegram/Discord
- Verify you receive notifications

---

## 🎊 Final Setup Summary

### Your System Will:

✅ **Check every hour** for:
- Load shedding
- System offline
- System reset
- Grid feeding disabled

✅ **Send instant alerts** when issues detected

✅ **Send reminders** while issues persist:
- Load shedding: Every 5 hours
- System reset: Every hour
- Grid feeding disabled: Every hour

✅ **Send daily summary** at midnight PKT

✅ **Cost: $0/month** - Completely FREE!

---

## 🚀 Deployment Commands

```bash
# 1. Deploy to Vercel
cd solar-nextjs
vercel --prod

# 2. Get your deployment URL
# Example: https://solar-monitoring-abc123.vercel.app

# 3. Set up external cron at cron-job.org or UptimeRobot

# 4. Done! You're monitoring hourly! 🎉
```

---

## 💡 Pro Tips

1. **Start with Hourly** - It's the sweet spot
2. **Use UptimeRobot** - Get bonus uptime monitoring
3. **Monitor Logs** - Check Vercel logs occasionally
4. **Test Alerts** - Use Controls page to test notifications
5. **Check Email** - cron-job.org will email you on failures

---

**Updated:** October 9, 2025  
**Monitoring Frequency:** Hourly (24 times/day)  
**Cost:** $0/month (100% FREE)  
**CRON_SECRET:** `JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM`






