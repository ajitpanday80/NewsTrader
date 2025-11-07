<?php
/**
 * NewsTrader Signal Dashboard
 * Displays trading signals grouped by exchange
 */

require_once 'config.php';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Signals Dashboard</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <div class="container">
        <!-- Status Bar -->
        <div class="status-bar">
            <div class="status-item">
                <span class="status-label">Last Updated:</span>
                <span id="lastUpdated" class="status-value">Loading...</span>
            </div>
            <div class="status-item">
                <span class="status-label">Time Remaining:</span>
                <span id="timeRemaining" class="status-value">--</span>
            </div>
            <div class="status-item">
                <span class="status-label">Total Signals:</span>
                <span id="totalSignals" class="status-value">0</span>
            </div>
            <div class="status-indicator">
                <span class="indicator" id="statusIndicator"></span>
                <span id="statusText">Connecting...</span>
            </div>
        </div>

        <!-- Loading State -->
        <div id="loadingState" class="loading-state">
            <div class="spinner"></div>
            <p>Loading signals...</p>
        </div>

        <!-- Error State -->
        <div id="errorState" class="error-state" style="display: none;">
            <div class="error-icon">⚠</div>
            <h3>Unable to Load Signals</h3>
            <p id="errorMessage"></p>
            <button onclick="location.reload()">Retry</button>
        </div>

        <!-- No Signals State -->
        <div id="noSignalsState" class="no-signals-state" style="display: none;">
            <div class="info-icon">ℹ</div>
            <h3>No Active Signals</h3>
            <p>New signals will appear when fresh news is analyzed.</p>
        </div>

        <!-- Signals Container -->
        <div id="signalsContainer" style="display: none;">
            <!-- Exchange tabs will be inserted here -->
            <div id="exchangeTabs" class="exchange-tabs"></div>

            <!-- Exchange content will be inserted here -->
            <div id="exchangeContent" class="exchange-content"></div>
        </div>
    </div>

    <script>
        // Pass PHP config to JavaScript
        const CONFIG = {
            apiBaseUrl: '<?php echo API_BASE_URL; ?>',
            apiKey: '<?php echo API_KEY; ?>',
            refreshInterval: <?php echo REFRESH_INTERVAL; ?> * 1000
        };
    </script>
    <script src="assets/js/app.js"></script>
</body>
</html>
