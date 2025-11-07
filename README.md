# NewsTrader - AI-Powered News-Based Stock Signal Generator

**NewsTrader** is an intelligent system that analyzes market news and generates actionable trading signals using AI. It fetches real-time news from **Alpha Vantage**, analyzes it using **Groq AI** (openai/gpt-oss-120b model), and provides trading signals with auto-expiry and backup functionality.

## 🎯 Features

### Core Capabilities
- ✅ **Real-time News Analysis** - Fetches latest market news from Alpha Vantage API
- ✅ **AI-Powered Signal Generation** - Uses Groq AI to identify trading opportunities
- ✅ **Multi-Asset Support** - Stocks (US, India, Global), Crypto, Forex, ETFs, Indices
- ✅ **Related Stock Discovery** - AI identifies correlated stocks not mentioned in news
- ✅ **Auto-Expiry with TTL** - Signals expire after 30 minutes (configurable)
- ✅ **Automatic Backup** - All signals backed up before removal
- ✅ **REST API** - FastAPI server for frontend/website integration
- ✅ **Rich Signal Data** - Includes confidence scores, reasoning, risk factors, catalysts

### Signal Types
- **BUY** - Bullish opportunity with positive catalysts
- **SELL** - Bearish signal with downside risks
- **HOLD** - Wait and watch recommendation

### Supported Instruments
- 📈 **Stocks** - US (NYSE, NASDAQ), India (NSE, BSE), Global
- 💰 **Cryptocurrencies** - Bitcoin, Ethereum, etc.
- 💱 **Forex** - Currency pairs (USD, EUR, INR, etc.)
- 📊 **ETFs** - Gold, sector funds, index funds
- 📉 **Indices** - Nifty 50, S&P 500, etc.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NEWSTRADER SYSTEM                         │
└─────────────────────────────────────────────────────────────┘

1. NEWS FETCH (Every 5 min)
   ↓
   Alpha Vantage API → Latest Market News

2. AI ANALYSIS
   ↓
   Groq AI (openai/gpt-oss-120b) → Analyze News
   - Identify mentioned stocks
   - Discover related/correlated stocks
   - Generate BUY/SELL/HOLD signals
   - Provide reasoning & risk analysis

3. SIGNAL STORAGE
   ↓
   Active Database → Signals with 30-min TTL

4. API SERVER
   ↓
   REST API → Website/Frontend Access

5. CLEANUP (Every 5 min)
   ↓
   - Backup expired signals
   - Remove from active database
   - Organized by date
```

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- Alpha Vantage API Key ([Get Free Key](https://www.alphavantage.co/support/#api-key))
- Groq API Key ([Get Key](https://console.groq.com/keys))

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd NewsTrader
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` file with your API keys:
```env
# Alpha Vantage API Configuration
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

# Signal TTL Configuration (in minutes)
SIGNAL_TTL_MINUTES=30

# Job Intervals (in minutes)
CLEANUP_INTERVAL_MINUTES=5
NEWS_FETCH_INTERVAL_MINUTES=5

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000

# API Authentication (IMPORTANT: Change this to a secure key)
API_KEY=your-secure-api-key-here

# Logging
LOG_LEVEL=INFO
```

**⚠️ IMPORTANT: Generate a strong API key for production:**
```bash
# Generate a secure random API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🚀 Usage

### Run Full System (Orchestrator + API Server)

```bash
python -m src.main --api
```

This starts:
- **Background orchestrator** - Fetches news and generates signals every 5 minutes
- **Cleanup service** - Removes expired signals every 5 minutes
- **API server** - Serves signals on `http://localhost:8000`

### Run Orchestrator Only

```bash
python -m src.main
```

Runs background jobs without API server.

### Run API Server Only

```bash
python -m src.api_server
```

Serves existing signals via REST API.

---

## 📡 API Endpoints

### Base URL
```
http://localhost:8000
```

### 🔐 Authentication

**All endpoints (except `/` and `/health`) require API key authentication.**

Include your API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" http://localhost:8000/signals
```

**JavaScript Example:**
```javascript
fetch('http://localhost:8000/signals', {
  headers: {
    'X-API-Key': 'your-api-key-here'
  }
})
```

**Python Example:**
```python
import requests

