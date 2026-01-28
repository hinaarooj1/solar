// API Configuration - Using Next.js API Routes (Vercel Backend)

// API Base URL - empty string uses same domain (Next.js API routes)
export const API_BASE_URL = '';

// API Endpoints - All using Next.js /api routes
export const API_ENDPOINTS = {
    // Get daily stats for a specific date
    getDailyStats: (date: string) => `/api/stats?date=${date}`,
    
    // Get stats for a date range
    getStatsRange: (fromDate: string, toDate: string) => 
        `/api/stats-range?from_date=${fromDate}&to_date=${toDate}`,
    
    // Refetch missing dates
    refetchMissingDates: () => `/api/stats-range/refetch`,
    
    // System Control Endpoints
    controlGridFeed: () => `/api/control/grid-feed`,
    controlOutputPriority: () => `/api/control/output-priority`,
    controlLCDAutoReturn: () => `/api/control/lcd-auto-return`,
    controlSystemSettings: () => `/api/control/system-settings`,
    
    // System Health & Monitoring
    systemHealth: () => `/api/system/health`,
    systemSettings: () => `/api/system/settings/current`,
    
    // Notifications
    notificationTest: () => `/api/notifications/test-email`,
    notificationStatus: () => `/api/notifications/status`,
    testDailySummary: () => `/api/notifications/test-daily-summary`,
    testTelegram: () => `/api/notifications/test-telegram`,
    testDiscord: () => `/api/notifications/test-discord`,
    
    // Alerts Configuration
    alertsConfig: () => `/api/alerts/config`,
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

export default {
    API_BASE_URL,
    API_ENDPOINTS,
    CONFIG
};
