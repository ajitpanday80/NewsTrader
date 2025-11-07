/**
 * NewsTrader Signal Dashboard - JavaScript
 * Handles data fetching, auto-refresh, and UI rendering
 */

class SignalDashboard {
    constructor() {
        this.currentData = null;
        this.activeExchange = null;
        this.refreshTimer = null;
        this.lastUpdate = null;

        this.init();
    }

    init() {
        console.log('Initializing Signal Dashboard...');
        this.fetchSignals();
        this.startAutoRefresh();
    }

    /**
     * Fetch signals from API
     */
    async fetchSignals() {
        try {
            const response = await fetch(`${CONFIG.apiBaseUrl}/signals`, {
                headers: {
                    'X-API-Key': CONFIG.apiKey
                }
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    throw new Error('Authentication failed. Check your API key.');
                }
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.status === 'success' && data.data) {
                this.currentData = data.data;
                this.lastUpdate = new Date();
                this.renderDashboard();
                this.updateStatus('connected');
            } else if (data.status === 'no_active_signals') {
                this.showNoSignals();
                this.updateStatus('connected');
            } else {
                throw new Error('Unexpected response format');
            }

        } catch (error) {
            console.error('Error fetching signals:', error);
            this.showError(error.message);
            this.updateStatus('error');
        }
    }

    /**
     * Render the dashboard with signals
     */
    renderDashboard() {
        if (!this.currentData || !this.currentData.news_articles) {
            this.showNoSignals();
            return;
        }

        // Group signals by exchange
        const signalsByExchange = this.groupSignalsByExchange();

        if (Object.keys(signalsByExchange).length === 0) {
            this.showNoSignals();
            return;
        }

        // Show signals container
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('errorState').style.display = 'none';
        document.getElementById('noSignalsState').style.display = 'none';
        document.getElementById('signalsContainer').style.display = 'block';

        // Render exchange tabs
        this.renderExchangeTabs(signalsByExchange);

        // Render exchange content
        this.renderExchangeContent(signalsByExchange);

        // Update metadata
        this.updateMetadata();
    }

    /**
     * Group signals by exchange
     */
    groupSignalsByExchange() {
        const grouped = {};

        this.currentData.news_articles.forEach(article => {
            article.trading_signals.forEach(signal => {
                const exchange = signal.exchange || 'Unknown';

                if (!grouped[exchange]) {
                    grouped[exchange] = [];
                }

                grouped[exchange].push({
                    ...signal,
                    article_title: article.title,
                    article_url: article.url,
                    article_source: article.source
                });
            });
        });

        return grouped;
    }

    /**
     * Render exchange tabs
     */
    renderExchangeTabs(signalsByExchange) {
        const tabsContainer = document.getElementById('exchangeTabs');
        const exchanges = Object.keys(signalsByExchange).sort();

        // Set first exchange as active if none selected
        if (!this.activeExchange && exchanges.length > 0) {
            this.activeExchange = exchanges[0];
        }

        tabsContainer.innerHTML = exchanges.map(exchange => {
            const count = signalsByExchange[exchange].length;
            const isActive = exchange === this.activeExchange;

            return `
                <div class="exchange-tab ${isActive ? 'active' : ''}"
                     onclick="dashboard.switchExchange('${exchange}')">
                    <span>${exchange}</span>
                    <span class="exchange-badge">${count}</span>
                </div>
            `;
        }).join('');
    }

    /**
     * Render exchange content
     */
    renderExchangeContent(signalsByExchange) {
        const contentContainer = document.getElementById('exchangeContent');
        const exchanges = Object.keys(signalsByExchange).sort();

        contentContainer.innerHTML = exchanges.map(exchange => {
            const signals = signalsByExchange[exchange];
            const isActive = exchange === this.activeExchange;

            return `
                <div class="exchange-section ${isActive ? 'active' : ''}"
                     data-exchange="${exchange}">
                    <div class="signals-grid">
                        ${signals.map(signal => this.renderSignalCard(signal)).join('')}
                    </div>
                </div>
            `;
        }).join('');
    }