headers = {'X-API-Key': 'your-api-key-here'}
response = requests.get('http://localhost:8000/signals', headers=headers)
```

**Error Responses:**
- `401 Unauthorized` - Missing API key
- `403 Forbidden` - Invalid API key

---

### Available Endpoints

#### 1. **Get Active Signals**
```http
GET /signals
```

Returns all active trading signals with TTL information.

**Response:**
```json
{
  "status": "success",
  "data": {
    "analysis_metadata": {...},
    "news_articles": [...],
    "summary": {...}
  },
  "timestamp": "2025-11-07T14:30:00Z"
}
```

#### 2. **Get Signals Summary**
```http
GET /signals/summary
```

Returns condensed summary without full article details.

#### 3. **Filter by Market**
```http
GET /signals/by-market?market=India
```

Filters: `US`, `India`, `Crypto`, `Forex`, `Global`

#### 4. **Filter by Exchange**
```http
GET /signals/by-exchange?exchange=NSE
```

Filters: `NYSE`, `NASDAQ`, `NSE`, `BSE`, `Multiple Exchanges`, `Forex Market`

#### 5. **Filter by Signal Type**
```http
GET /signals/by-signal-type?signal_type=BUY
```

Filters: `BUY`, `SELL`, `HOLD`

#### 6. **Get Historical Signals**
```http
GET /signals/history?date=2025-11-07&limit=10
```

Returns archived signals from backup.

#### 7. **List Backup Dates**
```http
GET /signals/backups
```

Lists all available backup dates.

#### 8. **Get Statistics**
```http
GET /stats
```

Returns system statistics and metrics.

#### 9. **Health Check**
```http
GET /health
```

Check if API is running.

---

## 📊 JSON Output Format

### Complete Signal Structure

```json
{
  "analysis_metadata": {
    "analysis_id": "uuid-string",
    "timestamp": "2025-11-07T14:30:00Z",
    "expires_at": "2025-11-07T15:00:00Z",
    "ttl_minutes": 30,
    "status": "active",
    "time_remaining_minutes": 25,
    "news_source": "Alpha Vantage",
    "ai_model": "openai/gpt-oss-120b",
    "total_articles_analyzed": 5,
    "total_signals_generated": 15,
    "markets_covered": ["US", "India", "Crypto"],
    "backup_path": "backups/2025-11-07/analysis-uuid.json"
  },

  "news_articles": [
    {
      "article_id": "uuid",
      "title": "Fed Announces Rate Cuts",
      "summary": "Federal Reserve...",
      "url": "https://example.com/article",
      "source": "Reuters",
      "published_at": "2025-11-07T10:00:00Z",
      "processed_at": "2025-11-07T14:30:00Z",
      "expires_at": "2025-11-07T15:00:00Z",
      "time_remaining_minutes": 25,

      "overall_sentiment": {
        "score": 0.45,
        "label": "Bullish"
      },

      "mentioned_assets": [
        {
          "ticker": "BTC",
          "symbol": "CRYPTO:BTC",
          "name": "Bitcoin",
          "instrument_type": "cryptocurrency",
          "exchange": "Multiple Exchanges",
          "market": "Crypto",
          "country": "Global",
          "currency": "USD",
          "relevance_score": 0.98,
          "sentiment": {
            "score": 0.65,
            "label": "Bullish"
          }
        }
      ],

      "related_assets": [
        {
          "ticker": "ETH",
          "name": "Ethereum",
          "instrument_type": "cryptocurrency",
          "exchange": "Multiple Exchanges",
          "market": "Crypto",
          "relationship": "correlated_asset",
          "potential_impact": "positive",
          "impact_probability": 0.82,
          "ai_reasoning": "Ethereum follows Bitcoin trends..."
        }
      ],

      "trading_signals": [
        {
          "signal_id": "uuid",
          "ticker": "BTC",
          "symbol": "CRYPTO:BTC",
          "name": "Bitcoin",
          "instrument_type": "cryptocurrency",
          "exchange": "Multiple Exchanges",
          "market": "Crypto",
          "country": "Global",
          "currency": "USD",
          "signal": "BUY",
          "confidence": 0.88,
          "strength": "strong",
          "timeframe": "short-term",
          "holding_period": "1-4 weeks",
          "entry_strategy": "immediate",
          "target_allocation": "5-10%",
          "reasoning": "Rate cuts make Bitcoin attractive...",
          "risk_factors": ["Regulatory uncertainty", "High volatility"],
          "catalysts": ["Fed rate cuts", "Dollar weakness"],
          "generated_at": "2025-11-07T14:30:00Z",
          "expires_at": "2025-11-07T15:00:00Z",
          "time_remaining_minutes": 25,
          "is_expired": false
        }
      ],

      "market_impact": {
        "sectors_affected": ["Cryptocurrency", "Financial Services"],
        "impact_level": "high",
        "geographic_impact": ["Global"],
        "market_sentiment_shift": "risk-on",
        "volatility_expectation": "high",
        "expected_duration": "1-2 weeks"
      }
    }
  ],

  "summary": {
    "total_assets_analyzed": 15,
    "signals_by_type": {
      "total": 15,
      "BUY": 8,
      "SELL": 3,
      "HOLD": 4
    },
    "signals_by_market": {
      "Crypto": {"total": 5, "BUY": 4, "SELL": 0, "HOLD": 1},
      "US": {"total": 6, "BUY": 3, "SELL": 2, "HOLD": 1},
      "India": {"total": 4, "BUY": 1, "SELL": 1, "HOLD": 2}
    },
    "average_confidence": 0.74,
    "high_confidence_signals": [...],
    "key_insights": ["Fed rate cuts drive crypto rally..."],
    "top_opportunities": [...],
    "top_risks": [...]
  }
}
```

---

## 📁 Project Structure

```
NewsTrader/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── config.py                # Configuration management
│   ├── models.py                # Data models (Pydantic)
│   ├── news_fetcher.py          # Alpha Vantage integration
│   ├── signal_generator.py      # Groq AI integration
│   ├── cleanup_service.py       # TTL & backup handler
│   ├── api_server.py            # FastAPI REST API
│   └── main.py                  # Main orchestrator
│
├── data/
│   ├── active/                  # Active signals (< 30 min)
│   │   └── current_signals.json
│   └── backups/                 # Archived signals
│       └── 2025-11-07/
│           └── analysis-*.json
│
├── logs/                        # Application logs
│   └── newstrader_*.log
│
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .env                         # Your configuration (gitignored)
└── README.md                    # This file
```

---

## 🔧 Configuration

### TTL Configuration
Control how long signals remain active:

```env
SIGNAL_TTL_MINUTES=30  # Signals expire after 30 minutes
```

### Job Intervals
Configure how often jobs run:

```env
NEWS_FETCH_INTERVAL_MINUTES=5   # Fetch news every 5 minutes
CLEANUP_INTERVAL_MINUTES=5      # Cleanup check every 5 minutes
```

### API Configuration
```env
API_HOST=0.0.0.0  # Listen on all interfaces
API_PORT=8000     # Port number
```

---

## 🎨 Frontend Integration

### Example: Fetch Active Signals

```javascript
// Fetch active signals with API key authentication
fetch('http://localhost:8000/signals', {
  headers: {
    'X-API-Key': 'your-api-key-here'
  }
})
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      const signals = data.data;
      console.log(`Time remaining: ${signals.analysis_metadata.time_remaining_minutes} minutes`);

      // Display signals
      signals.news_articles.forEach(article => {
        console.log(`Article: ${article.title}`);
        console.log(`URL: ${article.url}`);

        article.trading_signals.forEach(signal => {
          console.log(`${signal.signal} ${signal.ticker} (${signal.confidence})`);
        });
      });
    }
  });
