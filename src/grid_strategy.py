import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from loguru import logger
import numpy as np


class PositionSide(Enum):
    LONG = "Buy"
    SHORT = "Sell"


class OrderType(Enum):
    MARKET = "Market"
    LIMIT = "Limit"


@dataclass
class Position:
    """Position data structure."""
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    order_id: str
    timestamp: float
    
    def update_price(self, new_price: float):
        """Update position with new price."""
        self.current_price = new_price
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = (new_price - self.entry_price) * self.size
        else:
            self.unrealized_pnl = (self.entry_price - new_price) * self.size


@dataclass
class GridLevel:
    """Grid level data structure."""
    price: float
    position: Optional[Position]
    order_id: Optional[str]
    last_crossed: float
    is_active: bool


class GridStrategy:
    """High-performance grid trading strategy with fast reversal logic."""
    
    def __init__(self, config, bybit_client):
        self.config = config
        self.client = bybit_client
        self.symbol = config.get('trading.symbol', 'BTCUSDT')
        self.leverage = config.get('trading.leverage', 10)
        self.base_position_size = config.get('trading.position_size', 0.01)
        self.max_positions = config.get('trading.max_positions', 5)
        
        # Grid configuration
        self.grid_levels = config.get_grid_levels()
        self.grid_levels.sort()
        self.grid_data = {level: GridLevel(level, None, None, 0, True) for level in self.grid_levels}
        
        # Position tracking
        self.positions: Dict[str, Position] = {}
        self.active_orders: Dict[str, Dict] = {}
        self.position_history: List[Position] = []
        
        # Performance tracking
        self.total_pnl = 0.0
        self.daily_pnl = 0.0
        self.trade_count = 0
        self.last_price = None
        self.last_update = 0
        
        # Cover loss tracking
        self.consecutive_losses = 0
        self.current_multiplier = 1.0
        self.max_multiplier = config.get('cover_loss.max_multiplier', 3.0)
        
        # Risk management
        self.max_daily_loss = config.get('risk.max_daily_loss', 100)
        self.max_position_loss = config.get('risk.max_position_loss', 50)
        self.emergency_stop = config.get('risk.emergency_stop', True)
        
        logger.info(f"Grid strategy initialized with {len(self.grid_levels)} levels")
    
    async def initialize(self):
        """Initialize the strategy."""
        try:
            # Set leverage
            await self.client.set_leverage(self.symbol, self.leverage)
            
            # Cancel existing orders
            await self.client.cancel_all_orders(self.symbol)
            
            # Get current positions
            await self._load_positions()
            
            logger.info("Grid strategy initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize grid strategy: {e}")
            return False
    
    async def _load_positions(self):
        """Load existing positions from ByBit."""
        try:
            positions_response = await self.client.get_positions(self.symbol)
            if positions_response.get('retCode') == 0:
                positions_data = positions_response.get('result', [])
                
                for pos_data in positions_data:
                    if float(pos_data.get('size', 0)) > 0:
                        position = Position(
                            symbol=self.symbol,
                            side=PositionSide.LONG if pos_data.get('side') == 'Buy' else PositionSide.SHORT,
                            size=float(pos_data.get('size', 0)),
                            entry_price=float(pos_data.get('entry_price', 0)),
                            current_price=float(pos_data.get('mark_price', 0)),
                            unrealized_pnl=float(pos_data.get('unrealised_pnl', 0)),
                            realized_pnl=float(pos_data.get('realised_pnl', 0)),
                            stop_loss=float(pos_data.get('stop_loss', 0)) if pos_data.get('stop_loss') else None,
                            take_profit=float(pos_data.get('take_profit', 0)) if pos_data.get('take_profit') else None,
                            order_id=pos_data.get('order_id', ''),
                            timestamp=time.time()
                        )
                        self.positions[position.order_id] = position
                        
                        # Update grid level
                        for level in self.grid_levels:
                            if abs(position.entry_price - level) < 1:  # Within $1 of grid level
                                self.grid_data[level].position = position
                                break
                
                logger.info(f"Loaded {len(self.positions)} existing positions")
                
        except Exception as e:
            logger.error(f"Failed to load positions: {e}")
    
    async def update_price(self, price: float):
        """Update current price and check for grid crossings."""
        self.last_price = price
        self.last_update = time.time()
        
        # Update all position prices
        for position in self.positions.values():
            position.update_price(price)
        
        # Check for grid crossings
        await self._check_grid_crossings(price)
        
        # Check for stop losses and take profits
        await self._check_exit_conditions(price)
    
    async def _check_grid_crossings(self, price: float):
        """Check for grid level crossings and execute trades."""
        for i, level in enumerate(self.grid_levels):
            if not self.grid_data[level].is_active:
                continue
            
            grid_level = self.grid_data[level]
            current_position = grid_level.position
            
            # Check if price crossed the grid level
            if self._price_crossed_level(price, level, grid_level.last_crossed):
                logger.info(f"Price {price} crossed grid level {level}")
                
                # Determine trade direction
                if price > level:  # Price crossed above level
                    if current_position and current_position.side == PositionSide.SHORT:
                        # Close short position and open long
                        await self._reverse_position(current_position, PositionSide.LONG, price)
                    elif not current_position:
                        # Open new long position
                        await self._open_position(PositionSide.LONG, level, price)
                
                elif price < level:  # Price crossed below level
                    if current_position and current_position.side == PositionSide.LONG:
                        # Close long position and open short
                        await self._reverse_position(current_position, PositionSide.SHORT, price)
                    elif not current_position:
                        # Open new short position
                        await self._open_position(PositionSide.SHORT, level, price)
                
                grid_level.last_crossed = time.time()
    
    def _price_crossed_level(self, current_price: float, level: float, last_crossed: float) -> bool:
        """Check if price has crossed a grid level."""
        # Prevent multiple triggers within short time
        if time.time() - last_crossed < 1:  # 1 second cooldown
            return False
        
        # Check if price crossed the level
        if abs(current_price - level) < 0.1:  # Within $0.10 of level
            return True
        
        return False
    
    async def _open_position(self, side: PositionSide, grid_level: float, current_price: float):
        """Open a new position."""
        try:
            # Calculate position size with cover loss multiplier
            position_size = self.base_position_size * self.current_multiplier
            
            # Calculate stop loss and take profit
            stop_loss, take_profit = self._calculate_exit_prices(side, current_price, grid_level)
            
            # Place market order
            order_response = await self.client.place_order(
                symbol=self.symbol,
                side=side.value,
                order_type=OrderType.MARKET.value,
                qty=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if order_response.get('retCode') == 0:
                order_data = order_response.get('result', {})
                order_id = order_data.get('order_id', '')
                
                # Create position object
                position = Position(
                    symbol=self.symbol,
                    side=side,
                    size=position_size,
                    entry_price=current_price,
                    current_price=current_price,
                    unrealized_pnl=0.0,
                    realized_pnl=0.0,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    order_id=order_id,
                    timestamp=time.time()
                )
                
                self.positions[order_id] = position
                self.grid_data[grid_level].position = position
                self.active_orders[order_id] = order_data
                
                logger.info(f"Opened {side.value} position at {current_price}, size: {position_size}")
                
            else:
                logger.error(f"Failed to open position: {order_response}")
                
        except Exception as e:
            logger.error(f"Error opening position: {e}")
    
    async def _reverse_position(self, position: Position, new_side: PositionSide, current_price: float):
        """Reverse position with fast execution."""
        try:
            # Calculate loss
            loss = position.unrealized_pnl
            
            # Close existing position
            close_response = await self.client.place_order(
                symbol=self.symbol,
                side="Sell" if position.side == PositionSide.LONG else "Buy",
                order_type=OrderType.MARKET.value,
                qty=position.size
            )
            
            if close_response.get('retCode') == 0:
                # Update cover loss multiplier
                if loss < 0:
                    self.consecutive_losses += 1
                    self.current_multiplier = min(
                        self.current_multiplier * self.config.get('cover_loss.multiplier', 1.5),
                        self.max_multiplier
                    )
                else:
                    self.consecutive_losses = 0
                    self.current_multiplier = max(self.current_multiplier * 0.9, 1.0)
                
                # Remove old position
                if position.order_id in self.positions:
                    del self.positions[position.order_id]
                
                # Open reverse position immediately
                await self._open_position(new_side, position.entry_price, current_price)
                
                logger.info(f"Reversed position: {position.side.value} -> {new_side.value}, Loss: {loss}")
                
            else:
                logger.error(f"Failed to close position: {close_response}")
                
        except Exception as e:
            logger.error(f"Error reversing position: {e}")
    
    def _calculate_exit_prices(self, side: PositionSide, entry_price: float, grid_level: float) -> Tuple[float, float]:
        """Calculate stop loss and take profit prices."""
        grid_step = abs(self.grid_levels[1] - self.grid_levels[0]) if len(self.grid_levels) > 1 else 1000
        
        stop_loss_pct = self.config.get('stop_loss.percentage', 0.05)
        take_profit_pct = self.config.get('take_profit.percentage', 0.95)
        
        if side == PositionSide.LONG:
            stop_loss = entry_price * (1 - stop_loss_pct)
            take_profit = entry_price + (grid_step * take_profit_pct)
        else:
            stop_loss = entry_price * (1 + stop_loss_pct)
            take_profit = entry_price - (grid_step * take_profit_pct)
        
        return stop_loss, take_profit
    
    async def _check_exit_conditions(self, price: float):
        """Check for stop loss and take profit conditions."""
        positions_to_close = []
        
        for position in self.positions.values():
            # Check stop loss
            if position.stop_loss:
                if (position.side == PositionSide.LONG and price <= position.stop_loss) or \
                   (position.side == PositionSide.SHORT and price >= position.stop_loss):
                    positions_to_close.append((position, "Stop Loss"))
            
            # Check take profit
            if position.take_profit:
                if (position.side == PositionSide.LONG and price >= position.take_profit) or \
                   (position.side == PositionSide.SHORT and price <= position.take_profit):
                    positions_to_close.append((position, "Take Profit"))
        
        # Close positions
        for position, reason in positions_to_close:
            await self._close_position(position, reason)
    
    async def _close_position(self, position: Position, reason: str):
        """Close position."""
        try:
            close_response = await self.client.place_order(
                symbol=self.symbol,
                side="Sell" if position.side == PositionSide.LONG else "Buy",
                order_type=OrderType.MARKET.value,
                qty=position.size
            )
            
            if close_response.get('retCode') == 0:
                # Update PnL
                self.total_pnl += position.realized_pnl
                self.daily_pnl += position.realized_pnl
                self.trade_count += 1
                
                # Remove from tracking
                if position.order_id in self.positions:
                    del self.positions[position.order_id]
                
                # Clear grid level
                for grid_level in self.grid_data.values():
                    if grid_level.position and grid_level.position.order_id == position.order_id:
                        grid_level.position = None
                        break
                
                logger.info(f"Closed position: {reason}, PnL: {position.realized_pnl}")
                
            else:
                logger.error(f"Failed to close position: {close_response}")
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
    
    def get_status(self) -> Dict:
        """Get current strategy status."""
        return {
            'total_pnl': self.total_pnl,
            'daily_pnl': self.daily_pnl,
            'trade_count': self.trade_count,
            'active_positions': len(self.positions),
            'current_price': self.last_price,
            'cover_loss_multiplier': self.current_multiplier,
            'consecutive_losses': self.consecutive_losses,
            'grid_levels': len(self.grid_levels),
            'last_update': self.last_update
        }
    
    def check_risk_limits(self) -> bool:
        """Check if risk limits are exceeded."""
        if self.daily_pnl < -self.max_daily_loss:
            logger.warning(f"Daily loss limit exceeded: {self.daily_pnl}")
            return False
        
        for position in self.positions.values():
            if position.unrealized_pnl < -self.max_position_loss:
                logger.warning(f"Position loss limit exceeded: {position.unrealized_pnl}")
                return False
        
        return True 