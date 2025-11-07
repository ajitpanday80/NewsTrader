# 🚀 Quick Start Guide

Get NewsTrader up and running in 5 minutes!

## ⚡ Fast Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
ALPHA_VANTAGE_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

**Get API Keys:**
- Alpha Vantage: https://www.alphavantage.co/support/#api-key (FREE)
- Groq: https://console.groq.com/keys (FREE)

### 3. Run the System

```bash
python -m src.main --api
```

That's it! 🎉

## 📊 Access Your Signals

### Via API
Open browser: http://localhost:8000

### Get Active Signals
```bash
curl http://localhost:8000/signals
```

### Get Summary Only
```bash
curl http://localhost:8000/signals/summary
```

### Filter by Market
```bash
curl http://localhost:8000/signals/by-market?market=Crypto
```

## 🔍 What's Happening?

1. **Every 5 minutes**: System fetches latest market news
2. **AI Analysis**: Groq analyzes news and generates signals
3. **Active Signals**: Available via API for 30 minutes
4. **Auto-Backup**: Signals backed up before expiry
5. **Auto-Cleanup**: Old signals removed after 30 minutes

## 📱 Example Frontend Code

```javascript
// Fetch and display signals
async function getSignals() {
  const response = await fetch('http://localhost:8000/signals');
  const data = await response.json();

  if (data.status === 'success') {
    const signals = data.data;

    signals.news_articles.forEach(article => {
      console.log(`📰 ${article.title}`);
      console.log(`🔗 ${article.url}`);

      article.trading_signals.forEach(signal => {
        console.log(`
          ${signal.signal} ${signal.ticker}
          Exchange: ${signal.exchange}
          Confidence: ${signal.confidence}
          Reasoning: ${signal.reasoning}
        `);
      });
    });
  }
}

getSignals();
```

## 🎯 What You Get

Each signal includes:
- ✅ **BUY/SELL/HOLD** recommendation
- ✅ **Confidence score** (0-1)
- ✅ **Exchange & Market** info
- ✅ **AI Reasoning** for the signal
- ✅ **Risk factors** to consider
- ✅ **Catalysts** supporting the signal
- ✅ **News article link** (source)
- ✅ **Time remaining** before expiry

## 📂 Output Location

- **Active signals**: `data/active/current_signals.json`
- **Backups**: `data/backups/YYYY-MM-DD/`
- **Logs**: `logs/newstrader_YYYY-MM-DD.log`

## 🐛 Troubleshooting

### No signals appearing?
Wait 5 minutes for first news fetch or check logs:
```bash
tail -f logs/newstrader_*.log
```

### API not working?
Check if service is running:
```bash
curl http://localhost:8000/health
```

### Port 8000 in use?
Change port in `.env`:
```env
API_PORT=8001
```

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Run [example_usage.py](example_usage.py) for code examples
- Explore API at http://localhost:8000/docs (Swagger UI)
- Check [API endpoints](README.md#-api-endpoints) for filtering options

## 💡 Pro Tips

1. **Test with example script first**:
   ```bash
   python example_usage.py
   ```

2. **Monitor logs in real-time**:
   ```bash
   tail -f logs/newstrader_*.log
   ```

3. **Check system stats**:
   ```bash
   curl http://localhost:8000/stats
   ```

4. **View historical signals**:
   ```bash
   curl http://localhost:8000/signals/history?limit=5
   ```

---

**Need Help?** Check the full [README.md](README.md) or review logs in `logs/` directory.
