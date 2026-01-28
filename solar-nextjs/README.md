# Solar Monitoring System - Next.js Version

🚀 **Complete migration from Python + Render to Next.js + Vercel**

## Overview

This is a complete rewrite of the solar monitoring system using Next.js, providing:
- ✅ **No CORS issues** - Frontend and API in same domain
- ✅ **Built-in Cron Jobs** - Vercel Cron (no external service needed)
- ✅ **No Cold Starts** - Reliable cron execution
- ✅ **FREE Hosting** - Vercel free tier
- ✅ **TypeScript** - Type safety throughout
- ✅ **One Deployment** - Single command to deploy everything

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Material-UI (MUI)
- **Charts:** Recharts
- **Hosting:** Vercel
- **Cron Jobs:** Vercel Cron (built-in)
- **Notifications:** Email (Nodemailer), Telegram, Discord

## Project Structure

```
solar-nextjs/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Home page (Dashboard)
│   ├── stats/
│   │   └── page.tsx       # Daily stats page
│   ├── controls/
│   │   └── page.tsx       # System controls page
│   │
│   └── api/               # API Routes
│       ├── stats/
│       │   └── route.ts
│       ├── health/
│       │   └── route.ts
│       ├── notifications/
│       │   ├── test/route.ts
│       │   └── test-daily-summary/route.ts
│       │
│       └── cron/          # Vercel Cron Jobs
│           ├── monitor/route.ts       # Runs every 5 min
│           └── daily-summary/route.ts # Runs at midnight PKT
│
├── lib/                   # Shared libraries
│   ├── watchpower-api.ts  # WatchPower API client
│   ├── monitoring-service.ts
│   ├── email-service.ts
│   ├── telegram-service.ts
│   └── discord-service.ts
│
├── components/            # React components
│   └── ... (UI components)
│
├── public/               # Static files
├── vercel.json           # Vercel configuration (Cron setup)
├── package.json
└── tsconfig.json
```

## Installation

### 1. Clone or Navigate to Project

```bash
cd solar-nextjs
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Copy `env.example` to `.env.local`:

```bash
cp env.example .env.local
```

Edit `.env.local` with your values:

```env
# WatchPower API
USERNAMES=your_username
PASSWORD=your_password
SERIAL_NUMBER=your_serial
WIFI_PN=your_wifi_pn
DEV_CODE=your_dev_code
DEV_ADDR=your_dev_addr

# Email
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
ALERT_EMAIL=recipient@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Discord
DISCORD_WEBHOOK_URL=your_webhook_url

# Cron Security
CRON_SECRET=random_secret_key_here

# Alert Config
GRID_FEED_ALERT_INTERVAL_HOURS=1
LOAD_SHEDDING_VOLTAGE_THRESHOLD=180
SYSTEM_OFFLINE_THRESHOLD_MINUTES=10
LOW_PRODUCTION_THRESHOLD_WATTS=500
```

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Deployment to Vercel

### Option 1: Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Option 2: GitHub Integration

1. Push code to GitHub repository
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Configure environment variables in Vercel dashboard
6. Deploy!

### Setting Environment Variables on Vercel

1. Go to your project dashboard on Vercel
2. Click "Settings" → "Environment Variables"
3. Add all variables from `.env.local`
4. Redeploy if needed

## Vercel Cron Jobs

Configured in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/monitor",
      "schedule": "*/5 * * * *"  // Every 5 minutes
    },
    {
      "path": "/api/cron/daily-summary",
      "schedule": "0 19 * * *"  // 12 AM PKT (7 PM UTC)
    }
  ]
}
```

**Cron jobs run automatically after deployment!** No external service needed.

### Security

Cron endpoints are protected by `CRON_SECRET`:

```typescript
const authHeader = request.headers.get('authorization');
if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
  return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
}
```

## Features

### Monitoring (Every 5 minutes)
- ✅ System reset detection (Output Priority changes)
- ✅ Load shedding detection (Grid voltage drops)
- ✅ Grid feed status monitoring
- ✅ System offline detection
- ✅ Low production alerts

### Daily Summary (Midnight PKT)
- ✅ Solar production (kWh)
- ✅ Energy usage (kWh)
- ✅ Grid contribution (kWh)
- ✅ Load shedding hours
- ✅ System off time
- ✅ Sent to Email, Telegram, Discord

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Get daily statistics |
| `/api/health` | GET | System health check |
| `/api/notifications/test` | POST | Test notifications |
| `/api/notifications/test-daily-summary` | GET | Test daily summary |
| `/api/cron/monitor` | GET | Monitoring cron job |
| `/api/cron/daily-summary` | GET | Daily summary cron job |

