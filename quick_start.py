#!/usr/bin/env python3
"""
ByBit Auto Trading Bot - Quick Start Script
Easy setup and configuration for auto trading.
"""

import asyncio
import os
import sys
from typing import Dict, Any
from loguru import logger

def print_banner():
    """Print welcome banner."""
    print("\n" + "="*60)
    print("🚀 BYBIT AUTO TRADING BOT - QUICK START")
    print("="*60)
    print("This script will help you set up auto trading quickly.")
    print("="*60)

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'loguru', 'requests', 'aiohttp', 'aiohttp_cors',
        'websockets', 'numpy', 'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def check_config_file():
    """Check if config file exists and has API keys."""
    print("\n📋 Checking configuration...")
    
    if not os.path.exists('config.yaml'):
        print("❌ config.yaml not found")
        return False
    
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        api_key = config.get('api', {}).get('api_key', '')
        api_secret = config.get('api', {}).get('api_secret', '')
        
        if not api_key or not api_secret:
            print("❌ API keys not configured")
            return False
        
        print("✅ Configuration file found with API keys")
        return True
        
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

async def test_api_connection():
    """Test API connection."""
    print("\n🔗 Testing API connection...")
    
    try:
        from src.config import Config
        from src.bybit_client import ByBitClient
        
        config = Config()
        client = ByBitClient(
            api_key=config.get('api.api_key'),
            api_secret=config.get('api.api_secret'),
            testnet=config.get('api.testnet', False)
        )
        
        # Test account info
        account_info = await client.get_account_info()
        if account_info.get('retCode') == 0:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API connection failed: {account_info.get('retMsg')}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def setup_basic_config():
    """Set up basic configuration."""
    print("\n⚙️  Setting up basic configuration...")
    
    try:
        import yaml
        
        # Default configuration
        default_config = {
            'api': {
                'testnet': False,
                'api_key': 'YOUR_API_KEY',
                'api_secret': 'YOUR_API_SECRET'
            },
            'trading': {
                'mode': 'both',
                'auto_trade': {
                    'enabled': True,
                    'max_positions': 5,
                    'max_daily_trades': 50,
                    'max_daily_loss': 1000
                },
                'risk_management': {
                    'max_position_size': 0.1,
                    'max_leverage': 10,
                    'stop_loss_percentage': 5.0,
                    'take_profit_percentage': 10.0,
                    'trailing_stop': True,
                    'trailing_stop_distance': 2.0
                }
            },
            'spot': {
                'enabled': True,
                'symbols': ['BTCUSDT', 'ETHUSDT'],
                'base_order_size': 100,
                'grid_levels': 10,
                'grid_spacing': 2.0
            },
            'futures': {
                'enabled': True,
                'symbols': ['BTCUSDT', 'ETHUSDT'],
                'base_order_size': 50,
                'grid_levels': 15,
                'grid_spacing': 1.5,
                'leverage': 5,
                'margin_mode': 'ISOLATED'
            },
            'dashboard': {
                'enabled': True,
                'port': 8081,
                'host': 'localhost',
                'auto_refresh': 30
            }
        }
        
        # Save configuration
        with open('config.yaml', 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print("✅ Basic configuration created")
        print("📝 Please edit config.yaml with your API keys")
        
    except Exception as e:
        print(f"❌ Error creating config: {e}")

def show_quick_start_menu():
    """Show quick start menu."""
    print("\n" + "="*60)
    print("🎯 QUICK START OPTIONS")
    print("="*60)
    print("1. 🚀 Start Auto Trading (Both Spot & Futures)")
    print("2. 📈 Start Spot Trading Only")
    print("3. 📊 Start Futures Trading Only")
    print("4. 🌐 Start Web Dashboard Only")
    print("5. ⚙️  Configure Settings")
    print("6. 📋 View Current Status")
    print("7. ❌ Exit")
    print("="*60)
    
    choice = input("Select an option (1-7): ").strip()
    
    if choice == "1":
        return "both"
    elif choice == "2":
        return "spot"
    elif choice == "3":
        return "futures"
    elif choice == "4":
        return "dashboard"
    elif choice == "5":
        return "configure"
    elif choice == "6":
        return "status"
    elif choice == "7":
        return "exit"
    else:
        print("❌ Invalid option")
        return None

async def start_trading(mode: str):
    """Start trading with specified mode."""
    print(f"\n🚀 Starting {mode.upper()} trading...")
    
    try:
        # Import and start trading manager
        from src.config import Config
        from src.bybit_client import ByBitClient
        from src.trading_manager import AutoTradingManager
        
        config = Config()
        
        # Set trading mode
        config.set('trading.mode', mode)
        
        client = ByBitClient(
            api_key=config.get('api.api_key'),
            api_secret=config.get('api.api_secret'),
            testnet=config.get('api.testnet', False)
        )
        
        trading_manager = AutoTradingManager(config, client)
        
        print(f"✅ {mode.upper()} trading started!")
        print("📊 Monitor at: http://localhost:8081")
        print("🛑 Press Ctrl+C to stop")
        
        # Start trading
        await trading_manager.start_auto_trading()
        
    except Exception as e:
        logger.error(f"❌ Failed to start trading: {e}")
        print(f"❌ Error: {e}")

async def start_dashboard():
    """Start web dashboard only."""
    print("\n🌐 Starting web dashboard...")
    
    try:
        from advanced_dashboard import main
        await main()
        
    except Exception as e:
        logger.error(f"❌ Failed to start dashboard: {e}")
        print(f"❌ Error: {e}")

async def configure_settings():
    """Configure trading settings."""
    print("\n⚙️  Opening configuration interface...")
    
    try:
        from auto_trade_interface import AutoTradeInterface
        
        interface = AutoTradeInterface()
        await interface.initialize()
        await interface.configure_trading_settings()
        
    except Exception as e:
        logger.error(f"❌ Failed to open configuration: {e}")
        print(f"❌ Error: {e}")

async def view_status():
    """View current trading status."""
    print("\n📊 Checking current status...")
    
    try:
        from src.config import Config
        from src.bybit_client import ByBitClient
        
        config = Config()
        client = ByBitClient(
            api_key=config.get('api.api_key'),
            api_secret=config.get('api.api_secret'),
            testnet=config.get('api.testnet', False)
        )
        
        # Get account info
        account_info = await client.get_account_info()
        if account_info.get('retCode') == 0:
            result = account_info.get('result', {})
            list_data = result.get('list', [])
            
            if list_data:
                account_data = list_data[0]
                total_balance = float(account_data.get('totalWalletBalance', 0))
                available_balance = float(account_data.get('totalAvailableBalance', 0))
                
                print(f"💰 Total Balance: ${total_balance:.2f}")
                print(f"💳 Available Balance: ${available_balance:.2f}")
        
        # Get current price
        ticker = await client.get_ticker("BTCUSDT")
        if ticker.get('retCode') == 0:
            result = ticker.get('result', {})
            list_data = result.get('list', [])
            if list_data:
                current_price = float(list_data[0].get('lastPrice', 0))
                print(f"📈 BTC Price: ${current_price:.2f}")
        
        print("✅ Status check completed")
        
    except Exception as e:
        logger.error(f"❌ Failed to check status: {e}")
        print(f"❌ Error: {e}")

async def main():
    """Main quick start function."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check configuration
    if not check_config_file():
        print("\n📝 Setting up configuration file...")
        setup_basic_config()
        print("\n⚠️  Please edit config.yaml with your API keys and run again.")
        return
    
    # Test API connection
    if not await test_api_connection():
        print("\n❌ API connection failed. Please check your API keys.")
        return
    
    print("\n✅ All checks passed! Ready to start trading.")
    
    # Main loop
    while True:
        choice = show_quick_start_menu()
        
        if choice == "both":
            await start_trading("both")
        elif choice == "spot":
            await start_trading("spot")
        elif choice == "futures":
            await start_trading("futures")
        elif choice == "dashboard":
            await start_dashboard()
        elif choice == "configure":
            await configure_settings()
        elif choice == "status":
            await view_status()
        elif choice == "exit":
            print("\n👋 Thank you for using ByBit Auto Trading Bot!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted by user")
    except Exception as e:
        logger.error(f"❌ Program error: {e}")
        print(f"❌ Error: {e}") 