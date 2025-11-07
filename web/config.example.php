<?php
/**
 * NewsTrader Web Frontend Configuration - Example
 *
 * Copy this file to config.php and update with your settings:
 *   cp config.example.php config.php
 */

// API Configuration
define('API_BASE_URL', 'http://localhost:8000');  // Change to your API URL
define('API_KEY', 'your-api-key-here');           // Your API key from .env

// Refresh interval in seconds (how often to check for new data)
define('REFRESH_INTERVAL', 30);

// Timezone for displaying timestamps
date_default_timezone_set('UTC');

// Error reporting (disable in production)
error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('log_errors', 1);

/**
 * DEPLOYMENT EXAMPLES:
 *
 * Local development:
 *   API_BASE_URL = 'http://localhost:8000'
 *
 * Remote API server:
 *   API_BASE_URL = 'http://192.168.1.100:8000'
 *
 * API behind reverse proxy:
 *   API_BASE_URL = 'https://api.yourdomain.com'
 *
 * SECURITY:
 * - Never commit config.php with real API key
 * - Use strong, unique API keys
 * - Enable HTTPS in production
 * - Protect this file with .htaccess
 */
