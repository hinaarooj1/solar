# 🚀 Deployment Guide - Solar Monitoring Next.js

## Quick Deploy to Vercel (5 Minutes!)

### Method 1: Vercel CLI (Recommended)

```bash
# 1. Install Vercel CLI globally
npm install -g vercel

# 2. Navigate to project
cd solar-nextjs

# 3. Install dependencies
npm install

# 4. Login to Vercel
vercel login

# 5. Deploy to production
vercel --prod
```

Done! Your app is live! 🎉

### Method 2: GitHub + Vercel Dashboard

1. **Push to GitHub:**
   ```bash
   cd solar-nextjs
   git init
   git add .
   git commit -m "Initial commit - Solar monitoring Next.js"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Connect to Vercel:**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Git Repository"
   - Select your solar-nextjs repository
   - Click "Import"

3. **Configure & Deploy:**
   - Vercel will auto-detect Next.js
   - Click "Deploy"
   - Done!

## Environment Variables Setup

### Required Variables

After deployment, add these environment variables in Vercel dashboard:

1. Go to your project dashboard
2. Click **Settings** → **Environment Variables**
3. Add each variable:

```env
# WatchPower API Credentials
USERNAMES=Ahmarjb
PASSWORD=Ahmar123
SERIAL_NUMBER=96342404600319
WIFI_PN=W0034053928283
DEV_CODE=2488
DEV_ADDR=1

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
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/1425686982838714500/mGBwR_cxPi_ql2FETq3-xTg9By0etPsSDYurSv1vtzwjge1OWahWMsW_meeBieVKuTnK

# Cron Job Security (Generate a random secret)
CRON_SECRET=your-random-secret-key-here

# Alert Configuration
GRID_FEED_ALERT_INTERVAL_HOURS=1
LOAD_SHEDDING_VOLTAGE_THRESHOLD=180
SYSTEM_OFFLINE_THRESHOLD_MINUTES=10
LOW_PRODUCTION_THRESHOLD_WATTS=500
```

### Generate CRON_SECRET

```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Or use any random string:
my-super-secret-cron-key-12345
```

## Verify Deployment

### 1. Check Homepage
```
https://your-app.vercel.app
```
Should show the dashboard homepage

### 2. Test API Endpoints
```bash
# Test stats endpoint
curl https://your-app.vercel.app/api/stats

# Test health endpoint
curl https://your-app.vercel.app/api/health

# Test notifications
curl -X POST https://your-app.vercel.app/api/notifications/test

# Test daily summary
curl https://your-app.vercel.app/api/notifications/test-daily-summary
```

### 3. Verify Cron Jobs

In Vercel Dashboard:
1. Go to your project
2. Click **Deployments**
3. Click latest deployment
4. Click **Functions**
5. You should see:
   - `/api/cron/monitor` - Runs every 5 min
   - `/api/cron/daily-summary` - Runs at 7 PM UTC (midnight PKT)

### 4. Check Cron Job Logs

1. Go to Vercel Dashboard
2. Click your project
3. Click **Logs**
4. Filter by function: `/api/cron/monitor`
5. You should see logs every 5 minutes

## Post-Deployment Checklist

- [ ] Homepage loads successfully
- [ ] `/api/stats` returns data
- [ ] `/api/health` returns system health
- [ ] Test notifications work (email, telegram, discord)
- [ ] Cron job `/api/cron/monitor` appears in Functions
- [ ] Cron job `/api/cron/daily-summary` appears in Functions
- [ ] All environment variables are set
- [ ] CRON_SECRET is configured
- [ ] Monitoring logs appear in Vercel logs

## Monitoring Your Cron Jobs

### View Cron Execution Logs

```bash
# Install Vercel CLI
npm i -g vercel

# View logs (live)
vercel logs --follow

