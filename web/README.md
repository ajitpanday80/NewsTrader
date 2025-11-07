# NewsTrader Web Dashboard

Beautiful, elegant web interface for displaying trading signals from NewsTrader API.

## 🎨 Features

- ✅ **Clean & Elegant Design** - Dark theme, no headers/logos, pure signal display
- ✅ **Exchange-Based Organization** - Signals grouped by exchange (NYSE, NASDAQ, NSE, BSE, etc.)
- ✅ **Auto-Refresh** - Background refresh every 30 seconds for live updates
- ✅ **Real-Time Status** - Shows last update time, signals remaining, total count
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **News Links** - Direct links to source articles
- ✅ **Signal Details** - Confidence, reasoning, risk factors, and more
- ✅ **Remote Deployment Ready** - Works on any PHP web server

---

## 📦 What's Included

```
web/
├── index.php              # Main dashboard page
├── config.php             # Configuration file
├── assets/
│   ├── css/
│   │   └── style.css      # Beautiful styling
│   └── js/
│       └── app.js         # Data fetching & auto-refresh
└── README.md              # This file
```

---

## 🚀 Quick Deployment

### **Option 1: Local Testing**

1. **Start NewsTrader API** (if not running):
   ```bash
   cd /path/to/NewsTrader
   python -m src.main --api
   ```

2. **Start PHP built-in server**:
   ```bash
   cd web
   php -S localhost:8080
   ```

3. **Open in browser**:
   ```
   http://localhost:8080
   ```

### **Option 2: Remote Web Server**

1. **Upload files to your web server**:
   ```bash
   # Via FTP, SFTP, or cPanel File Manager
   # Upload all files in web/ directory
   ```

2. **Configure API connection**:
   Edit `config.php`:
   ```php
   define('API_BASE_URL', 'http://your-api-server.com:8000');
   define('API_KEY', 'your-api-key-here');
   ```

3. **Set proper permissions**:
   ```bash
   chmod 644 config.php
   chmod 644 index.php
   chmod -R 755 assets/
   ```

4. **Access your dashboard**:
   ```
   http://your-domain.com/
   ```

---

## ⚙️ Configuration

Edit `config.php` to customize settings:

```php
// API Configuration
define('API_BASE_URL', 'http://localhost:8000');  // Your API URL
define('API_KEY', 'your-api-key-here');           // Your API key

// Refresh interval in seconds (default: 30)
define('REFRESH_INTERVAL', 30);

// Timezone for timestamps
date_default_timezone_set('UTC');
```

### **Important Settings:**

- **API_BASE_URL**: URL where your NewsTrader API is running
  - Local: `http://localhost:8000`
  - Remote: `http://your-server-ip:8000` or `https://api.yourdomain.com`

- **API_KEY**: The API key from your NewsTrader `.env` file

- **REFRESH_INTERVAL**: How often to check for new signals (in seconds)
  - Default: 30 seconds
  - Recommended: 15-60 seconds

---

## 🌐 Deployment Scenarios

### **Scenario 1: Both API and Web on Same Server**

```
Server: Ubuntu 20.04
API: http://localhost:8000
Web: Apache/Nginx serving from /var/www/html

Config:
  API_BASE_URL = 'http://localhost:8000'
```

### **Scenario 2: Separate Servers**

```
API Server: 192.168.1.10:8000
Web Server: your-domain.com

Config:
  API_BASE_URL = 'http://192.168.1.10:8000'
```

### **Scenario 3: API Behind Reverse Proxy**

```
API: Internal port 8000
Nginx: Proxies api.yourdomain.com → localhost:8000

Config:
  API_BASE_URL = 'https://api.yourdomain.com'
```

---

## 📋 Requirements

- **PHP**: 7.0 or higher
- **Web Server**: Apache, Nginx, or any PHP-capable server
- **NewsTrader API**: Running and accessible
- **Browser**: Modern browser (Chrome, Firefox, Safari, Edge)

---

## 🎨 Customization

### **Change Colors**

Edit `assets/css/style.css`, modify CSS variables:

```css
:root {
    --bg-primary: #0f1419;      /* Main background */
    --color-buy: #10b981;       /* BUY signal color */
    --color-sell: #ef4444;      /* SELL signal color */
    --color-hold: #f59e0b;      /* HOLD signal color */
}
```

### **Change Refresh Interval**

Edit `config.php`:

```php
define('REFRESH_INTERVAL', 60);  // 60 seconds
```

### **Add Custom Header**

Edit `index.php`, add before `<div class="container">`:

```html
<header class="custom-header">
    <h1>My Trading Dashboard</h1>
</header>
```

---

## 🔒 Security Best Practices

1. **Protect config.php**:
   ```apache
   # Add to .htaccess
   <Files "config.php">
       Order Allow,Deny
       Deny from all
   </Files>
   ```

2. **Use HTTPS** in production:
   ```php
   define('API_BASE_URL', 'https://api.yourdomain.com');
   ```

3. **Restrict API access** by IP (in NewsTrader API):
   ```python
   # In api_server.py, add IP whitelist middleware
   ```

4. **Keep API key secret**:
   - Never commit `config.php` with real API key
   - Use environment variables in production

---

## 🐛 Troubleshooting

### **Problem: "Unable to Load Signals"**

**Solutions:**
1. Check API is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Verify API key in `config.php`

3. Check browser console for errors (F12 → Console)

4. Test API directly:
   ```bash
   curl -H "X-API-Key: your-key" http://localhost:8000/signals
   ```

### **Problem: No signals showing**

**Solutions:**
1. Wait for NewsTrader to fetch news (runs every 5 minutes)

2. Check API endpoint:
   ```bash
   curl -H "X-API-Key: your-key" http://localhost:8000/signals
   ```

3. Look for "No Active Signals" message (this is normal if no recent news)

### **Problem: CORS errors**

**Solution:** NewsTrader API already allows all origins. If still issues:

Edit `src/api_server.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://your-domain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Problem: Page not auto-refreshing**

**Solutions:**
1. Check browser console for JavaScript errors

2. Verify `REFRESH_INTERVAL` in `config.php`

3. Check API is accessible from browser

---

## 📱 Mobile Support

The dashboard is fully responsive:

- ✅ Works on phones and tablets
- ✅ Touch-friendly interface
- ✅ Optimized for small screens
- ✅ Swipeable exchange tabs

---

## 🎯 Features Breakdown

### **Status Bar**
- Last update timestamp
- Time remaining for current signals
- Total signal count
- Connection status indicator

### **Exchange Tabs**
- Click to switch between exchanges
- Shows signal count per exchange
- Auto-selects first exchange

### **Signal Cards**
Each card displays:
- Ticker symbol and name
- BUY/SELL/HOLD badge
- Exchange and market info
- Confidence score with progress bar
- AI reasoning/analysis
- Entry strategy and timeframe
- Link to source news article

### **Auto-Refresh**
- Background refresh every 30 seconds
- No page reload required
- Smooth transitions
- Maintains selected exchange

---

## 🚀 Production Deployment Checklist

- [ ] Upload all files to web server
- [ ] Edit `config.php` with production API URL
- [ ] Add production API key to `config.php`
- [ ] Set proper file permissions (644 for PHP, 755 for directories)
- [ ] Test API connection from browser
- [ ] Enable HTTPS (recommended)
- [ ] Add `.htaccess` to protect `config.php`
- [ ] Test on mobile devices
- [ ] Monitor browser console for errors
- [ ] Verify auto-refresh is working

---

## 📊 Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## 💡 Tips

1. **Bookmark the page** for quick access

2. **Keep tab open** to see live updates

3. **Use fullscreen mode** (F11) for clean view

4. **Check logs** if issues occur:
   - Browser Console (F12)
   - PHP error logs
   - NewsTrader API logs

5. **Monitor API health**:
   ```bash
   curl http://your-api:8000/health
   ```

---

## 🔗 Related Links

- [NewsTrader Main Documentation](../README.md)
- [NewsTrader API Endpoints](../README.md#-api-endpoints)
- [Quick Start Guide](../QUICKSTART.md)

---

## 📝 License

Same as NewsTrader main project - MIT License

---

**Enjoy your beautiful trading signal dashboard!** 📈
