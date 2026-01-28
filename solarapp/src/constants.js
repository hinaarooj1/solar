// API Configuration
// Toggle between local and production API

// Set to 'local' for localhost or 'production' for deployed API
const API_MODE = 'production'; // Change to 'local' to use localhost

const API_URLS = {
    local: 'http://localhost:8000', // Your local development server
    production: 'http://localhost:8000'
};

// Export the base URL based on current mode
export const API_BASE_URL = API_URLS[API_MODE];

// API Endpoints
export const API_ENDPOINTS = {
    // Auth
    login: () => `${API_BASE_URL}/auth/login`,
    authMe: () => `${API_BASE_URL}/auth/me`,
    notificationEmail: () => `${API_BASE_URL}/user/notification-email`,

    // Get daily stats for a specific date
    getDailyStats: (date) => `${API_BASE_URL}/stats?date=${date}`,
    
    // Get stats for a date range
    getStatsRange: (fromDate, toDate) => `${API_BASE_URL}/stats-range?from_date=${fromDate}&to_date=${toDate}`,
    
    // Refetch missing dates
    refetchMissingDates: () => `${API_BASE_URL}/stats-range/refetch`,
    
    // NEW: System Health & Monitoring
    systemHealth: () => `${API_BASE_URL}/system/health`,
    systemSettings: () => `${API_BASE_URL}/system/settings/current`,
    
    // NEW: Notifications
    notificationTest: () => `${API_BASE_URL}/notifications/test`,
    notificationStatus: () => `${API_BASE_URL}/notifications/status`,
    testDailySummary: () => `${API_BASE_URL}/notifications/test-daily-summary`,
};

// Configuration
export const CONFIG = {
    // Auto-refresh interval in milliseconds (5 minutes)
    AUTO_REFRESH_INTERVAL: 300000,
    
    // Toast notification duration
    TOAST_DURATION: 3000,
    
    // Data point interval in minutes
    DATA_INTERVAL_MINUTES: 5,
    
    // Expected data points per day (24 hours * 60 minutes / 5 minutes)
    EXPECTED_DATA_POINTS_PER_DAY: 288
};

const constants = {
    API_BASE_URL,
    API_ENDPOINTS,
    CONFIG
};

export default constants;