# View logs for specific function
vercel logs --follow /api/cron/monitor
```

### Expected Log Output

**Every 5 Minutes:**
```
🔄 Cron: Running monitoring checks...
✅ Cron: Monitoring checks completed
```

**Daily at Midnight PKT:**
```
🌙 Cron: Running daily summary...
📊 Sending daily summary for 2024-10-08
✅ Daily summary sent via Email
✅ Daily summary sent via Telegram
✅ Daily summary sent via Discord
✅ Cron: Daily summary sent for 2024-10-08
```

## Troubleshooting

### Cron Jobs Not Running

**Problem:** No logs appearing for cron jobs

**Solution:**
1. Verify `vercel.json` is in root directory
2. Check CRON_SECRET is set in environment variables
3. Redeploy: `vercel --prod`
4. Wait 5 minutes for first cron execution

### Environment Variables Not Working

**Problem:** API returns errors about missing credentials

**Solution:**
1. Double-check all variables are set in Vercel dashboard
2. Click **Redeploy** after adding variables
3. Check for typos in variable names (case-sensitive!)

### Notifications Not Sending

**Problem:** Test notifications return success but no message received

**Solution:**
1. Verify email/telegram/discord credentials
2. Check Gmail App Password (not regular password)
3. Test each service individually
4. Check Vercel function logs for errors

### API Timeout Errors

**Problem:** Functions timing out

**Solution:**
- Vercel free tier: 10s timeout (hobby: 60s)
- Optimize slow API calls
- Consider upgrading to Hobby plan ($20/mo) if needed

## Custom Domain (Optional)

### Add Your Own Domain

1. Go to Vercel Dashboard
2. Click **Settings** → **Domains**
3. Add your domain (e.g., `solar.yourdomain.com`)
4. Follow DNS configuration instructions
5. Done! Your app will be at your custom domain

## Updating Your App

### Deploy New Changes

```bash
# Make your changes
# ...

# Deploy
git add .
git commit -m "Update features"
git push

# If using Vercel CLI:
vercel --prod
```

Vercel automatically redeploys on git push if connected to GitHub!

## Rollback

### Rollback to Previous Version

1. Go to Vercel Dashboard
2. Click **Deployments**
3. Find the working deployment
4. Click **...** → **Promote to Production**

## Cost Estimate

### Vercel Free Tier
- ✅ 100GB bandwidth/month
- ✅ Unlimited API requests
- ✅ Cron jobs included
- ✅ 100 serverless function executions/day

**Your Usage Estimate:**
- Monitoring cron: 12 executions/hour × 24 hours = 288/day
- Daily summary: 1/day
- API calls from frontend: ~50/day
- **Total: ~340 executions/day**

**❌ Problem:** Free tier only allows 100 executions/day!

**✅ Solution:** Upgrade to Hobby plan ($20/month) for unlimited executions

**Or:** Reduce monitoring frequency:
- Change cron to every 10 minutes instead of 5
- Reduces to ~150 executions/day (still over limit)

**Recommendation:** Hobby plan is worth it for reliability!

## Comparison: Before vs After

| Feature | Python + Render | Next.js + Vercel |
|---------|----------------|------------------|
| **Cost** | FREE | $20/mo (Hobby) |
| **Cold Starts** | ❌ Yes | ✅ No |
| **CORS** | ❌ Issues | ✅ None |
| **Cron** | ❌ External | ✅ Built-in |
| **Reliability** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maintenance** | ❌ Two repos | ✅ One repo |
| **Deploy** | ❌ Complex | ✅ One command |

## Support

If you encounter issues:

1. **Check Vercel Logs**
   ```bash
   vercel logs --follow
   ```

2. **Check Environment Variables**
   - Vercel Dashboard → Settings → Environment Variables

3. **Verify Cron Schedule**
   - Check `vercel.json` configuration

4. **Test Endpoints Manually**
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

## Success! 🎉

If you see:
- ✅ Cron logs every 5 minutes
- ✅ Daily summary logs at midnight PKT
- ✅ Notifications arriving
- ✅ API endpoints working

**Your Next.js solar monitoring system is fully operational!**

---

**Deployment Time:** ~5 minutes
**Configuration Time:** ~10 minutes
**Total Setup:** ~15 minutes

**Result:** Reliable, scalable, NO CORS, built-in cron! 🚀


## Quick Deploy to Vercel (5 Minutes!)

### Method 1: Vercel CLI (Recommended)

```bash
# 1. Install Vercel CLI globally
npm install -g vercel

