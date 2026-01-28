# ⏰ 10-Minute Monitoring Setup (Perfect Balance!)

## 🎯 Why 10 Minutes is Great:
- ✅ Catches issues quickly (~10 min detection time)
- ✅ Less load than 5-min (144 checks/day vs 288)
- ✅ More responsive than hourly
- ✅ 100% FREE with any cron service
- ✅ Perfect balance of speed and reliability

---

## 🚀 Quick Setup (2 Steps):

### Step 1: Deploy to Vercel

Your `vercel.json` is already configured (daily summary only):
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

Deploy now:
```bash
vercel --prod
```

---

### Step 2: Set Up External Cron (10-Minute Interval)

Choose one of these FREE services:

---

## 🌟 **Option A: UptimeRobot** (RECOMMENDED)

**Why UptimeRobot:**
- ✅ 100% FREE
- ✅ Super reliable
- ✅ Can do 5-minute intervals (but we'll use 10)
- ✅ **BONUS:** Monitors if your site goes down
- ✅ Beautiful dashboard

### Setup Steps:

1. **Sign up FREE:** https://uptimerobot.com/

2. **Add New Monitor:**
   - Click **"+ Add New Monitor"**

3. **Configure Monitor:**
   ```
   Monitor Type: HTTP(s)
   Friendly Name: Solar Monitoring - 10 Min Checks
   URL (or IP): https://YOUR-VERCEL-URL.vercel.app/api/cron/monitor
   Monitoring Interval: 5 minutes
   ```
   
   **Note:** UptimeRobot's free plan offers 5-minute checks minimum. This is actually better than 10! But if you want to reduce load, you can:
   - Use 5 minutes (144 checks/day) ⭐ Recommended
   - Or upgrade to paid for custom intervals

4. **Advanced Settings** → **Custom HTTP Headers:**
   - Click "Add HTTP Header"
   - **Header Name:** `Authorization`
   - **Header Value:** `Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM`

5. **Alert Contacts:**
   - Add your email
   - Get notified if monitoring fails

6. **Save Monitor** ✅

---

## 🔧 **Option B: cron-job.org** (True 10-Minute Intervals)

**Perfect if you want exactly 10 minutes:**

1. **Sign up FREE:** https://cron-job.org/en/signup/

2. **Create Cronjob:**
   - Click **"Create Cronjob"**

3. **Configure:**
   ```
   Title: Solar Monitoring - 10 Min
   URL: https://YOUR-VERCEL-URL.vercel.app/api/cron/monitor
   Schedule: */10 * * * *  ← Every 10 minutes!
   Request Method: GET
   ```

4. **HTTP Headers:**
   - Click **"Add Header"**
   - **Header Name:** `Authorization`
   - **Header Value:** `Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM`

5. **Notifications:**
   - ✅ Enable "Notify me on failures"
   - Add your email

6. **Save** and **Test** (click "Run now")

---

## 📊 Monitoring Schedule Comparison

| Service | Interval | Checks/Day | Free Plan | Bonus Features |
|---------|----------|------------|-----------|----------------|
| **UptimeRobot** | 5 min | 288 | ✅ 50 monitors | Site uptime monitoring |
| **cron-job.org** | 10 min (custom) | 144 | ✅ Unlimited | Email on failures |
| **EasyCron** | 10 min | 144 | ✅ 100/month | Execution history |

**My Recommendation:** Use **UptimeRobot** with 5-minute checks - it's actually better and still free!

---

## 🎯 What You'll Get:

### **Monitoring Checks** (Every 5-10 minutes)
- 🚨 Load shedding detection (voltage < 180V)
- 🚨 System offline detection (no API response)
- 🚨 System reset detection (settings changed)
- 🚨 Grid feeding disabled detection

### **Alert Examples:**

**Scenario 1: Load Shedding**
```
2:35 PM - Load shedding starts (voltage drops to 170V)
2:40 PM - ✅ Alert sent! (detected in 5 min)
7:40 PM - ⏰ Reminder sent (5 hours later)
```

**Scenario 2: System Offline**
```
11:23 AM - System goes offline
11:30 AM - ✅ Alert sent! (detected in 7 min)
```

---

## 🔒 Environment Variables Checklist

Make sure these are set in **Vercel Dashboard** → **Settings** → **Environment Variables**:

```
# Security
CRON_SECRET = JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM

# WatchPower API
USERNAMES = Ahmarjb
PASSWORD = Ahmar123
SERIAL_NUMBER = 96342404600319
WIFI_PN = W0034053928283
DEV_CODE = 2488
DEV_ADDR = 1

# Email
EMAIL_USER = chbitug@gmail.com
EMAIL_PASSWORD = qbmkptoyswqofrel
ALERT_EMAIL = chbitug@gmail.com
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587

# Telegram
TELEGRAM_BOT_TOKEN = 6762994932:AAFUdwfusQyQ5ZpOOp3CDEIL2cY4kt-UpjM
TELEGRAM_CHAT_ID = 5677544633

# Discord
DISCORD_WEBHOOK_URL = https://discordapp.com/api/webhooks/...

# Alert Config
GRID_FEED_ALERT_INTERVAL_HOURS = 1
LOAD_SHEDDING_VOLTAGE_THRESHOLD = 180
SYSTEM_OFFLINE_THRESHOLD_MINUTES = 10
LOW_PRODUCTION_THRESHOLD_WATTS = 500
```

---

## 🧪 Testing Your Setup

### 1. Test Endpoint Manually:

**PowerShell:**
```powershell
$headers = @{
    "Authorization" = "Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM"
}
Invoke-WebRequest -Uri "https://your-vercel-url.vercel.app/api/cron/monitor" -Headers $headers
```

Expected response: `"success": true`

### 2. Test from UptimeRobot/cron-job.org:
- Click "Run now" or "Test"
- Check execution log shows HTTP 200

### 3. Verify Alerts Work:
- Go to `https://your-vercel-url.vercel.app/controls`
- Click test buttons for Email/Telegram/Discord
- You should receive test notifications

---

## 📈 Performance Comparison

| Interval | Detection Time | Checks/Day | Server Load | Reliability |
|----------|----------------|------------|-------------|-------------|
| 5 min | ~2-3 min avg | 288 | Higher | Very High |
| **10 min** | **~5 min avg** | **144** | **Low** | **⭐ Best Balance** |
| 15 min | ~7-8 min avg | 96 | Very Low | High |
| 30 min | ~15 min avg | 48 | Minimal | Medium |
| Hourly | ~30 min avg | 24 | Minimal | Medium |

**10 minutes = Perfect sweet spot!** ⭐

---

## 🎊 Final Architecture

```
┌──────────────────────────────────────────┐
│  Vercel (Your Solar Dashboard)           │
│  - Next.js app hosted                    │
│  - API: /api/cron/monitor ready          │
│  - Daily summary cron: Midnight PKT      │
└──────────────────────────────────────────┘
                ↑
                │ HTTP GET every 10 min
                │ Authorization: Bearer {secret}
                │
┌──────────────────────────────────────────┐
│  UptimeRobot / cron-job.org (FREE)       │
│  - Pings endpoint every 10 minutes       │
│  - Triggers monitoring checks            │
│  - Emails you if endpoint fails          │
└──────────────────────────────────────────┘
                ↓
        Monitoring checks run
        Alerts sent to Email/Telegram/Discord
```

---

## ✅ Deployment Checklist

- [ ] Deploy to Vercel: `vercel --prod`
- [ ] Get your Vercel URL
- [ ] Set all environment variables in Vercel Dashboard
- [ ] Sign up for UptimeRobot or cron-job.org
- [ ] Create monitor with 10-min interval (or 5-min with UptimeRobot)
- [ ] Add Authorization header with CRON_SECRET
- [ ] Test the monitor (click "Run now")
- [ ] Verify Vercel logs show monitoring execution
- [ ] Test alerts from Controls page
- [ ] Done! You're monitoring every 10 minutes! 🎉

---

## 💡 Pro Tips

1. **Use UptimeRobot** - Get 5-min checks + site monitoring for FREE
2. **Set up email alerts** - Get notified if cron job fails
3. **Check logs regularly** - Vercel Dashboard → Logs
4. **Test notifications** - Use Controls page weekly
5. **Monitor uptime** - UptimeRobot shows your site's uptime %

---

## 🎉 What You Get (100% FREE!)

✅ **Every 5-10 minutes:** Check for all issues  
✅ **Instant alerts:** When problems detected  
✅ **Daily summary:** At midnight PKT  
✅ **Three channels:** Email, Telegram, Discord  
✅ **Site monitoring:** Bonus with UptimeRobot  
✅ **Cost:** $0/month forever!

---

**Created:** October 9, 2025  
**Monitoring Frequency:** Every 10 minutes (144 checks/day)  
**Cost:** $0/month  
**CRON_SECRET:** `JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM` (KEEP PRIVATE!)






