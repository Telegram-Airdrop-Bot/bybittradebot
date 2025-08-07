#!/usr/bin/env python3
"""
ByBit Grid Trading Bot - Main Application
High-performance grid trading bot for ByBit futures market.
"""

import asyncio
import signal
import sys
import time
from typing import Optional
from loguru import logger
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config
from src.bybit_client import ByBitClient
from src.grid_strategy import GridStrategy
from src.monitor import SystemMonitor, AlertManager


class TradingBot:
    """Main trading bot application."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = Config(config_path)
        self.running = False
        self.shutdown_requested = False
        
        # Initialize components
        self.bybit_client = None
        self.strategy = None
        self.monitor = None
        self.alert_manager = None
        
        # Performance tracking
        self.start_time = time.time()
        self.last_price_update = 0
        self.price_update_interval = self.config.get('performance.price_update_interval', 0.1)
        
        logger.info("Trading bot initialized")
    
    async def initialize(self):
        """Initialize all bot components."""
        try:
            # Initialize ByBit client
            api_key = self.config.get('api.api_key', '')
            api_secret = self.config.get('api.api_secret', '')
            testnet = self.config.get('api.testnet', False)
            
            if not api_key or not api_secret:
                logger.error("API credentials not configured. Please set api_key and api_secret in config.yaml")
                return False
            
            self.bybit_client = ByBitClient(api_key, api_secret, testnet)
            
            # Initialize strategy
            self.strategy = GridStrategy(self.config, self.bybit_client)
            
            # Initialize monitoring
            self.monitor = SystemMonitor(self.config)
            self.alert_manager = AlertManager(self.config)
            
            # Initialize strategy
            if not await self.strategy.initialize():
                logger.error("Failed to initialize strategy")
                return False
            
            # Connect WebSocket
            if not await self.bybit_client.connect_websocket():
                logger.warning("WebSocket connection failed, will use REST API")
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            return False
    
    async def run(self):
        """Main bot loop."""
        if not await self.initialize():
            logger.error("Bot initialization failed")
            return
        
        self.running = True
        logger.info("Starting trading bot...")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            while self.running and not self.shutdown_requested:
                await self._main_loop()
                
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            self.alert_manager.log_error(f"Main loop error: {e}")
        
        finally:
            await self._cleanup()
    
    async def _main_loop(self):
        """Main trading loop."""
        try:
            current_time = time.time()
            
            # Update system metrics
            await self.monitor.update_system_metrics()
            
            # Get current price
            if current_time - self.last_price_update >= self.price_update_interval:
                price = await self.bybit_client.get_real_time_price(self.config.get('trading.symbol'))
                
                if price:
                    await self.strategy.update_price(price)
                    self.last_price_update = current_time
                else:
                    # Fallback to REST API
                    ticker = await self.bybit_client.get_ticker(self.config.get('trading.symbol'))
                    if ticker.get('retCode') == 0:
                        result = ticker.get('result', [])
                        if result:
                            price = float(result[0].get('last_price', 0))
                            await self.strategy.update_price(price)
                            self.last_price_update = current_time
            
            # Health check
            if not await self.monitor.health_check(self.bybit_client, self.strategy):
                logger.warning("Health check failed")
                self.alert_manager.log_warning("Health check failed")
            
            # Save state
            strategy_status = self.strategy.get_status()
            self.monitor.save_state(strategy_status)
            
            # Log performance
            self.monitor.log_performance(strategy_status)
            
            # Sleep for a short interval
            await asyncio.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.alert_manager.log_error(f"Main loop error: {e}")
            await asyncio.sleep(1)  # Wait before retrying
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_requested = True
    
    async def _cleanup(self):
        """Cleanup resources before shutdown."""
        logger.info("Cleaning up resources...")
        
        try:
            # Close WebSocket connection
            if self.bybit_client:
                await self.bybit_client.disconnect_websocket()
            
            # Cancel all orders
            if self.bybit_client:
                await self.bybit_client.cancel_all_orders(self.config.get('trading.symbol'))
            
            # Save final state
            if self.strategy:
                strategy_status = self.strategy.get_status()
                self.monitor.save_state(strategy_status)
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_status(self) -> dict:
        """Get current bot status."""
        if not self.strategy:
            return {'status': 'not_initialized'}
        
        status = self.strategy.get_status()
        status.update({
            'uptime': time.time() - self.start_time,
            'running': self.running,
            'system_metrics': self.monitor.get_metrics() if self.monitor else {}
        })
        
        return status


async def main():
    """Main entry point."""
    # Configure logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    logger.add(
        "bot.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    # Create and run bot
    bot = TradingBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 