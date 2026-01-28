# Solar Dashboard - Project Structure

## 📁 File Structure

```
src/
├── App.js                 # Main app with Router
├── Table.js               # Dashboard layout (sidebar, navbar, routing)
├── constants.js           # API configuration (TOGGLE HERE!)
├── pages/
│   ├── DailyStats.js     # Daily stats page component
│   └── MonthlyStats.js   # Monthly stats page component
├── Table.css             # Styles
└── App.css               # Global styles
```

## 🔧 How to Toggle Between Local and Production API

### Open `src/constants.js`

Change the `API_MODE` constant:

```javascript
// For Production API (deployed on Render)
const API_MODE = 'production';

// For Local Development API
const API_MODE = 'local';
```

### API Endpoints Available:

**Production:** `https://watchpower-api-main-1.onrender.com`  
**Local:** `http://localhost:5000` (make sure your local server is running)

### APIs Used:
1. **Daily Stats:** `/stats?date=YYYY-MM-DD`
2. **Monthly Stats:** `/stats-range?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`

## 🚀 Routes

- `/` - Daily Stats Page
- `/monthly` - Monthly Stats Page

## 🎨 Features

### Dashboard Layout (`Table.js`)
- ✅ Persistent drawer (desktop) / Temporary drawer (mobile)
- ✅ Dark/Light mode toggle
- ✅ Theme color selector (Purple, Blue, Green, Orange)
- ✅ Responsive navigation
- ✅ Active route highlighting

### Daily Stats Page (`/`)
- ✅ Real-time solar production & load tracking
- ✅ Auto-refresh every 5 minutes (toggle-able)
- ✅ Date navigation (Previous/Next/Today)
- ✅ Fullscreen chart mode
- ✅ Missing data detection & visualization
- ✅ System status tracking (Connected/Disconnected/Off)

### Monthly Stats Page (`/monthly`)
- ✅ Date range selection
- ✅ Streaming progress indicator
- ✅ Daily production/load comparison
- ✅ Missing dates detection

## 🛠️ Development

```bash
# Start the app
npm start

# The app will run on http://localhost:3000
```

## 📝 Configuration Options

### `constants.js` - Full Configuration

```javascript
// API Mode: 'local' or 'production'
const API_MODE = 'production';

// API URLs
const API_URLS = {
    local: 'http://localhost:5000',
    production: 'https://watchpower-api-main-1.onrender.com'
};

// Config
export const CONFIG = {
    AUTO_REFRESH_INTERVAL: 300000,        // 5 minutes
    TOAST_DURATION: 3000,                 // 3 seconds
    DATA_INTERVAL_MINUTES: 5,             // Data points every 5 min
    EXPECTED_DATA_POINTS_PER_DAY: 288     // 24 * 60 / 5
};
```

## 🎯 How It Works

1. **App.js** wraps everything with `BrowserRouter`
2. **Table.js** provides the layout (navbar, sidebar, theme)
3. **Routes** render `DailyStats` or `MonthlyStats` based on URL
4. **Both pages** import from `constants.js` for API calls
5. **No hardcoded URLs** - all API calls use `API_ENDPOINTS` from constants

## 🔄 Adding New Routes

Edit `src/Table.js`:

```javascript
const menuItems = [
    { text: "Daily Stats", icon: <DashboardIcon />, path: "/" },
    { text: "Monthly Stats", icon: <BarChartIcon />, path: "/monthly" },
    { text: "New Page", icon: <YourIcon />, path: "/newpage" },  // Add here
];
```

Then add the route:

```javascript
<Routes>
    <Route path="/" element={<DailyStats {...props} />} />
    <Route path="/monthly" element={<MonthlyStats {...props} />} />
    <Route path="/newpage" element={<NewPage {...props} />} />  // Add here
</Routes>
```

## 📦 Dependencies

- `react-router-dom` - Routing
- `@mui/material` - UI components
- `recharts` - Charts
- `axios` - HTTP client
- `react-toastify` - Notifications

## 🎨 Theme Colors

Available themes: Purple (default), Blue, Green, Orange

Each theme has primary and secondary gradient colors for a modern look!

