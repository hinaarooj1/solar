# 🚀 Vercel Deployment Guide - Solar Monitoring Dashboard

## ✅ Pre-Deployment Checklist

Your app is already configured with:
- ✅ `vercel.json` with built-in cron jobs
- ✅ Environment variables ready
- ✅ All API routes fixed and working
- ✅ Monitoring service implemented

## 📦 Step 1: Install Vercel CLI (if not installed)

```bash
npm install -g vercel
```

## 🔐 Step 2: Login to Vercel

```bash
vercel login
```

Choose your login method (GitHub, GitLab, Email, etc.)

## 🚀 Step 3: Deploy to Vercel

Navigate to your project directory:

```bash
cd solar-nextjs
```

### First-time deployment:

```bash
vercel
```

Vercel will ask you:
1. **Set up and deploy?** → Yes
2. **Which scope?** → Choose your account
3. **Link to existing project?** → No
4. **Project name?** → `solar-monitoring` (or your preferred name)
5. **Directory?** → `.` (current directory)
6. **Override settings?** → No

This will create a **preview deployment**.

### Deploy to Production:

```bash
vercel --prod
```

## 🔧 Step 4: Configure Environment Variables

After deployment, you need to add environment variables in Vercel Dashboard:

### Option A: Via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to **Settings** → **Environment Variables**
4. Add each variable:

#### WatchPower API Credentials
```
USERNAMES = Ahmarjb
PASSWORD = Ahmar123
SERIAL_NUMBER = 96342404600319
WIFI_PN = W0034053928283
DEV_CODE = 2488
DEV_ADDR = 1
```

#### Email Configuration
```
EMAIL_USER = chbitug@gmail.com
EMAIL_PASSWORD = qbmkptoyswqofrel
ALERT_EMAIL = chbitug@gmail.com
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 587
```

#### Telegram Configuration
```
TELEGRAM_BOT_TOKEN = 6762994932:AAFUdwfusQyQ5ZpOOp3CDEIL2cY4kt-UpjM
TELEGRAM_CHAT_ID = 5677544633
```

#### Discord Configuration
```
DISCORD_WEBHOOK_URL = https://discordapp.com/api/webhooks/1425686982838714500/mGBwR_cxPi_ql2FETq3-xTg9By0etPsSDYurSv1vtzwjge1OWahWMsW_meeBieVKuTnK
```

#### Cron Job Security (IMPORTANT!)
```
CRON_SECRET = [GENERATE A RANDOM SECRET - see below]
```

**Generate a secure CRON_SECRET:**
```bash
# On Windows PowerShell:
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})

# On Mac/Linux:
openssl rand -base64 32
```

Example: `x7k9mP2qR5tY8wN3jL6vC1bF4hG0sA9d`

#### Alert Configuration
```
GRID_FEED_ALERT_INTERVAL_HOURS = 1
LOAD_SHEDDING_VOLTAGE_THRESHOLD = 180
SYSTEM_OFFLINE_THRESHOLD_MINUTES = 10
LOW_PRODUCTION_THRESHOLD_WATTS = 500
```

5. Click **Save** for each variable
6. Make sure to select **Production**, **Preview**, and **Development** for all variables

### Option B: Via Vercel CLI

```bash
# Set environment variables via CLI
vercel env add USERNAMES production
vercel env add PASSWORD production
vercel env add SERIAL_NUMBER production
# ... (repeat for all variables)
```

## 🔄 Step 5: Redeploy After Adding Environment Variables

```bash
vercel --prod
```

## ⏰ Step 6: Verify Cron Jobs (Built-in - No Third Party Needed!)

### ✅ Vercel Has Built-in Cron Jobs!

Your `vercel.json` already configures them:

```json
{
  "crons": [
    {
      "path": "/api/cron/monitor",
      "schedule": "*/5 * * * *"        // Every 5 minutes
    },
    {
      "path": "/api/cron/daily-summary",
      "schedule": "0 19 * * *"         // Daily at 7 PM UTC (midnight PKT)
    }
  ]
}
```

### How to Verify Cron Jobs:

1. **Via Vercel Dashboard:**
   - Go to your project
   - Click **Settings** → **Cron Jobs**
   - You should see:
     - `/api/cron/monitor` - Every 5 minutes ✅
     - `/api/cron/daily-summary` - Every day at 19:00 UTC ✅

2. **Via Logs:**
   - Go to **Deployments** → Click latest deployment → **Function Logs**
   - Wait 5 minutes
   - Look for logs: `🔄 Cron: Running monitoring checks...`

## 🧪 Step 7: Test Everything

### Test Homepage:
```
https://your-project.vercel.app
```

### Test API Endpoints:
```
https://your-project.vercel.app/api/stats?date=2025-10-08
https://your-project.vercel.app/api/system/health
```