## Testing

### Test Notifications

```bash
curl https://your-app.vercel.app/api/notifications/test -X POST
```

### Test Daily Summary

```bash
curl https://your-app.vercel.app/api/notifications/test-daily-summary
```

### Test Cron Manually

```bash
curl https://your-app.vercel.app/api/cron/monitor \
  -H "Authorization: Bearer YOUR_CRON_SECRET"
```

## Advantages Over Python + Render

| Feature | Python + Render | Next.js + Vercel |
|---------|----------------|------------------|
| Cold Starts | ❌ Yes (15 min) | ✅ None for cron |
| CORS | ❌ Needs config | ✅ No CORS |
| Cron | ❌ External | ✅ Built-in |
| Deployment | ❌ Separate | ✅ One command |
| Cost | FREE (limited) | ✅ FREE (better) |
| Maintenance | ❌ Two codebases | ✅ One codebase |
| Type Safety | ❌ Python | ✅ TypeScript |
| Performance | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Vercel Free Tier Limits

✅ **100GB bandwidth/month**
✅ **Unlimited API requests**
✅ **Cron Jobs included**
✅ **Edge Functions**
✅ **Automatic HTTPS**
✅ **Global CDN**

**Your monitoring system fits well within the free tier!**

## Troubleshooting

### Cron Jobs Not Running

1. Check Vercel dashboard → Deployments → Functions
2. Verify `CRON_SECRET` is set in environment variables
3. Check function logs in Vercel dashboard

### Email Not Working

1. Verify Gmail App Password (not regular password)
2. Enable "Less secure app access" or use App Passwords
3. Check environment variables are set correctly

### API Errors

1. Check WatchPower credentials
2. Verify all environment variables are set
3. Check function logs in Vercel

## Migration from Python Version

All features from the Python version are included:
- ✅ All monitoring alerts
- ✅ Daily summary
- ✅ Email, Telegram, Discord notifications
- ✅ System health checks
- ✅ Dashboard UI
- ✅ System controls page

## Support

If you encounter issues:
1. Check Vercel function logs
2. Verify environment variables
3. Test notifications manually
4. Check cron job execution in Vercel dashboard

## License

MIT

---

**Built with ❤️ using Next.js + TypeScript + Vercel**

🚀 Deploy with one command: `vercel --prod`


🚀 **Complete migration from Python + Render to Next.js + Vercel**

## Overview

This is a complete rewrite of the solar monitoring system using Next.js, providing:
- ✅ **No CORS issues** - Frontend and API in same domain
- ✅ **Built-in Cron Jobs** - Vercel Cron (no external service needed)
- ✅ **No Cold Starts** - Reliable cron execution
- ✅ **FREE Hosting** - Vercel free tier
- ✅ **TypeScript** - Type safety throughout
- ✅ **One Deployment** - Single command to deploy everything

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Material-UI (MUI)
- **Charts:** Recharts
- **Hosting:** Vercel
- **Cron Jobs:** Vercel Cron (built-in)
- **Notifications:** Email (Nodemailer), Telegram, Discord

## Project Structure

```
solar-nextjs/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Home page (Dashboard)
│   ├── stats/
│   │   └── page.tsx       # Daily stats page
│   ├── controls/
│   │   └── page.tsx       # System controls page
│   │
│   └── api/               # API Routes
│       ├── stats/
│       │   └── route.ts
│       ├── health/
│       │   └── route.ts
│       ├── notifications/
│       │   ├── test/route.ts
│       │   └── test-daily-summary/route.ts
│       │
│       └── cron/          # Vercel Cron Jobs
│           ├── monitor/route.ts       # Runs every 5 min
│           └── daily-summary/route.ts # Runs at midnight PKT
│
├── lib/                   # Shared libraries
│   ├── watchpower-api.ts  # WatchPower API client
│   ├── monitoring-service.ts
│   ├── email-service.ts
│   ├── telegram-service.ts
│   └── discord-service.ts
│
├── components/            # React components
│   └── ... (UI components)
│
├── public/               # Static files
├── vercel.json           # Vercel configuration (Cron setup)
├── package.json
└── tsconfig.json
```

## Installation

### 1. Clone or Navigate to Project

```bash
cd solar-nextjs
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

Copy `env.example` to `.env.local`:

```bash
cp env.example .env.local
```

Edit `.env.local` with your values:

```env
# WatchPower API
USERNAMES=your_username
PASSWORD=your_password
SERIAL_NUMBER=your_serial
WIFI_PN=your_wifi_pn
DEV_CODE=your_dev_code
DEV_ADDR=your_dev_addr