    /**
     * Render individual signal card
     */
    renderSignalCard(signal) {
        const confidencePercent = (signal.confidence * 100).toFixed(0);
        const signalClass = signal.signal.toLowerCase();

        return `
            <div class="signal-card">
                <div class="signal-header">
                    <div class="signal-ticker">
                        <div class="ticker-symbol">${this.escapeHtml(signal.ticker)}</div>
                        <div class="ticker-name">${this.escapeHtml(signal.name)}</div>
                    </div>
                    <div class="signal-badge ${signalClass}">
                        ${signal.signal}
                    </div>
                </div>

                <div class="signal-meta">
                    <div class="meta-item">
                        <div class="meta-label">Exchange</div>
                        <div class="meta-value">${this.escapeHtml(signal.exchange)}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Market</div>
                        <div class="meta-value">${this.escapeHtml(signal.market)}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Timeframe</div>
                        <div class="meta-value">${this.escapeHtml(signal.timeframe)}</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-label">Strategy</div>
                        <div class="meta-value">${this.escapeHtml(signal.entry_strategy)}</div>
                    </div>
                </div>

                <div class="confidence-bar">
                    <div class="meta-label">Confidence: ${confidencePercent}%</div>
                    <div class="confidence-progress">
                        <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                    </div>
                </div>

                <div class="signal-reasoning">
                    <div class="reasoning-title">Analysis</div>
                    <div class="reasoning-text">${this.escapeHtml(signal.reasoning)}</div>
                </div>

                <div class="signal-tags">
                    <div class="signal-tag">${this.escapeHtml(signal.instrument_type)}</div>
                    <div class="signal-tag">${this.escapeHtml(signal.currency)}</div>
                    <div class="signal-tag">${this.escapeHtml(signal.strength)} strength</div>
                </div>

                ${signal.article_url ? `
                    <div class="news-link">
                        <a href="${this.escapeHtml(signal.article_url)}" target="_blank" rel="noopener">
                            📰 Read News Article →
                        </a>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Switch to different exchange tab
     */
    switchExchange(exchange) {
        this.activeExchange = exchange;

        // Update tabs
        document.querySelectorAll('.exchange-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        event.target.closest('.exchange-tab').classList.add('active');

        // Update content
        document.querySelectorAll('.exchange-section').forEach(section => {
            section.classList.remove('active');
        });
        document.querySelector(`[data-exchange="${exchange}"]`).classList.add('active');
    }

    /**
     * Update dashboard metadata
     */
    updateMetadata() {
        // Last updated
        const lastUpdatedEl = document.getElementById('lastUpdated');
        if (this.lastUpdate) {
            lastUpdatedEl.textContent = this.formatTime(this.lastUpdate);
        }

        // Time remaining
        const timeRemainingEl = document.getElementById('timeRemaining');
        if (this.currentData && this.currentData.analysis_metadata) {
            const remaining = this.currentData.analysis_metadata.time_remaining_minutes;
            timeRemainingEl.textContent = `${remaining} min`;
        }

        // Total signals
        const totalSignalsEl = document.getElementById('totalSignals');
        let totalCount = 0;
        if (this.currentData && this.currentData.news_articles) {
            this.currentData.news_articles.forEach(article => {
                totalCount += article.trading_signals.length;
            });
        }
        totalSignalsEl.textContent = totalCount;
    }

    /**
     * Update status indicator
     */
    updateStatus(status) {
        const indicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');

        if (status === 'connected') {
            indicator.classList.remove('error');
            statusText.textContent = 'Connected';
        } else if (status === 'error') {
            indicator.classList.add('error');
            statusText.textContent = 'Error';
        }
    }

    /**
     * Show no signals state
     */
    showNoSignals() {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('errorState').style.display = 'none';
        document.getElementById('signalsContainer').style.display = 'none';
        document.getElementById('noSignalsState').style.display = 'block';
    }

    /**
     * Show error state
     */
    showError(message) {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('signalsContainer').style.display = 'none';
        document.getElementById('noSignalsState').style.display = 'none';

        const errorState = document.getElementById('errorState');
        const errorMessage = document.getElementById('errorMessage');

        errorMessage.textContent = message;
        errorState.style.display = 'block';
    }

    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        this.refreshTimer = setInterval(() => {
            console.log('Auto-refreshing signals...');
            this.fetchSignals();
        }, CONFIG.refreshInterval);

        console.log(`Auto-refresh enabled (every ${CONFIG.refreshInterval / 1000}s)`);
    }

    /**
     * Format time
     */
    formatTime(date) {
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    }

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize dashboard when DOM is ready
let dashboard;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        dashboard = new SignalDashboard();
    });
} else {
    dashboard = new SignalDashboard();
}
