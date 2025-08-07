# 🚀 ByBit Auto Trading Bot - Complete Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Trading Modes](#trading-modes)
4. [Configuration](#configuration)
5. [Risk Management](#risk-management)
6. [Technical Indicators](#technical-indicators)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

## 🎯 Overview

This ByBit Auto Trading Bot supports both **Spot Trading** and **Futures Trading** with comprehensive risk management and technical analysis.

### Key Features:
- ✅ **Dual Mode Trading**: Spot and Futures
- ✅ **Grid Trading Strategy**: Automated buy/sell orders
- ✅ **Risk Management**: Stop-loss, take-profit, daily limits
- ✅ **Technical Indicators**: RSI, Moving Averages, Bollinger Bands
- ✅ **Real-time Monitoring**: Web dashboard and terminal interface
- ✅ **Auto Recovery**: Automatic reconnection and error handling

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
Edit `config.yaml`:
```yaml
api:
  api_key: "YOUR_API_KEY"
  api_secret: "YOUR_API_SECRET"
  testnet: false  # Set to true for testing
```

### 3. Start Auto Trading Interface
```bash
python auto_trade_interface.py
```

### 4. Access Web Dashboard
Open browser: `http://localhost:8081`

## 📊 Trading Modes

### 🎯 Mode Selection

#### 1. Spot Trading Only
- **Best for**: Beginners, conservative traders
- **Risk**: Lower (no leverage)
- **Capital**: Full amount required
- **Settings**:
  ```yaml
  trading:
    mode: "spot"
  spot:
    enabled: true
    symbols: ["BTCUSDT", "ETHUSDT"]
    base_order_size: 100  # USDT
    grid_levels: 10
    grid_spacing: 2.0  # %
  ```

#### 2. Futures Trading Only
- **Best for**: Experienced traders, higher returns
- **Risk**: Higher (leverage involved)
- **Capital**: Margin required
- **Settings**:
  ```yaml
  trading:
    mode: "futures"
  futures:
    enabled: true
    symbols: ["BTCUSDT", "ETHUSDT"]
    leverage: 5
    margin_mode: "ISOLATED"
    base_order_size: 50  # USDT
  ```

#### 3. Both Spot and Futures
- **Best for**: Diversified strategy
- **Risk**: Balanced
- **Capital**: Both spot and margin
- **Settings**:
  ```yaml
  trading:
    mode: "both"
  ```

## ⚙️ Configuration

### 🎯 Trading Settings

#### Auto Trade Configuration
```yaml
trading:
  auto_trade:
    enabled: true
    max_positions: 5
    max_daily_trades: 50
    max_daily_loss: 1000  # USDT
```

#### Risk Management
```yaml
risk_management:
  max_position_size: 0.1  # BTC
  max_leverage: 10
  stop_loss_percentage: 5.0
  take_profit_percentage: 10.0
  trailing_stop: true
  trailing_stop_distance: 2.0  # %
```

### 📈 Spot Trading Configuration

#### Basic Settings
```yaml
spot:
  enabled: true
  symbols: ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
  base_order_size: 100  # USDT
  grid_levels: 10
  grid_spacing: 2.0  # %
```

#### Advanced Settings
```yaml
spot:
  auto_rebalance: true
  rebalance_threshold: 5.0  # %
  use_margin: false
  max_margin_ratio: 0.8
```

### 📊 Futures Trading Configuration

#### Basic Settings
```yaml
futures:
  enabled: true
  symbols: ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
  base_order_size: 50  # USDT
  grid_levels: 15
  grid_spacing: 1.5  # %
  leverage: 5
```

#### Advanced Settings
```yaml
futures:
  margin_mode: "ISOLATED"  # ISOLATED or CROSS
  auto_leverage: true
  max_leverage: 10
  funding_rate_threshold: 0.01  # 1%
  hedging:
    enabled: true
    hedge_ratio: 0.5  # 50% hedge
```

## 💰 Risk Management

### 🛡️ Daily Limits
```yaml
trading:
  auto_trade:
    max_daily_loss: 1000  # USDT
    max_daily_trades: 50
    max_positions: 5
```

### 📊 Position Sizing
```yaml
grid_strategy:
  position_management:
    max_positions_per_symbol: 3
    position_sizing: "fixed"  # fixed, percentage, kelly
    position_size_percentage: 10.0  # % of available balance
```

### 🎯 Stop Loss & Take Profit
```yaml
risk_management:
  stop_loss_percentage: 5.0
  take_profit_percentage: 10.0
  trailing_stop: true
  trailing_stop_distance: 2.0  # %
```

### 🔄 Cover Loss Strategy
```yaml
grid_strategy:
  cover_loss:
    enabled: true
    multiplier: 1.5
    max_multiplier: 5.0
    reset_threshold: 3  # consecutive wins
```

## 📈 Technical Indicators

### 🔧 RSI (Relative Strength Index)
```yaml
market_analysis:
  indicators:
    rsi:
      enabled: true
      period: 14
      overbought: 70
      oversold: 30
```

**Usage**:
- **Oversold (< 30)**: Buy signal
- **Overbought (> 70)**: Sell signal
- **Neutral (30-70)**: No signal

### 📊 Moving Averages
```yaml
market_analysis:
  indicators:
    moving_average:
      enabled: true
      short_period: 10
      long_period: 20
      type: "SMA"  # SMA, EMA, WMA
```

**Usage**:
- **Golden Cross**: Short MA > Long MA = Buy
- **Death Cross**: Short MA < Long MA = Sell

### 📈 Bollinger Bands
```yaml
market_analysis:
  indicators:
    bollinger_bands:
      enabled: true
      period: 20
      std_dev: 2
```

**Usage**:
- **Price at Lower Band**: Buy signal
- **Price at Upper Band**: Sell signal
- **Price in Middle**: Neutral

### 📊 Volume Profile
```yaml
market_analysis:
  indicators:
    volume_profile:
      enabled: true
      period: 24
```

## 📱 Monitoring

### 🌐 Web Dashboard
Access: `http://localhost:8081`

**Features**:
- Real-time price charts
- Order book visualization
- Position monitoring
- Performance metrics
- Risk management alerts

### 💻 Terminal Interface
Run: `python auto_trade_interface.py`

**Features**:
- Interactive configuration
- Real-time status monitoring
- Account balance viewing
- Trading history
- Advanced settings

### 📊 Monitoring Commands

#### Check Trading Status
```bash
curl http://localhost:8081/api/status
```

#### View Account Balance
```bash
curl http://localhost:8081/api/account
```

#### Get Trading History
```bash
curl http://localhost:8081/api/trade-history
```

## 🔧 Advanced Configuration

### 📊 Grid Strategy
```yaml
grid_strategy:
  dynamic_grid: true
  volatility_threshold: 5.0  # %
  grid_calculation:
    method: "percentage"  # percentage, fixed, atr
    base_spacing: 2.0  # %
    volatility_multiplier: 1.5
```

### 🎯 Order Management
```yaml
orders:
  default_order_type: "LIMIT"
  market_orders: false
  post_only: true
  time_in_force: "GTC"  # GTC, IOC, FOK
  order_timeout: 30  # seconds
  max_slippage: 0.5  # %
  price_deviation: 1.0  # %
```

### 📱 Notifications
```yaml
notifications:
  enabled: true
  alerts:
    trade_executed: true
    position_closed: true
    stop_loss_triggered: true
    take_profit_triggered: true
    daily_summary: true
    error_notifications: true
```

## 🛠️ Troubleshooting

### ❌ Common Issues

#### 1. API Connection Error
**Error**: `"error sign! origin_string"`
**Solution**: 
- Check API key and secret
- Verify API permissions
- Ensure correct testnet setting

#### 2. Insufficient Balance
**Error**: `"insufficient balance"`
**Solution**:
- Check account balance
- Reduce position size
- Verify margin requirements

#### 3. Rate Limit Exceeded
**Error**: `"rate limit exceeded"`
**Solution**:
- Reduce trading frequency
- Increase request intervals
- Check API limits

#### 4. Order Rejection
**Error**: `"order rejected"`
**Solution**:
- Check symbol availability
- Verify order parameters
- Ensure sufficient balance

### 🔧 Debug Commands

#### Check API Status
```bash
python -c "
import asyncio
from src.bybit_client import ByBitClient
from src.config import Config

async def test_api():
    config = Config()
    client = ByBitClient(config.get('api.api_key'), config.get('api.api_secret'))
    result = await client.get_account_info()
    print(f'API Status: {result}')

asyncio.run(test_api())
"
```

#### Test Trading Interface
```bash
python auto_trade_interface.py
```

#### Check Logs
```bash
tail -f trading_bot.log
```

## 📋 Best Practices

### 🎯 For Beginners
1. **Start with Spot Trading**: Lower risk, easier to understand
2. **Use Small Position Sizes**: Start with 1-5% of capital
3. **Enable All Risk Limits**: Set conservative daily loss limits
4. **Monitor Regularly**: Check dashboard daily
5. **Test on Testnet**: Practice before live trading

### 📊 For Experienced Traders
1. **Use Futures for Leverage**: Higher potential returns
2. **Implement Hedging**: Reduce portfolio risk
3. **Dynamic Grid Spacing**: Adapt to market volatility
4. **Advanced Indicators**: Combine multiple signals
5. **Custom Risk Management**: Tailor to your strategy

### 🛡️ Risk Management Tips
1. **Never Risk More Than 2%**: Per trade
2. **Set Daily Loss Limits**: Stick to them
3. **Use Stop Losses**: Always protect capital
4. **Diversify Symbols**: Don't put all eggs in one basket
5. **Monitor Market Conditions**: Adjust strategy accordingly

## 📞 Support

### 🔗 Useful Links
- **ByBit API Documentation**: https://bybit-exchange.github.io/docs/v5/intro
- **Web Dashboard**: http://localhost:8081
- **Configuration File**: `config.yaml`
- **Log File**: `trading_bot.log`

### 📧 Contact
For issues or questions:
1. Check the troubleshooting section
2. Review logs in `trading_bot.log`
3. Test API connection
4. Verify configuration settings

---

**⚠️ Disclaimer**: This bot is for educational purposes. Always test thoroughly before using with real money. Trading cryptocurrencies involves risk of loss. 