#!/usr/bin/env python3
"""
ByBit Grid Trading Bot - Monitor Script
Simple monitoring interface for users to check bot status.
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from loguru import logger

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.bybit_client import ByBitClient
from src.grid_strategy import GridStrategy
from src.monitor import SystemMonitor


class BotMonitor:
    """Simple monitoring interface for the trading bot."""
    
    def __init__(self):
        self.config = Config()
        self.client = None
        self.strategy = None
        self.monitor = None
    
    async def initialize(self):
        """Initialize monitoring components."""
        try:
            api_key = self.config.get('api.api_key')
            api_secret = self.config.get('api.api_secret')
            testnet = self.config.get('api.testnet', False)
            
            self.client = ByBitClient(api_key, api_secret, testnet)
            self.strategy = GridStrategy(self.config, self.client)
            self.monitor = SystemMonitor(self.config)
            
            return True
        except Exception as e:
            print(f"Error initializing monitor: {e}")
            return False
    
    async def get_bot_status(self):
        """Get comprehensive bot status."""
        try:
            # Get current price
            ticker = await self.client.get_ticker("BTCUSDT")
            current_price = None
            if ticker.get('retCode') == 0:
                result = ticker.get('result', {})
                list_data = result.get('list', [])
                if list_data:
                    current_price = float(list_data[0].get('lastPrice', 0))
            
            # Get account info
            account_info = await self.client.get_account_info()
            
            # Get positions
            positions = await self.client.get_positions("BTCUSDT")
            
            # Get strategy status
            strategy_status = self.strategy.get_status()
            
            # Get system metrics
            await self.monitor.update_system_metrics()
            system_metrics = self.monitor.get_metrics()
            
            return {
                'current_price': current_price,
                'account_info': account_info,
                'positions': positions,
                'strategy_status': strategy_status,
                'system_metrics': system_metrics,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"Error getting bot status: {e}")
            return None
    
    def display_status(self, status):
        """Display bot status in a user-friendly format."""
        if not status:
            print("❌ Unable to get bot status")
            return
        
        print("\n" + "="*60)
        print("🤖 BYBIT GRID TRADING BOT - STATUS")
        print("="*60)
        print(f"📅 Last Updated: {status['timestamp']}")
        
        # Current Price
        if status['current_price']:
            print(f"💰 Current BTC Price: ${status['current_price']:,.2f}")
        else:
            print("💰 Current BTC Price: Unable to fetch")
        
        # Account Information
        account = status['account_info']
        if account.get('retCode') == 0:
            result = account.get('result', {})
            list_data = result.get('list', [])
            if list_data:
                wallet = list_data[0]
                print(f"💳 Account Balance: ${float(wallet.get('walletBalance', 0)):,.2f} USDT")
                print(f"📊 Available Balance: ${float(wallet.get('availableBalance', 0)):,.2f} USDT")
        else:
            print("💳 Account Balance: Unable to fetch")
        
        # Positions
        positions = status['positions']
        if positions.get('retCode') == 0:
            result = positions.get('result', {})
            list_data = result.get('list', [])
            active_positions = [p for p in list_data if float(p.get('size', 0)) > 0]
            print(f"📈 Active Positions: {len(active_positions)}")
            
            for pos in active_positions:
                side = "LONG" if pos.get('side') == 'Buy' else "SHORT"
                size = float(pos.get('size', 0))
                entry_price = float(pos.get('entryPrice', 0))
                pnl = float(pos.get('unrealisedPnl', 0))
                print(f"   {side}: {size} BTC @ ${entry_price:,.2f} | PnL: ${pnl:,.2f}")
        else:
            print("📈 Active Positions: Unable to fetch")
        
        # Strategy Status
        strategy = status['strategy_status']
        print(f"\n🎯 STRATEGY STATUS:")
        print(f"   Total PnL: ${strategy.get('total_pnl', 0):,.2f}")
        print(f"   Daily PnL: ${strategy.get('daily_pnl', 0):,.2f}")
        print(f"   Trade Count: {strategy.get('trade_count', 0)}")
        print(f"   Active Positions: {strategy.get('active_positions', 0)}")
        print(f"   Cover Loss Multiplier: {strategy.get('cover_loss_multiplier', 1.0):.2f}x")
        print(f"   Consecutive Losses: {strategy.get('consecutive_losses', 0)}")
        
        # System Metrics
        system = status['system_metrics']
        print(f"\n💻 SYSTEM METRICS:")
        print(f"   CPU Usage: {system.get('cpu_usage', 0):.1f}%")
        print(f"   Memory Usage: {system.get('memory_usage', 0):.1f}%")
        print(f"   Disk Usage: {system.get('disk_usage', 0):.1f}%")
        print(f"   Uptime: {system.get('uptime', 0):.0f} seconds")
        
        # Grid Levels
        grid_levels = self.config.get_grid_levels()
        current_price = status['current_price']
        if current_price and grid_levels:
            print(f"\n📊 GRID ANALYSIS:")
            print(f"   Grid Levels: {len(grid_levels)}")
            print(f"   Grid Range: ${min(grid_levels):,.0f} - ${max(grid_levels):,.0f}")
            
            # Find nearest grid level
            nearest_level = min(grid_levels, key=lambda x: abs(x - current_price))
            distance = abs(current_price - nearest_level)
            print(f"   Nearest Grid Level: ${nearest_level:,.0f}")
            print(f"   Distance to Grid: ${distance:,.0f}")
        
        print("\n" + "="*60)
    
    async def continuous_monitor(self, interval=30):
        """Continuously monitor the bot."""
        print("🔄 Starting continuous monitoring...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                status = await self.get_bot_status()
                self.display_status(status)
                
                print(f"\n⏰ Next update in {interval} seconds...")
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")


async def main():
    """Main monitoring function."""
    monitor = BotMonitor()
    
    if not await monitor.initialize():
        print("❌ Failed to initialize monitor")
        return
    
    print("🔍 ByBit Grid Trading Bot Monitor")
    print("Choose monitoring mode:")
    print("1. Single status check")
    print("2. Continuous monitoring (30s intervals)")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            status = await monitor.get_bot_status()
            monitor.display_status(status)
        elif choice == "2":
            await monitor.continuous_monitor()
        else:
            print("Invalid choice. Exiting.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    asyncio.run(main()) 