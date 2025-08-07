# Quick Start Guide - ByBit Grid Trading Bot

## 🚀 Immediate Setup

Your API credentials have been configured. Here's how to get started:

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test the Bot (RECOMMENDED FIRST)
```bash
python test_bot.py
```
This will test all components before live trading.

### 3. Run the Bot
```bash
python run.py
```

## ⚠️ IMPORTANT SAFETY NOTES

### Before Live Trading:
1. **Test on Testnet First**: Change `testnet: true` in config.yaml
2. **Start Small**: Use small position sizes (0.001 BTC)
3. **Monitor Closely**: Watch the bot for the first few hours
4. **Set Risk Limits**: Adjust max_daily_loss and max_position_loss

### Current Configuration:
- **Symbol**: BTCUSDT
- **Leverage**: 10x
- **Position Size**: 0.01 BTC (adjust this!)
- **Grid Range**: $40,000 - $50,000
- **Grid Levels**: 20 levels

## 🔧 Quick Configuration Changes

### For Testing (Safe):
```yaml
api:
  testnet: true  # Use testnet
trading:
  position_size: 0.001  # Smaller position size
risk:
  max_daily_loss: 50    # Lower risk
  max_position_loss: 25  # Lower risk
```

### For Live Trading:
```yaml
api:
  testnet: false  # Live trading
trading:
  position_size: 0.01   # Your preferred size
risk:
  max_daily_loss: 100   # Your risk tolerance
  max_position_loss: 50  # Your risk tolerance
```

## 📊 Monitoring

### View Logs:
```bash
tail -f bot.log
```

### Check Status:
The bot logs performance metrics every 30 seconds.

## 🛑 Emergency Stop

If you need to stop the bot immediately:
```bash
# Press Ctrl+C in the terminal
# Or kill the process
```

## 📈 Performance Tracking

The bot tracks:
- Total PnL
- Daily PnL
- Trade count
- Active positions
- Cover loss multiplier

## 🔍 Troubleshooting

### Common Issues:
1. **API Error**: Check your API permissions
2. **Connection Error**: Check internet connection
3. **Position Error**: Check account balance

### Debug Mode:
```yaml
logging:
  level: "DEBUG"
```

## 🎯 Next Steps

1. **Test thoroughly** on testnet first
2. **Start with small amounts** in live trading
3. **Monitor performance** closely
4. **Adjust parameters** based on results
5. **Scale up gradually** once confident

## 📞 Support

- Check logs for detailed error messages
- Review the README.md for full documentation
- Test all components before live trading

**Remember: Start small and test thoroughly!** 