/**
 * Configuration Template File
 * 
 * Instructions:
 * 1. Copy this file to config.js
 * 2. Replace placeholder values with your actual credentials
 * 3. Never commit your actual config.js file
 * 
 * Note: config.js should be listed in .gitignore
 */

const CONFIG = {
    // API Keys
    ALPHA_VANTAGE_API_KEY: 'YOUR_API_KEY_HERE', // Get from: https://www.alphavantage.co/support/#api-key
    
    // API Endpoints
    ENDPOINTS: {
        ALPHA_VANTAGE: 'https://www.alphavantage.co/query',
        SEC_FILINGS: 'https://api.sec-api.io',
        CUSTOM_BACKEND: 'http://localhost:8000/api/v1' // Update for production
    },

    // API Rate Limits
    RATE_LIMITS: {
        ALPHA_VANTAGE: {
            CALLS_PER_MINUTE: 5,
            CALLS_PER_DAY: 500
        }
    },

    // Chart Configuration
    CHART_CONFIG: {
        COLORS: {
            PRIMARY: '#00ff9f',
            SECONDARY: '#00aeff',
            DANGER: '#ff5555',
            WARNING: '#ffb86c',
            INFO: '#bd93f9'
        },
        DEFAULT_TIMEFRAME: '1Y', // Options: '1M', '3M', '6M', '1Y', '5Y'
        CHART_THEME: 'dark' // Options: 'dark', 'light'
    },

    // Portfolio Settings
    PORTFOLIO: {
        MAX_STOCKS: 50,
        DEFAULT_CURRENCY: 'USD',
        RISK_FREE_RATE: 0.02, // 2% annual rate
        REBALANCE_THRESHOLD: 0.05 // 5% deviation triggers rebalance alert
    },

    // Cache Settings
    CACHE: {
        STOCK_DATA_TTL: 300, // 5 minutes in seconds
        SEC_DATA_TTL: 86400 // 24 hours in seconds
    },

    // Feature Flags
    FEATURES: {
        ENABLE_SEC_FILINGS: true,
        ENABLE_REAL_TIME_UPDATES: false,
        ENABLE_NOTIFICATIONS: true,
        ENABLE_ADVANCED_METRICS: true
    },

    // Error Handling
    ERROR_REPORTING: {
        LOG_LEVEL: 'ERROR', // Options: 'DEBUG', 'INFO', 'WARN', 'ERROR'
        ENABLE_CONSOLE_LOGS: true,
        ENABLE_ERROR_REPORTING: false
    },

    // Development Settings
    DEV: {
        USE_MOCK_DATA: false,
        MOCK_DATA_PATH: '/assets/mock_data/',
        ENABLE_DEBUG_TOOLS: false
    }
};

// Prevent accidental modification of config
Object.freeze(CONFIG); 