# 2. Navigate to project
cd solar-nextjs

# 3. Install dependencies
npm install

# 4. Login to Vercel
vercel login

# 5. Deploy to production
vercel --prod
```

Done! Your app is live! 🎉

### Method 2: GitHub + Vercel Dashboard

1. **Push to GitHub:**
   ```bash
   cd solar-nextjs
   git init
   git add .
   git commit -m "Initial commit - Solar monitoring Next.js"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Connect to Vercel:**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Git Repository"
   - Select your solar-nextjs repository
   - Click "Import"

3. **Configure & Deploy:**
   - Vercel will auto-detect Next.js
   - Click "Deploy"
   - Done!

## Environment Variables Setup

### Required Variables

After deployment, add these environment variables in Vercel dashboard:

1. Go to your project dashboard
2. Click **Settings** → **Environment Variables**
3. Add each variable:

```env
# WatchPower API Credentials
USERNAMES=Ahmarjb
PASSWORD=Ahmar123
SERIAL_NUMBER=96342404600319
WIFI_PN=W0034053928283
DEV_CODE=2488
DEV_ADDR=1

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
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/1425686982838714500/mGBwR_cxPi_ql2FETq3-xTg9By0etPsSDYurSv1vtzwjge1OWahWMsW_meeBieVKuTnK

# Cron Job Security (Generate a random secret)
CRON_SECRET=your-random-secret-key-here

# Alert Configuration
GRID_FEED_ALERT_INTERVAL_HOURS=1
LOAD_SHEDDING_VOLTAGE_THRESHOLD=180
SYSTEM_OFFLINE_THRESHOLD_MINUTES=10
LOW_PRODUCTION_THRESHOLD_WATTS=500
```

### Generate CRON_SECRET

```bash
# On Linux/Mac:
openssl rand -hex 32

# On Windows (PowerShell):
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

# Or use any random string:
my-super-secret-cron-key-12345
```

## Verify Deployment

### 1. Check Homepage
```
https://your-app.vercel.app
```
Should show the dashboard homepage

### 2. Test API Endpoints
```bash
# Test stats endpoint
curl https://your-app.vercel.app/api/stats

# Test health endpoint
curl https://your-app.vercel.app/api/health

# Test notifications
curl -X POST https://your-app.vercel.app/api/notifications/test

# Test daily summary
curl https://your-app.vercel.app/api/notifications/test-daily-summary
```

### 3. Verify Cron Jobs

In Vercel Dashboard:
1. Go to your project
2. Click **Deployments**
3. Click latest deployment
4. Click **Functions**
5. You should see:
   - `/api/cron/monitor` - Runs every 5 min
   - `/api/cron/daily-summary` - Runs at 7 PM UTC (midnight PKT)

### 4. Check Cron Job Logs

1. Go to Vercel Dashboard
2. Click your project
3. Click **Logs**
4. Filter by function: `/api/cron/monitor`
5. You should see logs every 5 minutes

## Post-Deployment Checklist

- [ ] Homepage loads successfully
- [ ] `/api/stats` returns data
- [ ] `/api/health` returns system health
- [ ] Test notifications work (email, telegram, discord)
- [ ] Cron job `/api/cron/monitor` appears in Functions
- [ ] Cron job `/api/cron/daily-summary` appears in Functions
- [ ] All environment variables are set
- [ ] CRON_SECRET is configured
- [ ] Monitoring logs appear in Vercel logs

## Monitoring Your Cron Jobs

### View Cron Execution Logs

```bash
# Install Vercel CLI
npm i -g vercel

# View logs (live)
vercel logs --follow

# View logs for specific function
vercel logs --follow /api/cron/monitor
```

### Expected Log Output

**Every 5 Minutes:**
```
🔄 Cron: Running monitoring checks...
✅ Cron: Monitoring checks completed
```

