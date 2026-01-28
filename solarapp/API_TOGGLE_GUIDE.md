# 🔄 Quick Guide: Toggle API Between Local & Production

## Where to Change

**File:** `src/constants.js` (Line 4)

## Option 1: Use Production API (Default)

```javascript
const API_MODE = 'production'; // ✅ Using Render deployment
```

**API URL:** `https://watchpower-api-main-1.onrender.com`

✅ Use this when:
- Testing the deployed app
- Your local backend is not running
- Production environment

---

## Option 2: Use Local API

```javascript
const API_MODE = 'local'; // ✅ Using localhost
```

**API URL:** `http://localhost:5000`

✅ Use this when:
- Developing/testing locally
- Your local backend is running on port 5000
- Testing new features

⚠️ **Important:** Make sure your local API server is running first!

---

## 📍 Visual Reference

```javascript
// API Configuration
// Toggle between local and production API

// ┌─────────────────────────────────────┐
// │ CHANGE THIS LINE TO SWITCH API ⬇️   │
// └─────────────────────────────────────┘
const API_MODE = 'production'; // or 'local'
//               ^^^^^^^^^^
//               Change this!

const API_URLS = {
    local: 'http://localhost:5000',
    production: 'https://watchpower-api-main-1.onrender.com'
};
```

---

## 🎯 What Gets Changed Automatically

When you toggle `API_MODE`, these endpoints automatically update:

1. **Daily Stats API:**
   - Production: `https://watchpower-api-main-1.onrender.com/stats?date=...`
   - Local: `http://localhost:5000/stats?date=...`

2. **Monthly Stats API:**
   - Production: `https://watchpower-api-main-1.onrender.com/stats-range?from_date=...&to_date=...`
   - Local: `http://localhost:5000/stats-range?from_date=...&to_date=...`

---

## 🚀 After Changing

1. Save the file (`src/constants.js`)
2. The app will auto-reload (hot reload)
3. Check browser console for API calls
4. Test your dashboard!

---

## ❌ Common Issues

### Issue: "Error fetching API" when using local mode

**Solution:** 
- Make sure your local API server is running on `http://localhost:5000`
- Check if the port matches (you can change it in `constants.js`)

### Issue: App not updating after change

**Solution:**
- Clear browser cache
- Stop and restart development server: `Ctrl+C` then `npm start`

---

## 🔧 Custom API URL

Want to use a different URL? Edit `constants.js`:

```javascript
const API_URLS = {
    local: 'http://localhost:8000',  // Your custom port
    production: 'https://your-custom-api.com',  // Your API
    staging: 'https://staging-api.com'  // Add more environments!
};
```

Then switch between them:
```javascript
const API_MODE = 'staging';  // or 'local' or 'production'
```

