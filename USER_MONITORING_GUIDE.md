# 🤖 ByBit Grid Trading Bot - User Monitoring Guide

## 📊 How to Monitor Your Bot

There are **3 different ways** to monitor your trading bot:

---

## 🖥️ Method 1: Terminal Monitoring (Simple)

### Quick Status Check
```bash
python monitor_bot.py
```

**What you'll see:**
- Current BTC price
- Account balance
- Active positions
- Total PnL and daily PnL
- Trade count
- System performance
- Grid analysis

**Features:**
- ✅ Single status check
- ✅ Continuous monitoring (30s intervals)
- ✅ Real-time updates
- ✅ Easy to use

---

## 🌐 Method 2: Web Dashboard (Recommended)

### Start Web Dashboard
```bash
python web_dashboard.py
```

### Access Dashboard
1. Open your web browser
2. Go to: `http://localhost:8080`
3. Enjoy beautiful real-time dashboard!

**What you'll see:**
- 💰 **Market Info**: Current BTC price, last updated
- 💳 **Account**: Balance, available funds
- 📈 **Trading**: Total PnL, daily PnL, trade count, active positions
- 🎯 **Strategy**: Cover loss multiplier, consecutive losses, grid levels
- 💻 **System**: CPU usage, memory usage, uptime

**Features:**
- ✅ Beautiful web interface
- ✅ Auto-refresh every 30 seconds
- ✅ Color-coded PnL (green for profit, red for loss)
- ✅ Mobile-friendly design
- ✅ Real-time data updates

---

## 📝 Method 3: Log Files (Advanced)

### View Logs
```bash
# View real-time logs
tail -f bot.log

# View last 100 lines
tail -n 100 bot.log

# Search for errors
grep "ERROR" bot.log

# Search for trades
grep "position" bot.log
```

### Log File Locations
- **Main log**: `bot.log`
- **System logs**: Check your system's log directory
- **Redis data**: Available via Redis CLI

---

## 📱 Mobile Monitoring

### Web Dashboard on Mobile
1. Start the web dashboard: `python web_dashboard.py`
2. Find your computer's IP address
3. On your phone, go to: `http://YOUR_IP:8080`
4. Bookmark the page for easy access

### Terminal Monitoring on Mobile
Use SSH apps like:
- **Termius** (iOS/Android)
- **JuiceSSH** (Android)
- **iTerm2** (iOS)

Then run: `python monitor_bot.py`

---

## 🔍 What to Monitor

### ✅ **Good Signs:**
- ✅ Bot is running without errors
- ✅ PnL is positive (green)
- ✅ Active positions are reasonable
- ✅ System resources are normal
- ✅ Grid levels are appropriate for current price

### ⚠️ **Warning Signs:**
- ⚠️ High consecutive losses
- ⚠️ Cover loss multiplier > 2.0x
- ⚠️ Daily PnL approaching loss limit
- ⚠️ High CPU/memory usage
- ⚠️ No price updates for >60 seconds

### 🚨 **Emergency Signs:**
- 🚨 Bot stopped responding
- 🚨 Daily loss limit exceeded
- 🚨 System errors in logs
- 🚨 API connection failures

---

## 🛠️ Troubleshooting

### Bot Not Responding
```bash
# Check if bot is running
ps aux | grep python

# Restart the bot
python run.py
```

### Can't Access Web Dashboard
```bash
# Check if port 8080 is in use
netstat -an | grep 8080

# Try different port
# Edit web_dashboard.py and change port number
```

### Logs Not Updating
```bash
# Check log file permissions
ls -la bot.log

# Check disk space
df -h
```

---

## 📊 Performance Metrics

### Trading Metrics
- **Total PnL**: Overall profit/loss
- **Daily PnL**: Today's profit/loss
- **Trade Count**: Number of completed trades
- **Active Positions**: Current open positions
- **Cover Loss Multiplier**: Position size multiplier after losses

### System Metrics
- **CPU Usage**: Should be <80%
- **Memory Usage**: Should be <90%
- **Uptime**: How long bot has been running
- **Network I/O**: Data transfer rates

### Grid Metrics
- **Grid Levels**: Number of price levels
- **Grid Range**: Price range covered
- **Nearest Level**: Closest grid level to current price
- **Distance to Grid**: How far price is from grid level

---

## 🔔 Alerts and Notifications

### Automatic Alerts
The bot automatically logs:
- 🚨 Error messages
- ⚠️ Warning messages
- 📊 Performance metrics
- 💰 Trade executions

### Manual Alerts
Set up notifications for:
- Daily PnL changes
- Large position changes
- System resource usage
- API connection status

---

## 📈 Best Practices

### Daily Monitoring
1. **Morning**: Check overnight performance
2. **Midday**: Monitor active positions
3. **Evening**: Review daily PnL

### Weekly Review
1. **Performance**: Analyze weekly PnL
2. **Settings**: Review grid levels and risk parameters
3. **System**: Check system health and logs

### Monthly Analysis
1. **Strategy**: Evaluate grid strategy performance
2. **Risk**: Review risk management settings
3. **Optimization**: Adjust parameters based on results

---

## 🆘 Emergency Procedures

### Stop the Bot
```bash
# Graceful shutdown
Ctrl+C

# Force stop
pkill -f "python run.py"
```

### Emergency Contact
- Check logs for error details
- Review system resources
- Verify API credentials
- Restart bot if necessary

---

## 📱 Quick Commands

### Start Monitoring
```bash
# Terminal monitoring
python monitor_bot.py

# Web dashboard
python web_dashboard.py

# View logs
tail -f bot.log
```

### Check Status
```bash
# Quick test
python test_bot.py

# Check configuration
cat config.yaml
```

### Emergency Stop
```bash
# Stop bot
Ctrl+C

# Kill process
pkill -f "python run.py"
```

---

## 🎯 Monitoring Checklist

### Daily Checklist
- [ ] Bot is running
- [ ] No error messages in logs
- [ ] PnL is reasonable
- [ ] System resources are normal
- [ ] Grid levels are appropriate

### Weekly Checklist
- [ ] Review performance metrics
- [ ] Check system health
- [ ] Analyze trading patterns
- [ ] Update risk parameters if needed

### Monthly Checklist
- [ ] Comprehensive performance review
- [ ] Strategy optimization
- [ ] System maintenance
- [ ] Backup configuration

---

**Remember: Regular monitoring is key to successful bot trading!** 🚀 