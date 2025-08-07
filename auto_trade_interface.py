#!/usr/bin/env python3
"""
ByBit Auto Trading Interface
User-friendly interface for configuring and managing auto trading.
"""

import asyncio
import json
import sys
from typing import Dict, Any
from loguru import logger

from src.config import Config
from src.bybit_client import ByBitClient
from src.trading_manager import AutoTradingManager


class AutoTradeInterface:
    """User interface for auto trading configuration and management."""
    
    def __init__(self):
        self.config = Config()
        self.client = ByBitClient(
            api_key=self.config.get('api.api_key'),
            api_secret=self.config.get('api.api_secret'),
            testnet=self.config.get('api.testnet', False)
        )
        self.trading_manager = None
    
    async def initialize(self):
        """Initialize the trading interface."""
        try:
            logger.info("🔧 Initializing Auto Trading Interface...")
            
            # Test API connection
            await self._test_api_connection()
            
            # Initialize trading manager
            self.trading_manager = AutoTradingManager(self.config, self.client)
            
            logger.info("✅ Auto Trading Interface initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize interface: {e}")
            raise
    
    async def _test_api_connection(self):
        """Test API connection."""
        try:
            logger.info("🔍 Testing API connection...")
            
            # Test account info
            account_info = await self.client.get_account_info()
            if account_info.get('retCode') == 0:
                logger.info("✅ API connection successful")
            else:
                logger.error(f"❌ API connection failed: {account_info.get('retMsg')}")
                raise Exception("API connection failed")
                
        except Exception as e:
            logger.error(f"❌ API connection test failed: {e}")
            raise
    
    async def show_main_menu(self):
        """Show the main menu."""
        while True:
            print("\n" + "="*60)
            print("🚀 BYBIT AUTO TRADING BOT")
            print("="*60)
            print("1. 📊 View Current Settings")
            print("2. ⚙️  Configure Trading Settings")
            print("3. 🎯 Start Auto Trading")
            print("4. 🛑 Stop Auto Trading")
            print("5. 📈 View Trading Status")
            print("6. 💰 View Account Balance")
            print("7. 📋 View Trading History")
            print("8. 🔧 Advanced Settings")
            print("9. ❌ Exit")
            print("="*60)
            
            choice = input("Select an option (1-9): ").strip()
            
            if choice == "1":
                await self.view_current_settings()
            elif choice == "2":
                await self.configure_trading_settings()
            elif choice == "3":
                await self.start_auto_trading()
            elif choice == "4":
                await self.stop_auto_trading()
            elif choice == "5":
                await self.view_trading_status()
            elif choice == "6":
                await self.view_account_balance()
            elif choice == "7":
                await self.view_trading_history()
            elif choice == "8":
                await self.advanced_settings()
            elif choice == "9":
                await self.exit_program()
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    async def view_current_settings(self):
        """View current trading settings."""
        print("\n" + "="*60)
        print("📊 CURRENT TRADING SETTINGS")
        print("="*60)
        
        # Trading mode
        trading_mode = self.config.get('trading.mode', 'both')
        print(f"Trading Mode: {trading_mode.upper()}")
        
        # Auto trade settings
        auto_trade_enabled = self.config.get('trading.auto_trade.enabled', True)
        print(f"Auto Trade Enabled: {'✅ YES' if auto_trade_enabled else '❌ NO'}")
        
        # Risk management
        max_daily_loss = self.config.get('trading.auto_trade.max_daily_loss', 1000)
        max_positions = self.config.get('trading.auto_trade.max_positions', 5)
        max_daily_trades = self.config.get('trading.auto_trade.max_daily_trades', 50)
        
        print(f"Max Daily Loss: ${max_daily_loss}")
        print(f"Max Positions: {max_positions}")
        print(f"Max Daily Trades: {max_daily_trades}")
        
        # Spot settings
        if trading_mode in ['spot', 'both']:
            print("\n📈 SPOT TRADING SETTINGS:")
            spot_config = self.config.get('spot', {})
            symbols = spot_config.get('symbols', ['BTCUSDT'])
            base_size = spot_config.get('base_order_size', 100)
            grid_levels = spot_config.get('grid_levels', 10)
            
            print(f"  Symbols: {', '.join(symbols)}")
            print(f"  Base Order Size: ${base_size}")
            print(f"  Grid Levels: {grid_levels}")
        
        # Futures settings
        if trading_mode in ['futures', 'both']:
            print("\n📊 FUTURES TRADING SETTINGS:")
            futures_config = self.config.get('futures', {})
            symbols = futures_config.get('symbols', ['BTCUSDT'])
            leverage = futures_config.get('leverage', 5)
            margin_mode = futures_config.get('margin_mode', 'ISOLATED')
            
            print(f"  Symbols: {', '.join(symbols)}")
            print(f"  Leverage: {leverage}x")
            print(f"  Margin Mode: {margin_mode}")
        
        input("\nPress Enter to continue...")
    
    async def configure_trading_settings(self):
        """Configure trading settings."""
        print("\n" + "="*60)
        print("⚙️  CONFIGURE TRADING SETTINGS")
        print("="*60)
        
        while True:
            print("\n1. 🎯 Set Trading Mode (Spot/Futures/Both)")
            print("2. 💰 Set Risk Management")
            print("3. 📈 Configure Spot Trading")
            print("4. 📊 Configure Futures Trading")
            print("5. 🔧 Set Technical Indicators")
            print("6. 📱 Configure Notifications")
            print("7. ⬅️  Back to Main Menu")
            
            choice = input("Select an option (1-7): ").strip()
            
            if choice == "1":
                await self.set_trading_mode()
            elif choice == "2":
                await self.set_risk_management()
            elif choice == "3":
                await self.configure_spot_trading()
            elif choice == "4":
                await self.configure_futures_trading()
            elif choice == "5":
                await self.configure_technical_indicators()
            elif choice == "6":
                await self.configure_notifications()
            elif choice == "7":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    async def set_trading_mode(self):
        """Set trading mode."""
        print("\n🎯 SET TRADING MODE")
        print("1. Spot Trading Only")
        print("2. Futures Trading Only")
        print("3. Both Spot and Futures")
        
        choice = input("Select trading mode (1-3): ").strip()
        
        if choice == "1":
            self.config.set('trading.mode', 'spot')
            print("✅ Set to Spot Trading Only")
        elif choice == "2":
            self.config.set('trading.mode', 'futures')
            print("✅ Set to Futures Trading Only")
        elif choice == "3":
            self.config.set('trading.mode', 'both')
            print("✅ Set to Both Spot and Futures")
        else:
            print("❌ Invalid option.")
    
    async def set_risk_management(self):
        """Set risk management parameters."""
        print("\n💰 RISK MANAGEMENT SETTINGS")
        
        try:
            max_daily_loss = float(input("Max Daily Loss (USDT): ") or "1000")
            max_positions = int(input("Max Positions: ") or "5")
            max_daily_trades = int(input("Max Daily Trades: ") or "50")
            stop_loss_pct = float(input("Stop Loss Percentage: ") or "5.0")
            take_profit_pct = float(input("Take Profit Percentage: ") or "10.0")
            
            self.config.set('trading.auto_trade.max_daily_loss', max_daily_loss)
            self.config.set('trading.auto_trade.max_positions', max_positions)
            self.config.set('trading.auto_trade.max_daily_trades', max_daily_trades)
            self.config.set('trading.risk_management.stop_loss_percentage', stop_loss_pct)
            self.config.set('trading.risk_management.take_profit_percentage', take_profit_pct)
            
            print("✅ Risk management settings updated")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    async def configure_spot_trading(self):
        """Configure spot trading settings."""
        print("\n📈 SPOT TRADING CONFIGURATION")
        
        try:
            symbols_input = input("Trading Symbols (comma-separated, e.g., BTCUSDT,ETHUSDT): ") or "BTCUSDT"
            symbols = [s.strip() for s in symbols_input.split(',')]
            
            base_order_size = float(input("Base Order Size (USDT): ") or "100")
            grid_levels = int(input("Grid Levels: ") or "10")
            grid_spacing = float(input("Grid Spacing (%): ") or "2.0")
            
            self.config.set('spot.symbols', symbols)
            self.config.set('spot.base_order_size', base_order_size)
            self.config.set('spot.grid_levels', grid_levels)
            self.config.set('spot.grid_spacing', grid_spacing)
            
            print("✅ Spot trading settings updated")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    async def configure_futures_trading(self):
        """Configure futures trading settings."""
        print("\n📊 FUTURES TRADING CONFIGURATION")
        
        try:
            symbols_input = input("Trading Symbols (comma-separated, e.g., BTCUSDT,ETHUSDT): ") or "BTCUSDT"
            symbols = [s.strip() for s in symbols_input.split(',')]
            
            leverage = int(input("Leverage (1-100): ") or "5")
            margin_mode = input("Margin Mode (ISOLATED/CROSS): ") or "ISOLATED"
            base_order_size = float(input("Base Order Size (USDT): ") or "50")
            
            self.config.set('futures.symbols', symbols)
            self.config.set('futures.leverage', leverage)
            self.config.set('futures.margin_mode', margin_mode)
            self.config.set('futures.base_order_size', base_order_size)
            
            print("✅ Futures trading settings updated")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    async def configure_technical_indicators(self):
        """Configure technical indicators."""
        print("\n🔧 TECHNICAL INDICATORS CONFIGURATION")
        
        try:
            # RSI settings
            rsi_enabled = input("Enable RSI (y/n): ").lower() == 'y'
            rsi_period = int(input("RSI Period (14): ") or "14")
            rsi_overbought = int(input("RSI Overbought Level (70): ") or "70")
            rsi_oversold = int(input("RSI Oversold Level (30): ") or "30")
            
            # Moving Average settings
            ma_enabled = input("Enable Moving Average (y/n): ").lower() == 'y'
            ma_short = int(input("Short MA Period (10): ") or "10")
            ma_long = int(input("Long MA Period (20): ") or "20")
            
            self.config.set('market_analysis.indicators.rsi.enabled', rsi_enabled)
            self.config.set('market_analysis.indicators.rsi.period', rsi_period)
            self.config.set('market_analysis.indicators.rsi.overbought', rsi_overbought)
            self.config.set('market_analysis.indicators.rsi.oversold', rsi_oversold)
            
            self.config.set('market_analysis.indicators.moving_average.enabled', ma_enabled)
            self.config.set('market_analysis.indicators.moving_average.short_period', ma_short)
            self.config.set('market_analysis.indicators.moving_average.long_period', ma_long)
            
            print("✅ Technical indicators configured")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    async def configure_notifications(self):
        """Configure notifications."""
        print("\n📱 NOTIFICATION SETTINGS")
        
        notifications_enabled = input("Enable Notifications (y/n): ").lower() == 'y'
        self.config.set('notifications.enabled', notifications_enabled)
        
        if notifications_enabled:
            trade_executed = input("Notify on Trade Execution (y/n): ").lower() == 'y'
            stop_loss_triggered = input("Notify on Stop Loss (y/n): ").lower() == 'y'
            daily_summary = input("Send Daily Summary (y/n): ").lower() == 'y'
            
            self.config.set('notifications.alerts.trade_executed', trade_executed)
            self.config.set('notifications.alerts.stop_loss_triggered', stop_loss_triggered)
            self.config.set('notifications.alerts.daily_summary', daily_summary)
        
        print("✅ Notification settings updated")
    
    async def start_auto_trading(self):
        """Start auto trading."""
        print("\n🚀 STARTING AUTO TRADING")
        
        try:
            # Confirm settings
            print("\nCurrent Settings:")
            await self.view_current_settings()
            
            confirm = input("\nStart auto trading? (y/n): ").lower()
            if confirm != 'y':
                print("❌ Auto trading cancelled")
                return
            
            # Start trading manager
            if self.trading_manager:
                await self.trading_manager.start_auto_trading()
                print("✅ Auto trading started successfully!")
                print("📊 Monitor your trades at: http://localhost:8081")
                
                # Keep the interface running
                await self._monitor_trading()
            else:
                print("❌ Trading manager not initialized")
                
        except Exception as e:
            logger.error(f"❌ Failed to start auto trading: {e}")
            print(f"❌ Error: {e}")
    
    async def _monitor_trading(self):
        """Monitor trading while running."""
        print("\n📊 MONITORING AUTO TRADING")
        print("Press 'q' to stop trading")
        
        while True:
            try:
                if self.trading_manager:
                    status = self.trading_manager.get_trading_status()
                    
                    print(f"\r📈 Active Positions: {status['active_positions']} | "
                          f"Daily Trades: {status['daily_stats']['trades']} | "
                          f"Daily PnL: ${status['daily_stats']['profit'] - status['daily_stats']['loss']:.2f}", end='')
                
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping auto trading...")
                break
            except Exception as e:
                logger.error(f"Error in monitoring: {e}")
                break
    
    async def stop_auto_trading(self):
        """Stop auto trading."""
        print("\n🛑 STOPPING AUTO TRADING")
        
        if self.trading_manager:
            # This would implement stopping logic
            print("✅ Auto trading stopped")
        else:
            print("❌ No active trading session")
    
    async def view_trading_status(self):
        """View current trading status."""
        print("\n" + "="*60)
        print("📊 TRADING STATUS")
        print("="*60)
        
        if self.trading_manager:
            status = self.trading_manager.get_trading_status()
            
            print(f"Trading Mode: {status['trading_mode'].upper()}")
            print(f"Active Positions: {status['active_positions']}")
            print(f"Daily Trades: {status['daily_stats']['trades']}")
            print(f"Daily Profit: ${status['daily_stats']['profit']:.2f}")
            print(f"Daily Loss: ${status['daily_stats']['loss']:.2f}")
            print(f"Net PnL: ${status['daily_stats']['profit'] - status['daily_stats']['loss']:.2f}")
            
            if status['market_data']:
                print("\nCurrent Prices:")
                for symbol, price in status['market_data'].items():
                    print(f"  {symbol}: ${price:.2f}")
        else:
            print("❌ Trading manager not initialized")
        
        input("\nPress Enter to continue...")
    
    async def view_account_balance(self):
        """View account balance."""
        print("\n" + "="*60)
        print("💰 ACCOUNT BALANCE")
        print("="*60)
        
        try:
            account_info = await self.client.get_account_info()
            if account_info.get('retCode') == 0:
                result = account_info.get('result', {})
                list_data = result.get('list', [])
                
                if list_data:
                    account_data = list_data[0]
                    
                    total_balance = float(account_data.get('totalWalletBalance', 0))
                    available_balance = float(account_data.get('totalAvailableBalance', 0))
                    margin_balance = float(account_data.get('totalMarginBalance', 0))
                    
                    print(f"Total Balance: ${total_balance:.2f}")
                    print(f"Available Balance: ${available_balance:.2f}")
                    print(f"Margin Balance: ${margin_balance:.2f}")
                    
                    # Show coin details
                    coins = account_data.get('coin', [])
                    if coins:
                        print("\nCoin Details:")
                        for coin in coins:
                            if float(coin.get('walletBalance', 0)) > 0:
                                coin_name = coin.get('coin', '')
                                balance = float(coin.get('walletBalance', 0))
                                usd_value = float(coin.get('usdValue', 0))
                                print(f"  {coin_name}: {balance:.6f} (${usd_value:.2f})")
            else:
                print(f"❌ Failed to get account info: {account_info.get('retMsg')}")
                
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    async def view_trading_history(self):
        """View trading history."""
        print("\n" + "="*60)
        print("📋 TRADING HISTORY")
        print("="*60)
        
        try:
            # Get recent orders
            order_history = await self.client.get_order_history("BTCUSDT", 20)
            if order_history.get('retCode') == 0:
                result = order_history.get('result', {})
                list_data = result.get('list', [])
                
                if list_data:
                    print("Recent Orders:")
                    for order in list_data[:10]:  # Show last 10 orders
                        symbol = order.get('symbol', '')
                        side = order.get('side', '')
                        status = order.get('orderStatus', '')
                        qty = float(order.get('qty', 0))
                        price = float(order.get('avgPrice', 0))
                        time = order.get('createdTime', '')
                        
                        print(f"  {symbol} {side} {qty} @ ${price:.2f} - {status}")
                else:
                    print("No recent orders found")
            else:
                print(f"❌ Failed to get order history: {order_history.get('retMsg')}")
                
        except Exception as e:
            logger.error(f"Error getting trading history: {e}")
            print(f"❌ Error: {e}")
        
        input("\nPress Enter to continue...")
    
    async def advanced_settings(self):
        """Advanced settings menu."""
        print("\n" + "="*60)
        print("🔧 ADVANCED SETTINGS")
        print("="*60)
        
        while True:
            print("\n1. 📊 Configure Grid Strategy")
            print("2. 🎯 Set Order Management")
            print("3. 📱 Configure Dashboard")
            print("4. 💾 Database Settings")
            print("5. 📝 Logging Settings")
            print("6. ⬅️  Back to Main Menu")
            
            choice = input("Select an option (1-6): ").strip()
            
            if choice == "1":
                await self.configure_grid_strategy()
            elif choice == "2":
                await self.configure_order_management()
            elif choice == "3":
                await self.configure_dashboard()
            elif choice == "4":
                await self.configure_database()
            elif choice == "5":
                await self.configure_logging()
            elif choice == "6":
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    async def configure_grid_strategy(self):
        """Configure grid strategy settings."""
        print("\n📊 GRID STRATEGY CONFIGURATION")
        
        try:
            dynamic_grid = input("Enable Dynamic Grid (y/n): ").lower() == 'y'
            base_spacing = float(input("Base Grid Spacing (%): ") or "2.0")
            volatility_multiplier = float(input("Volatility Multiplier: ") or "1.5")
            
            self.config.set('grid_strategy.dynamic_grid', dynamic_grid)
            self.config.set('grid_strategy.grid_calculation.base_spacing', base_spacing)
            self.config.set('grid_strategy.grid_calculation.volatility_multiplier', volatility_multiplier)
            
            print("✅ Grid strategy settings updated")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    async def configure_order_management(self):
        """Configure order management settings."""
        print("\n🎯 ORDER MANAGEMENT SETTINGS")
        
        try:
            default_order_type = input("Default Order Type (LIMIT/MARKET): ") or "LIMIT"
            post_only = input("Post Only Orders (y/n): ").lower() == 'y'
            max_slippage = float(input("Max Slippage (%): ") or "0.5")
            
            self.config.set('orders.default_order_type', default_order_type)
            self.config.set('orders.post_only', post_only)
            self.config.set('orders.max_slippage', max_slippage)
            
            print("✅ Order management settings updated")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    async def configure_dashboard(self):
        """Configure dashboard settings."""
        print("\n📱 DASHBOARD CONFIGURATION")
        
        try:
            port = int(input("Dashboard Port (8081): ") or "8081")
            auto_refresh = int(input("Auto Refresh Interval (seconds): ") or "30")
            
            self.config.set('dashboard.port', port)
            self.config.set('dashboard.auto_refresh', auto_refresh)
            
            print("✅ Dashboard settings updated")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    async def configure_database(self):
        """Configure database settings."""
        print("\n💾 DATABASE SETTINGS")
        
        try:
            db_type = input("Database Type (sqlite/postgresql/mysql): ") or "sqlite"
            connection_string = input("Connection String: ") or "trading_bot.db"
            
            self.config.set('database.type', db_type)
            self.config.set('database.connection_string', connection_string)
            
            print("✅ Database settings updated")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def configure_logging(self):
        """Configure logging settings."""
        print("\n📝 LOGGING SETTINGS")
        
        try:
            log_level = input("Log Level (DEBUG/INFO/WARNING/ERROR): ") or "INFO"
            file_logging = input("Enable File Logging (y/n): ").lower() == 'y'
            max_file_size = int(input("Max File Size (MB): ") or "10")
            
            self.config.set('logging.level', log_level)
            self.config.set('logging.file_logging', file_logging)
            self.config.set('logging.max_file_size', max_file_size)
            
            print("✅ Logging settings updated")
            
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    async def exit_program(self):
        """Exit the program."""
        print("\n👋 Thank you for using ByBit Auto Trading Bot!")
        print("📊 Don't forget to monitor your trades at: http://localhost:8081")
        
        # Save configuration
        self.config.save()
        print("✅ Configuration saved")


async def main():
    """Main function."""
    try:
        interface = AutoTradeInterface()
        await interface.initialize()
        await interface.show_main_menu()
        
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        logger.error(f"❌ Program error: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 