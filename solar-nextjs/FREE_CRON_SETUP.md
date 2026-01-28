# 🆓 Free Cron Service Setup for Vercel Hobby Plan

## ⚠️ Vercel Hobby Plan Limitation

Vercel's **Hobby (free) plan** only supports:
- ✅ Daily cron jobs
- ❌ NOT 5-minute intervals

**Solution:** Use a **FREE third-party cron service** to trigger your monitoring endpoint!

---

## 🎯 Recommended Solution: cron-job.org (100% FREE)

### Why cron-job.org?
- ✅ **Completely FREE**
- ✅ Run jobs every 1, 5, or 15 minutes
- ✅ Unlimited jobs
- ✅ Reliable execution
- ✅ Email notifications on failure
- ✅ No credit card required

---

## 📋 Step-by-Step Setup

### Step 1: Deploy to Vercel (Daily Cron Only)

First, update `vercel.json` to only use daily cron:

**File: `vercel.json`**
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

Deploy to Vercel:
```bash
vercel --prod
```

Get your deployment URL (e.g., `https://solar-monitoring-abc123.vercel.app`)

---

### Step 2: Sign Up for cron-job.org

1. Go to https://cron-job.org/en/signup/
2. Sign up with your email (FREE account)
3. Verify your email
4. Login to dashboard

---

### Step 3: Create Monitoring Cron Job

1. **Click "Create Cronjob"**

2. **Configure the job:**

**Title:**
```
Solar Monitoring - Alert Check
```

**URL:**
```
https://YOUR-VERCEL-URL.vercel.app/api/cron/monitor
```

**Schedule:** 
- Select: **Every 5 minutes**
- Or custom: `*/5 * * * *`

**Request Method:**
- Select: **GET**

**HTTP Headers - IMPORTANT!**
Click "Add Header" and add:
```
Header Name: Authorization
Header Value: Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM
```
(Use the CRON_SECRET you generated)

**Notifications:**
- ✅ Enable "Notify me on failures"
- Add your email

3. **Click "Create Cronjob"** ✅

---

### Step 4: Test the Cron Job

1. In cron-job.org dashboard, find your job
2. Click "Run now" to test immediately
3. Check the execution log - should show "Success" (HTTP 200)
4. Check your Vercel logs - should see monitoring check executed

---

## 🎯 Alternative Free Cron Services

If cron-job.org doesn't work for you, try these:

### Option A: EasyCron (Free Plan)
- Website: https://www.easycron.com/
- Free: 100 tasks/month, 1-minute intervals
- Setup: Same as cron-job.org

### Option B: cron-job.org Alternative
- Website: https://console.cron-job.org/
- Completely free, unlimited jobs

### Option C: UptimeRobot (Monitor + Cron)
- Website: https://uptimerobot.com/
- Free: 50 monitors, 5-minute intervals
- **Bonus:** Also monitors if your site is down!

**Setup for UptimeRobot:**
1. Sign up free at https://uptimerobot.com/
2. Add New Monitor:
   - Monitor Type: **HTTP(s)**
   - Friendly Name: `Solar Monitoring Alert Check`
   - URL: `https://your-vercel-url.vercel.app/api/cron/monitor`
   - Monitoring Interval: **5 minutes**
   - Custom HTTP Headers:
     ```
     Authorization: Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM
     ```
3. Save and it will ping every 5 minutes!

---

## 📊 Final Configuration

### Vercel Cron (Daily)
```
✅ Daily Summary - Runs at 7 PM UTC (midnight PKT)
   Path: /api/cron/daily-summary
   Schedule: 0 19 * * *
```

### External Cron Service (5 minutes)
```
✅ Monitoring Alerts - Runs every 5 minutes
   URL: https://your-vercel-url.vercel.app/api/cron/monitor
   Schedule: */5 * * * *
   Authorization: Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM
```

---

## 🔒 Security Notes

### Your CRON_SECRET (KEEP THIS PRIVATE!)
```
JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM
```

**Important:**
- ✅ Add this to Vercel Environment Variables
- ✅ Use it in cron-job.org Authorization header
- ❌ Never commit to Git
- ❌ Never share publicly

### How It Works:
1. cron-job.org makes HTTP request every 5 minutes
2. Request includes `Authorization: Bearer YOUR_SECRET` header
3. Your API verifies the secret matches
4. If valid → runs monitoring checks
5. If invalid → returns 401 Unauthorized

---

## 🧪 Testing Your Setup

### Test the endpoint manually:

**Windows PowerShell:**
```powershell
$headers = @{
    "Authorization" = "Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM"
}
Invoke-WebRequest -Uri "https://your-vercel-url.vercel.app/api/cron/monitor" -Headers $headers -Method GET
```

**Or using curl (Git Bash/WSL):**
```bash
curl -X GET \
  -H "Authorization: Bearer JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM" \
  https://your-vercel-url.vercel.app/api/cron/monitor
```

Expected Response:
```json
{
  "success": true,
  "message": "Monitoring checks completed",
  "timestamp": "2025-10-09T..."
}
```

---

## 📈 What You Get (FREE!)

### With This Setup:
✅ **Every 5 minutes** - Monitoring checks via cron-job.org
✅ **Daily at midnight PKT** - Daily summary via Vercel
✅ **All alerts working** - Load shedding, system reset, grid feed, offline
✅ **100% FREE** - No paid plans needed
✅ **Reliable** - External service ensures uptime
✅ **Monitored** - Get notified if cron job fails

---

## 🎊 Cost Comparison

| Option | Cost | Features |
|--------|------|----------|
| **Vercel Hobby + cron-job.org** | $0/month | ✅ All features working |
| **Vercel Pro** | $20/month | ✅ Built-in 5-min cron |
| **Other platforms** | Varies | May have better free tiers |

**Recommendation:** Start with FREE option, upgrade later if needed!

---

## 🔧 Troubleshooting

### Cron job returns 401 Unauthorized:
- ❌ CRON_SECRET not set in Vercel environment variables
- ❌ Authorization header incorrect in cron-job.org
- ✅ Fix: Double-check secret matches exactly

### Cron job returns 500 Error:
- Check Vercel Function Logs
- Verify all environment variables are set
- Test endpoint manually

### Not receiving alerts:
- Check email/Telegram/Discord credentials
- Test notifications from Controls page
- Verify cron job is actually running (check execution log)

---

## 📝 Quick Setup Checklist

- [ ] Deploy to Vercel with updated `vercel.json` (daily cron only)
- [ ] Set all environment variables in Vercel Dashboard
- [ ] Add CRON_SECRET to Vercel env vars
- [ ] Sign up for cron-job.org (or alternative)
- [ ] Create cron job for monitoring endpoint
- [ ] Add Authorization header with CRON_SECRET
- [ ] Test the cron job
- [ ] Verify alerts are working
- [ ] Check Vercel logs after 5 minutes

---

## 🎉 You're All Set!

Your monitoring system will now:
- ✅ Check every 5 minutes via external cron service
- ✅ Send daily summary via Vercel cron
- ✅ Send instant alerts to all 3 channels
- ✅ Cost you $0/month

**Completely FREE and fully functional!** 🚀

---

**Last Updated:** October 9, 2025  
**CRON_SECRET:** `JBPy9kcYHhSUOj7L3KwDAXQlzm8eudsM` (KEEP PRIVATE!)






