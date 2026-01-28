# Daily Summary Date Fix

## 🐛 Issue
The "Test Daily Summary" button was sending data from **2 days ago** instead of **yesterday's data**.

## 🔍 Root Cause
The issue was **timezone handling**. The code was using:
```javascript
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
const dateStr = yesterday.toISOString().split('T')[0];
```

This approach has problems:
- `toISOString()` always converts to UTC time
- When running on Vercel servers (UTC timezone), this was causing date offset issues
- For Pakistan (PKT = UTC+5), dates were getting confused

### Example of the Problem:
```
Server time: Oct 9, 2025 (UTC)
User expectation: Oct 8, 2025 (yesterday in PKT)
Old code calculated: Oct 7, 2025 (2 days ago!)
```

## ✅ Solution
Now properly calculating dates in **PKT timezone (UTC+5)**:

```javascript
// Get current time
const now = new Date();

// Convert to PKT (UTC+5)
const pktOffset = 5 * 60; // PKT is UTC+5
const localOffset = now.getTimezoneOffset();
const pktTime = new Date(now.getTime() + (pktOffset + localOffset) * 60 * 1000);

// Get yesterday in PKT
const yesterday = new Date(pktTime);
yesterday.setDate(yesterday.getDate() - 1);

// Format as YYYY-MM-DD
const year = yesterday.getFullYear();
const month = String(yesterday.getMonth() + 1).padStart(2, '0');
const day = String(yesterday.getDate()).padStart(2, '0');
const dateStr = `${year}-${month}-${day}`;
```

## 📝 Files Fixed

1. **`solar-nextjs/app/api/notifications/test-daily-summary/route.ts`**
   - Now correctly calculates yesterday's date in PKT
   - Added debug logging to show current PKT time

2. **`solar-nextjs/app/api/cron/daily-summary/route.ts`**
   - Also fixed for consistency
   - Ensures automatic daily summaries use correct date

## 🧪 Testing

Today is **October 9, 2025** (in PKT timezone)

When you click "Test Daily Summary", it should now:
- ✅ Fetch data for **October 8, 2025** (yesterday)
- ✅ Show correct date in logs: `2025-10-08`
- ✅ Send summary for the correct day

### How to Test:
1. Click "Test Daily Summary" button in Controls page
2. Check the response - should say date: "2025-10-08"
3. Check your Email/Telegram/Discord - summary should be for Oct 8

## 📊 What This Affects

- **Test Daily Summary button** - Now sends correct date
- **Automatic Daily Summary cron** - Will send correct date at midnight PKT
- **All timezone calculations** - Now properly handle PKT

---

**Fixed:** October 9, 2025
**Issue:** Timezone offset causing wrong date calculation
**Solution:** Proper PKT (UTC+5) timezone handling