**Daily at Midnight PKT:**
```
🌙 Cron: Running daily summary...
📊 Sending daily summary for 2024-10-08
✅ Daily summary sent via Email
✅ Daily summary sent via Telegram
✅ Daily summary sent via Discord
✅ Cron: Daily summary sent for 2024-10-08
```

## Troubleshooting

### Cron Jobs Not Running

**Problem:** No logs appearing for cron jobs

**Solution:**
1. Verify `vercel.json` is in root directory
2. Check CRON_SECRET is set in environment variables
3. Redeploy: `vercel --prod`
4. Wait 5 minutes for first cron execution

### Environment Variables Not Working

**Problem:** API returns errors about missing credentials

**Solution:**
1. Double-check all variables are set in Vercel dashboard
2. Click **Redeploy** after adding variables
3. Check for typos in variable names (case-sensitive!)

### Notifications Not Sending

**Problem:** Test notifications return success but no message received

**Solution:**
1. Verify email/telegram/discord credentials
2. Check Gmail App Password (not regular password)
3. Test each service individually
4. Check Vercel function logs for errors

### API Timeout Errors

**Problem:** Functions timing out

**Solution:**
- Vercel free tier: 10s timeout (hobby: 60s)
- Optimize slow API calls
- Consider upgrading to Hobby plan ($20/mo) if needed

## Custom Domain (Optional)

### Add Your Own Domain

1. Go to Vercel Dashboard
2. Click **Settings** → **Domains**
3. Add your domain (e.g., `solar.yourdomain.com`)
4. Follow DNS configuration instructions
5. Done! Your app will be at your custom domain

## Updating Your App

### Deploy New Changes

```bash
# Make your changes
# ...

# Deploy
git add .
git commit -m "Update features"
git push

# If using Vercel CLI:
vercel --prod
```

Vercel automatically redeploys on git push if connected to GitHub!

## Rollback

### Rollback to Previous Version

1. Go to Vercel Dashboard
2. Click **Deployments**
3. Find the working deployment
4. Click **...** → **Promote to Production**

## Cost Estimate

### Vercel Free Tier
- ✅ 100GB bandwidth/month
- ✅ Unlimited API requests
- ✅ Cron jobs included
- ✅ 100 serverless function executions/day

**Your Usage Estimate:**
- Monitoring cron: 12 executions/hour × 24 hours = 288/day
- Daily summary: 1/day
- API calls from frontend: ~50/day
- **Total: ~340 executions/day**

**❌ Problem:** Free tier only allows 100 executions/day!

**✅ Solution:** Upgrade to Hobby plan ($20/month) for unlimited executions

**Or:** Reduce monitoring frequency:
- Change cron to every 10 minutes instead of 5
- Reduces to ~150 executions/day (still over limit)

**Recommendation:** Hobby plan is worth it for reliability!

## Comparison: Before vs After

| Feature | Python + Render | Next.js + Vercel |
|---------|----------------|------------------|
| **Cost** | FREE | $20/mo (Hobby) |
| **Cold Starts** | ❌ Yes | ✅ No |
| **CORS** | ❌ Issues | ✅ None |
| **Cron** | ❌ External | ✅ Built-in |
| **Reliability** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Maintenance** | ❌ Two repos | ✅ One repo |
| **Deploy** | ❌ Complex | ✅ One command |

## Support

If you encounter issues:

1. **Check Vercel Logs**
   ```bash
   vercel logs --follow
   ```

2. **Check Environment Variables**
   - Vercel Dashboard → Settings → Environment Variables

3. **Verify Cron Schedule**
   - Check `vercel.json` configuration

4. **Test Endpoints Manually**
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

## Success! 🎉

If you see:
- ✅ Cron logs every 5 minutes
- ✅ Daily summary logs at midnight PKT
- ✅ Notifications arriving
- ✅ API endpoints working

**Your Next.js solar monitoring system is fully operational!**

---

**Deployment Time:** ~5 minutes
**Configuration Time:** ~10 minutes
**Total Setup:** ~15 minutes

**Result:** Reliable, scalable, NO CORS, built-in cron! 🚀

