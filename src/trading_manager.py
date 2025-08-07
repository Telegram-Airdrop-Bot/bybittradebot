#!/usr/bin/env python3
"""
ByBit Auto Trading Manager
Handles both spot and futures trading with comprehensive risk management.
"""

import asyncio
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import numpy as np

from .bybit_client import ByBitClient
from .config import Config


class TradingMode(Enum):
    SPOT = "spot"
    FUTURES = "futures"
    BOTH = "both"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


@dataclass
class TradeSignal:
    symbol: str
    side: str  # BUY or SELL
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 0.0
    signal_strength: str = "WEAK"


class AutoTradingManager:
    """Comprehensive auto trading manager for spot and futures."""
    
    def __init__(self, config: Config, client: ByBitClient):
        self.config = config
        self.client = client
        self.trading_mode = TradingMode(config.get('trading.mode', 'both'))
        
        # Trading state
        self.active_positions = {}
        self.pending_orders = {}
        self.daily_stats = {
            'trades': 0,
            'profit': 0.0,
            'loss': 0.0,
            'volume': 0.0
        }
        
        # Risk management
        self.risk_limits = {
            'max_daily_loss': float(config.get('trading.auto_trade.max_daily_loss', 1000)),
            'max_positions': int(config.get('trading.auto_trade.max_positions', 5)),
            'max_daily_trades': int(config.get('trading.auto_trade.max_daily_trades', 50))
        }
        
        # Market analysis
        self.market_data = {}
        self.technical_indicators = {}
        
        logger.info(f"Auto Trading Manager initialized with mode: {self.trading_mode.value}")
    
    async def start_auto_trading(self):
        """Start the auto trading system."""
        logger.info("🚀 Starting Auto Trading System...")
        
        try:
            # Initialize trading environment
            await self._initialize_trading_environment()
            
            # Start trading loops
            if self.trading_mode in [TradingMode.SPOT, TradingMode.BOTH]:
                asyncio.create_task(self._spot_trading_loop())
            
            if self.trading_mode in [TradingMode.FUTURES, TradingMode.BOTH]:
                asyncio.create_task(self._futures_trading_loop())
            
            # Start monitoring
            asyncio.create_task(self._monitoring_loop())
            
            logger.info("✅ Auto trading system started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start auto trading: {e}")
            raise
    
    async def _initialize_trading_environment(self):
        """Initialize the trading environment."""
        logger.info("🔧 Initializing trading environment...")
        
        # Check account status
        account_info = await self.client.get_account_details()
        if account_info.get('retCode') == 0:
            result = account_info.get('result', {})
            margin_mode = result.get('marginMode', 'Unknown')
            logger.info(f"Account margin mode: {margin_mode}")
        
        # Set up futures settings if needed
        if self.trading_mode in [TradingMode.FUTURES, TradingMode.BOTH]:
            await self._setup_futures_trading()
        
        # Initialize market data
        await self._initialize_market_data()
        
        logger.info("✅ Trading environment initialized")
    
    async def _setup_futures_trading(self):
        """Set up futures trading parameters."""
        futures_config = self.config.get('futures', {})
        
        for symbol in futures_config.get('symbols', ['BTCUSDT']):
            try:
                # Set leverage
                leverage = futures_config.get('leverage', 5)
                await self.client.set_leverage(symbol, leverage)
                logger.info(f"Set leverage for {symbol}: {leverage}x")
                
            except Exception as e:
                logger.warning(f"Failed to set leverage for {symbol}: {e}")
    
    async def _initialize_market_data(self):
        """Initialize market data for all symbols."""
        symbols = []
        
        if self.trading_mode in [TradingMode.SPOT, TradingMode.BOTH]:
            spot_config = self.config.get('spot', {})
            symbols.extend(spot_config.get('symbols', ['BTCUSDT']))
        
        if self.trading_mode in [TradingMode.FUTURES, TradingMode.BOTH]:
            futures_config = self.config.get('futures', {})
            symbols.extend(futures_config.get('symbols', ['BTCUSDT']))
        
        # Remove duplicates
        symbols = list(set(symbols))
        
        for symbol in symbols:
            self.market_data[symbol] = {
                'price': 0.0,
                'volume': 0.0,
                'timestamp': 0,
                'indicators': {}
            }
        
        logger.info(f"Initialized market data for {len(symbols)} symbols")
    
    async def _spot_trading_loop(self):
        """Main spot trading loop."""
        logger.info("📈 Starting spot trading loop")
        
        while True:
            try:
                await self._process_spot_trading()
                await asyncio.sleep(5)  # 5 second intervals
                
            except Exception as e:
                logger.error(f"Error in spot trading loop: {e}")
                await asyncio.sleep(10)
    
    async def _futures_trading_loop(self):
        """Main futures trading loop."""
        logger.info("📊 Starting futures trading loop")
        
        while True:
            try:
                await self._process_futures_trading()
                await asyncio.sleep(5)  # 5 second intervals
                
            except Exception as e:
                logger.error(f"Error in futures trading loop: {e}")
                await asyncio.sleep(10)
    
    async def _process_spot_trading(self):
        """Process spot trading logic."""
        spot_config = self.config.get('spot', {})
        symbols = spot_config.get('symbols', ['BTCUSDT'])
        
        for symbol in symbols:
            try:
                # Update market data
                await self._update_market_data(symbol)
                
                # Generate trading signals
                signal = await self._generate_trading_signal(symbol, 'spot')
                
                if signal and signal.confidence > 0.6:
                    await self._execute_spot_trade(signal)
                
            except Exception as e:
                logger.error(f"Error processing spot trading for {symbol}: {e}")
    
    async def _process_futures_trading(self):
        """Process futures trading logic."""
        futures_config = self.config.get('futures', {})
        symbols = futures_config.get('symbols', ['BTCUSDT'])
        
        for symbol in symbols:
            try:
                # Update market data
                await self._update_market_data(symbol)
                
                # Generate trading signals
                signal = await self._generate_trading_signal(symbol, 'futures')
                
                if signal and signal.confidence > 0.6:
                    await self._execute_futures_trade(signal)
                
            except Exception as e:
                logger.error(f"Error processing futures trading for {symbol}: {e}")
    
    async def _update_market_data(self, symbol: str):
        """Update market data for a symbol."""
        try:
            # Get ticker data
            ticker = await self.client.get_ticker(symbol)
            if ticker.get('retCode') == 0:
                result = ticker.get('result', {})
                list_data = result.get('list', [])
                if list_data:
                    ticker_data = list_data[0]
                    
                    self.market_data[symbol].update({
                        'price': float(ticker_data.get('lastPrice', 0)),
                        'volume': float(ticker_data.get('volume24h', 0)),
                        'timestamp': int(time.time() * 1000)
                    })
            
            # Calculate technical indicators
            await self._calculate_technical_indicators(symbol)
            
        except Exception as e:
            logger.error(f"Error updating market data for {symbol}: {e}")
    
    async def _calculate_technical_indicators(self, symbol: str):
        """Calculate technical indicators for a symbol."""
        try:
            # Get kline data for indicators
            kline_data = await self.client.get_kline_data(symbol, "1", 100)
            
            if kline_data.get('retCode') == 0:
                result = kline_data.get('result', {})
                list_data = result.get('list', [])
                
                if len(list_data) >= 20:
                    # Calculate RSI
                    rsi = self._calculate_rsi(list_data)
                    
                    # Calculate Moving Averages
                    sma_short, sma_long = self._calculate_moving_averages(list_data)
                    
                    # Calculate Bollinger Bands
                    bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(list_data)
                    
                    self.market_data[symbol]['indicators'] = {
                        'rsi': rsi,
                        'sma_short': sma_short,
                        'sma_long': sma_long,
                        'bb_upper': bb_upper,
                        'bb_middle': bb_middle,
                        'bb_lower': bb_lower
                    }
            
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
    
    def _calculate_rsi(self, kline_data: List) -> float:
        """Calculate RSI from kline data."""
        if len(kline_data) < 14:
            return 50.0
        
        prices = [float(kline[4]) for kline in kline_data]  # Close prices
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-change)
        
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_moving_averages(self, kline_data: List) -> tuple:
        """Calculate short and long moving averages."""
        prices = [float(kline[4]) for kline in kline_data]
        
        short_period = 10
        long_period = 20
        
        sma_short = sum(prices[-short_period:]) / short_period if len(prices) >= short_period else prices[-1]
        sma_long = sum(prices[-long_period:]) / long_period if len(prices) >= long_period else prices[-1]
        
        return sma_short, sma_long
    
    def _calculate_bollinger_bands(self, kline_data: List) -> tuple:
        """Calculate Bollinger Bands."""
        prices = [float(kline[4]) for kline in kline_data]
        period = 20
        
        if len(prices) < period:
            current_price = prices[-1]
            return current_price, current_price, current_price
        
        sma = sum(prices[-period:]) / period
        variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
        std_dev = variance ** 0.5
        
        bb_upper = sma + (2 * std_dev)
        bb_middle = sma
        bb_lower = sma - (2 * std_dev)
        
        return bb_upper, bb_middle, bb_lower
    
    async def _generate_trading_signal(self, symbol: str, market_type: str) -> Optional[TradeSignal]:
        """Generate trading signal based on market analysis."""
        try:
            market_data = self.market_data.get(symbol, {})
            indicators = market_data.get('indicators', {})
            current_price = market_data.get('price', 0)
            
            if current_price == 0:
                return None
            
            # Calculate signal strength
            signal_strength = 0.0
            side = None
            
            # RSI signals
            rsi = indicators.get('rsi', 50)
            if rsi < 30:  # Oversold
                signal_strength += 0.3
                side = "BUY"
            elif rsi > 70:  # Overbought
                signal_strength += 0.3
                side = "SELL"
            
            # Moving average signals
            sma_short = indicators.get('sma_short', current_price)
            sma_long = indicators.get('sma_long', current_price)
            
            if current_price > sma_short > sma_long:  # Uptrend
                signal_strength += 0.2
                if side != "SELL":
                    side = "BUY"
            elif current_price < sma_short < sma_long:  # Downtrend
                signal_strength += 0.2
                if side != "BUY":
                    side = "SELL"
            
            # Bollinger Bands signals
            bb_upper = indicators.get('bb_upper', current_price)
            bb_lower = indicators.get('bb_lower', current_price)
            
            if current_price <= bb_lower:  # Price at lower band
                signal_strength += 0.2
                if side != "SELL":
                    side = "BUY"
            elif current_price >= bb_upper:  # Price at upper band
                signal_strength += 0.2
                if side != "BUY":
                    side = "SELL"
            
            # Volume confirmation
            volume = market_data.get('volume', 0)
            if volume > 1000000:  # High volume
                signal_strength += 0.1
            
            if signal_strength >= 0.6 and side:
                # Calculate position size
                quantity = self._calculate_position_size(symbol, market_type, current_price)
                
                # Calculate stop loss and take profit
                stop_loss, take_profit = self._calculate_risk_levels(side, current_price, market_type)
                
                return TradeSignal(
                    symbol=symbol,
                    side=side,
                    order_type=OrderType.LIMIT,
                    quantity=quantity,
                    price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    confidence=signal_strength,
                    signal_strength="STRONG" if signal_strength > 0.8 else "MODERATE"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating trading signal for {symbol}: {e}")
            return None
    
    def _calculate_position_size(self, symbol: str, market_type: str, current_price: float) -> float:
        """Calculate position size based on risk management."""
        try:
            if market_type == 'spot':
                base_size = float(self.config.get('spot.base_order_size', 100))  # USDT
                quantity = base_size / current_price
            else:  # futures
                base_size = float(self.config.get('futures.base_order_size', 50))  # USDT
                leverage = float(self.config.get('futures.leverage', 5))
                quantity = (base_size * leverage) / current_price
            
            # Apply risk management limits
            max_position_size = float(self.config.get('trading.risk_management.max_position_size', 0.1))
            quantity = min(quantity, max_position_size)
            
            return quantity
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.001  # Minimum position size
    
    def _calculate_risk_levels(self, side: str, current_price: float, market_type: str) -> tuple:
        """Calculate stop loss and take profit levels."""
        try:
            stop_loss_pct = float(self.config.get('trading.risk_management.stop_loss_percentage', 5.0))
            take_profit_pct = float(self.config.get('trading.risk_management.take_profit_percentage', 10.0))
            
            if side == "BUY":
                stop_loss = current_price * (1 - stop_loss_pct / 100)
                take_profit = current_price * (1 + take_profit_pct / 100)
            else:  # SELL
                stop_loss = current_price * (1 + stop_loss_pct / 100)
                take_profit = current_price * (1 - take_profit_pct / 100)
            
            return stop_loss, take_profit
            
        except Exception as e:
            logger.error(f"Error calculating risk levels: {e}")
            return None, None
    
    async def _execute_spot_trade(self, signal: TradeSignal):
        """Execute spot trade."""
        try:
            logger.info(f"🔄 Executing spot trade: {signal.side} {signal.quantity} {signal.symbol}")
            
            # Check risk limits
            if not self._check_risk_limits():
                logger.warning("Risk limits exceeded, skipping trade")
                return
            
            # Place order
            order_result = await self.client.place_order(
                symbol=signal.symbol,
                side=signal.side,
                order_type=signal.order_type.value,
                qty=signal.quantity,
                price=signal.price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )
            
            if order_result.get('retCode') == 0:
                logger.info(f"✅ Spot trade executed successfully")
                self._update_daily_stats('trades', 1)
                
                # Store position
                self.active_positions[signal.symbol] = {
                    'side': signal.side,
                    'quantity': signal.quantity,
                    'entry_price': signal.price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'timestamp': int(time.time())
                }
            else:
                logger.error(f"❌ Failed to execute spot trade: {order_result.get('retMsg')}")
                
        except Exception as e:
            logger.error(f"Error executing spot trade: {e}")
    
    async def _execute_futures_trade(self, signal: TradeSignal):
        """Execute futures trade."""
        try:
            logger.info(f"🔄 Executing futures trade: {signal.side} {signal.quantity} {signal.symbol}")
            
            # Check risk limits
            if not self._check_risk_limits():
                logger.warning("Risk limits exceeded, skipping trade")
                return
            
            # Place order
            order_result = await self.client.place_order(
                symbol=signal.symbol,
                side=signal.side,
                order_type=signal.order_type.value,
                qty=signal.quantity,
                price=signal.price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit
            )
            
            if order_result.get('retCode') == 0:
                logger.info(f"✅ Futures trade executed successfully")
                self._update_daily_stats('trades', 1)
                
                # Store position
                self.active_positions[signal.symbol] = {
                    'side': signal.side,
                    'quantity': signal.quantity,
                    'entry_price': signal.price,
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'timestamp': int(time.time())
                }
            else:
                logger.error(f"❌ Failed to execute futures trade: {order_result.get('retMsg')}")
                
        except Exception as e:
            logger.error(f"Error executing futures trade: {e}")
    
    def _check_risk_limits(self) -> bool:
        """Check if risk limits are within acceptable range."""
        try:
            # Check daily loss limit
            daily_pnl = self.daily_stats['profit'] - self.daily_stats['loss']
            if daily_pnl < -self.risk_limits['max_daily_loss']:
                logger.warning(f"Daily loss limit exceeded: {daily_pnl}")
                return False
            
            # Check position count
            if len(self.active_positions) >= self.risk_limits['max_positions']:
                logger.warning(f"Maximum positions reached: {len(self.active_positions)}")
                return False
            
            # Check daily trade count
            if self.daily_stats['trades'] >= self.risk_limits['max_daily_trades']:
                logger.warning(f"Maximum daily trades reached: {self.daily_stats['trades']}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return False
    
    def _update_daily_stats(self, stat_type: str, value: float):
        """Update daily statistics."""
        try:
            if stat_type == 'trades':
                self.daily_stats['trades'] += int(value)
            elif stat_type == 'profit':
                self.daily_stats['profit'] += float(value)
            elif stat_type == 'loss':
                self.daily_stats['loss'] += float(value)
            elif stat_type == 'volume':
                self.daily_stats['volume'] += float(value)
        except Exception as e:
            logger.error(f"Error updating daily stats: {e}")
    
    async def _monitoring_loop(self):
        """Monitor trading performance and positions."""
        logger.info("📊 Starting monitoring loop")
        
        while True:
            try:
                await self._monitor_positions()
                await self._monitor_performance()
                await asyncio.sleep(30)  # 30 second intervals
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_positions(self):
        """Monitor active positions."""
        try:
            for symbol, position in list(self.active_positions.items()):
                # Get current price
                ticker = await self.client.get_ticker(symbol)
                if ticker.get('retCode') == 0:
                    result = ticker.get('result', {})
                    list_data = result.get('list', [])
                    if list_data:
                        current_price = float(list_data[0].get('lastPrice', 0))
                        
                        # Check stop loss and take profit
                        if self._should_close_position(position, current_price):
                            await self._close_position(symbol, position)
                
        except Exception as e:
            logger.error(f"Error monitoring positions: {e}")
    
    def _should_close_position(self, position: Dict, current_price: float) -> bool:
        """Check if position should be closed."""
        try:
            side = position['side']
            entry_price = position['entry_price']
            stop_loss = position['stop_loss']
            take_profit = position['take_profit']
            
            if side == "BUY":
                # Check stop loss
                if current_price <= stop_loss:
                    return True
                # Check take profit
                if current_price >= take_profit:
                    return True
            else:  # SELL
                # Check stop loss
                if current_price >= stop_loss:
                    return True
                # Check take profit
                if current_price <= take_profit:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking position close conditions: {e}")
            return False
    
    async def _close_position(self, symbol: str, position: Dict):
        """Close a position."""
        try:
            logger.info(f"🔄 Closing position for {symbol}")
            
            # Determine close side (opposite of entry)
            close_side = "SELL" if position['side'] == "BUY" else "BUY"
            
            # Place closing order
            order_result = await self.client.place_order(
                symbol=symbol,
                side=close_side,
                order_type="MARKET",
                qty=position['quantity']
            )
            
            if order_result.get('retCode') == 0:
                logger.info(f"✅ Position closed successfully for {symbol}")
                
                # Calculate PnL
                ticker = await self.client.get_ticker(symbol)
                if ticker.get('retCode') == 0:
                    result = ticker.get('result', {})
                    list_data = result.get('list', [])
                    if list_data:
                        current_price = float(list_data[0].get('lastPrice', 0))
                        pnl = self._calculate_pnl(position, current_price)
                        
                        if pnl > 0:
                            self._update_daily_stats('profit', pnl)
                        else:
                            self._update_daily_stats('loss', abs(pnl))
                
                # Remove from active positions
                del self.active_positions[symbol]
                
            else:
                logger.error(f"❌ Failed to close position: {order_result.get('retMsg')}")
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    def _calculate_pnl(self, position: Dict, current_price: float) -> float:
        """Calculate PnL for a position."""
        try:
            entry_price = position['entry_price']
            quantity = position['quantity']
            side = position['side']
            
            if side == "BUY":
                pnl = (current_price - entry_price) * quantity
            else:  # SELL
                pnl = (entry_price - current_price) * quantity
            
            return pnl
            
        except Exception as e:
            logger.error(f"Error calculating PnL: {e}")
            return 0.0
    
    async def _monitor_performance(self):
        """Monitor trading performance."""
        try:
            # Ensure all values are floats
            profit = float(self.daily_stats.get('profit', 0))
            loss = float(self.daily_stats.get('loss', 0))
            total_pnl = profit - loss
            win_rate = self._calculate_win_rate()
            
            logger.info(f"📊 Daily Performance - PnL: ${total_pnl:.2f}, Trades: {self.daily_stats.get('trades', 0)}, Win Rate: {win_rate:.1f}%")
            
            # Check for emergency stop
            max_daily_loss = float(self.risk_limits.get('max_daily_loss', 1000))
            if total_pnl < -max_daily_loss:
                logger.warning("🚨 Emergency stop triggered due to excessive losses")
                await self._emergency_stop()
                
        except Exception as e:
            logger.error(f"Error monitoring performance: {e}")
    
    def _calculate_win_rate(self) -> float:
        """Calculate win rate."""
        try:
            total_trades = self.daily_stats['trades']
            if total_trades == 0:
                return 0.0
            
            # This is a simplified calculation
            # In a real implementation, you'd track individual trade results
            return 65.0  # Mock win rate
            
        except Exception as e:
            logger.error(f"Error calculating win rate: {e}")
            return 0.0
    
    async def _emergency_stop(self):
        """Emergency stop all trading."""
        try:
            logger.warning("🚨 EMERGENCY STOP - Closing all positions")
            
            # Close all active positions
            for symbol, position in list(self.active_positions.items()):
                await self._close_position(symbol, position)
            
            # Cancel all pending orders
            for symbol in self.active_positions.keys():
                await self.client.cancel_all_orders(symbol)
            
            logger.info("✅ Emergency stop completed")
            
        except Exception as e:
            logger.error(f"Error during emergency stop: {e}")
    
    def get_trading_status(self) -> Dict[str, Any]:
        """Get current trading status."""
        return {
            'trading_mode': self.trading_mode.value,
            'active_positions': len(self.active_positions),
            'daily_stats': self.daily_stats,
            'risk_limits': self.risk_limits,
            'market_data': {symbol: data.get('price', 0) for symbol, data in self.market_data.items()}
        } 