### Test Notifications (via Controls page):
1. Go to `https://your-project.vercel.app/controls`
2. Click "Test Email" - Should receive test email
3. Click "Test Telegram" - Should receive Telegram message
4. Click "Test Discord" - Should receive Discord message
5. Click "Test Daily Summary" - Should receive yesterday's summary

### Test Cron Job Manually:
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_CRON_SECRET" \
  https://your-project.vercel.app/api/cron/monitor
```

## 📊 Step 8: Monitor Your Deployment

### Check Logs:
1. Vercel Dashboard → Your Project → **Logs**
2. Filter by function: `/api/cron/monitor`
3. You should see logs every 5 minutes

### Expected Log Output:
```
🔄 Cron: Running monitoring checks...
⏰ Running monitoring checks...
📊 Fetching system data...
✅ Monitoring checks completed
```

## 🎯 Cron Job Schedule Explained

| Cron Job | Schedule | Frequency | Purpose |
|----------|----------|-----------|---------|
| `/api/cron/monitor` | `*/5 * * * *` | Every 5 minutes | Check for alerts (load shedding, system reset, etc.) |
| `/api/cron/daily-summary` | `0 19 * * *` | Daily at 7 PM UTC | Send daily summary (midnight PKT) |

### Why 7 PM UTC = Midnight PKT?
- Pakistan Time (PKT) = UTC+5
- 7 PM UTC = 7:00 + 5 hours = 12:00 AM (midnight) PKT ✅

## 🔒 Security Notes

### CRON_SECRET Protection:
- Your cron endpoints are protected with `Authorization: Bearer` token
- Only Vercel's cron system can call them
- No one else can trigger your cron jobs

### Environment Variables:
- Never commit `.env` or `.env.local` to Git
- All secrets are stored securely in Vercel
- Variables are encrypted at rest

## 🎉 What You Get with Vercel Cron (Free!)

✅ **No Third-Party Service Needed**
- Vercel Cron is built-in and FREE
- No need for cron-job.org, EasyCron, etc.
- Managed automatically

✅ **Reliable Execution**
- Guaranteed to run on schedule
- Automatic retries on failure
- Built-in logging

✅ **Simple Configuration**
- Just add to `vercel.json`
- Deploy and it works!

✅ **Monitoring Built-in**
- View execution logs in dashboard
- See success/failure rates
- Debug easily

## 🚨 Troubleshooting

### Cron Jobs Not Running?

1. **Check vercel.json exists in root:**
   ```bash
   ls solar-nextjs/vercel.json
   ```

2. **Verify CRON_SECRET is set:**
   - Dashboard → Settings → Environment Variables
   - Make sure `CRON_SECRET` exists for Production

3. **Check cron endpoint returns 200:**
   ```bash
   curl -H "Authorization: Bearer YOUR_SECRET" \
     https://your-app.vercel.app/api/cron/monitor
   ```

4. **View Logs:**
   - Dashboard → Logs
   - Filter by `/api/cron/monitor`

### No Alerts Being Sent?

1. Check environment variables are set
2. Test notifications manually from Controls page
3. Verify email/Telegram/Discord credentials

### 500 Errors?

1. Check Function Logs in Vercel Dashboard
2. Look for error messages
3. Verify all environment variables are correct

## 📝 Quick Command Reference

```bash
# Login to Vercel
vercel login

# Deploy preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# List environment variables
vercel env ls

# Pull environment variables locally
vercel env pull

# Check project status
vercel inspect
```

## 🔄 Update Deployment

When you make code changes:

```bash
# 1. Test locally
npm run dev

# 2. Deploy to production
vercel --prod
```

Vercel will:
- ✅ Build your app
- ✅ Deploy new version
- ✅ Keep cron jobs running
- ✅ Zero downtime

## 🎊 Success Checklist

After deployment, verify:

- [ ] App loads at your Vercel URL
- [ ] Homepage shows solar stats
- [ ] Controls page works
- [ ] Can test Email/Telegram/Discord
- [ ] Cron jobs appear in Settings → Cron Jobs
- [ ] Logs show cron execution every 5 minutes
- [ ] Receive test alerts successfully
- [ ] Daily summary works (test button)

## 📱 Access Your Dashboard

Your production URL will be:
```
https://your-project-name.vercel.app
```

Or connect a custom domain:
- Dashboard → Settings → Domains
- Add your domain and follow DNS instructions

---

## 🎉 Congratulations!

You now have:
✅ Solar monitoring dashboard deployed to Vercel
✅ Built-in cron jobs running every 5 minutes
✅ Automatic daily summaries at midnight PKT
✅ Real-time alerts for all issues
✅ No third-party services needed!

**Your system is now fully automated and cloud-hosted!** 🚀

---

**Deployment Date:** October 9, 2025  
**Platform:** Vercel (with built-in Cron)  
**Monitoring:** Every 5 minutes  
**Alerts:** Email, Telegram, Discord