```

### Example: Filter by Market

```javascript
// Get only Indian stocks
fetch('http://localhost:8000/signals/by-market?market=India', {
  headers: {
    'X-API-Key': 'your-api-key-here'
  }
})
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.data.count} signals for Indian market`);
  });
```

### Example: Get BUY Signals Only

```javascript
// Get only BUY signals
fetch('http://localhost:8000/signals/by-signal-type?signal_type=BUY', {
  headers: {
    'X-API-Key': 'your-api-key-here'
  }
})
  .then(response => response.json())
  .then(data => {
    data.data.news_articles.forEach(article => {
      article.trading_signals.forEach(signal => {
        console.log(`BUY ${signal.ticker} @ ${signal.confidence} confidence`);
        console.log(`Reasoning: ${signal.reasoning}`);
      });
    });
  });
```

---

## 📝 Logging

Logs are stored in `logs/` directory with daily rotation:

```
logs/
├── newstrader_2025-11-07.log
├── newstrader_2025-11-06.log
└── ...
```

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

Configure via `.env`:
```env
LOG_LEVEL=INFO
```

---

## 🔒 Security Notes

1. **API Keys**: Never commit `.env` file to git
2. **CORS**: Update `api_server.py` to restrict origins in production
3. **Rate Limits**: Alpha Vantage free tier has API rate limits
4. **Backup Cleanup**: Old backups auto-delete after 30 days

---

## 🐛 Troubleshooting

### Issue: No news articles fetched
**Solution**: Check Alpha Vantage API key and rate limits

### Issue: Groq API errors
**Solution**: Verify Groq API key and model name (`openai/gpt-oss-120b`)

### Issue: Signals not appearing
**Solution**: Wait for initial news fetch cycle (5 minutes) or check logs

### Issue: Port already in use
**Solution**: Change `API_PORT` in `.env` or kill process using port 8000

---

## 📈 Performance

- **News Fetch**: ~2-5 seconds (depends on Alpha Vantage)
- **AI Analysis**: ~10-30 seconds (depends on article count and Groq API)
- **API Response**: <100ms for active signals
- **Memory**: ~50-100MB typical usage
- **Storage**: ~1-5MB per day (backups)

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Add more exchanges and markets
- Enhance AI prompt engineering
- Add technical indicators
- Implement portfolio management
- Add backtesting capabilities
- Create frontend dashboard

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **Alpha Vantage** - Market news data
- **Groq** - AI analysis infrastructure
- **FastAPI** - Modern Python web framework

---

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check logs in `logs/` directory
- Review API documentation above

---

**Built with ❤️ for traders and investors**