# Email
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
ALERT_EMAIL=recipient@gmail.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Discord
DISCORD_WEBHOOK_URL=your_webhook_url

# Cron Security
CRON_SECRET=random_secret_key_here

# Alert Config
GRID_FEED_ALERT_INTERVAL_HOURS=1
LOAD_SHEDDING_VOLTAGE_THRESHOLD=180
SYSTEM_OFFLINE_THRESHOLD_MINUTES=10
LOW_PRODUCTION_THRESHOLD_WATTS=500
```

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

## Deployment to Vercel

### Option 1: Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Option 2: GitHub Integration

1. Push code to GitHub repository
2. Go to [vercel.com](https://vercel.com)
3. Click "New Project"
4. Import your GitHub repository
5. Configure environment variables in Vercel dashboard
6. Deploy!

### Setting Environment Variables on Vercel

1. Go to your project dashboard on Vercel
2. Click "Settings" → "Environment Variables"
3. Add all variables from `.env.local`
4. Redeploy if needed

## Vercel Cron Jobs

Configured in `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/cron/monitor",
      "schedule": "*/5 * * * *"  // Every 5 minutes
    },
    {
      "path": "/api/cron/daily-summary",
      "schedule": "0 19 * * *"  // 12 AM PKT (7 PM UTC)
    }
  ]
}
```

**Cron jobs run automatically after deployment!** No external service needed.

### Security

Cron endpoints are protected by `CRON_SECRET`:

```typescript
const authHeader = request.headers.get('authorization');
if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
  return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
}
```

## Features

### Monitoring (Every 5 minutes)
- ✅ System reset detection (Output Priority changes)
- ✅ Load shedding detection (Grid voltage drops)
- ✅ Grid feed status monitoring
- ✅ System offline detection
- ✅ Low production alerts

### Daily Summary (Midnight PKT)
- ✅ Solar production (kWh)
- ✅ Energy usage (kWh)
- ✅ Grid contribution (kWh)
- ✅ Load shedding hours
- ✅ System off time
- ✅ Sent to Email, Telegram, Discord

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Get daily statistics |
| `/api/health` | GET | System health check |
| `/api/notifications/test` | POST | Test notifications |
| `/api/notifications/test-daily-summary` | GET | Test daily summary |
| `/api/cron/monitor` | GET | Monitoring cron job |
| `/api/cron/daily-summary` | GET | Daily summary cron job |

## Testing

### Test Notifications

```bash
curl https://your-app.vercel.app/api/notifications/test -X POST
```

### Test Daily Summary

```bash
curl https://your-app.vercel.app/api/notifications/test-daily-summary
```

### Test Cron Manually

```bash
curl https://your-app.vercel.app/api/cron/monitor \
  -H "Authorization: Bearer YOUR_CRON_SECRET"
```

## Advantages Over Python + Render

| Feature | Python + Render | Next.js + Vercel |
|---------|----------------|------------------|
| Cold Starts | ❌ Yes (15 min) | ✅ None for cron |
| CORS | ❌ Needs config | ✅ No CORS |
| Cron | ❌ External | ✅ Built-in |
| Deployment | ❌ Separate | ✅ One command |
| Cost | FREE (limited) | ✅ FREE (better) |
| Maintenance | ❌ Two codebases | ✅ One codebase |
| Type Safety | ❌ Python | ✅ TypeScript |
| Performance | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## Vercel Free Tier Limits

✅ **100GB bandwidth/month**
✅ **Unlimited API requests**
✅ **Cron Jobs included**
✅ **Edge Functions**
✅ **Automatic HTTPS**
✅ **Global CDN**

**Your monitoring system fits well within the free tier!**

## Troubleshooting

### Cron Jobs Not Running

1. Check Vercel dashboard → Deployments → Functions
2. Verify `CRON_SECRET` is set in environment variables
3. Check function logs in Vercel dashboard

### Email Not Working

1. Verify Gmail App Password (not regular password)
2. Enable "Less secure app access" or use App Passwords
3. Check environment variables are set correctly

### API Errors

1. Check WatchPower credentials
2. Verify all environment variables are set
3. Check function logs in Vercel

## Migration from Python Version

All features from the Python version are included:
- ✅ All monitoring alerts
- ✅ Daily summary
- ✅ Email, Telegram, Discord notifications
- ✅ System health checks
- ✅ Dashboard UI
- ✅ System controls page

## Support

If you encounter issues:
1. Check Vercel function logs
2. Verify environment variables
3. Test notifications manually
4. Check cron job execution in Vercel dashboard

## License

MIT

---

**Built with ❤️ using Next.js + TypeScript + Vercel**

🚀 Deploy with one command: `vercel --prod`

