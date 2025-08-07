import asyncio
import time
import psutil
import redis
from typing import Dict, Any, Optional
from loguru import logger
import json


class SystemMonitor:
    """System monitoring and health check for the trading bot."""
    
    def __init__(self, config):
        self.config = config
        self.start_time = time.time()
        self.last_health_check = 0
        self.health_check_interval = config.get('monitoring.health_check_interval', 30)
        
        # Performance metrics
        self.metrics = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'disk_usage': 0.0,
            'network_io': {'bytes_sent': 0, 'bytes_recv': 0},
            'uptime': 0,
            'api_latency': 0.0,
            'websocket_status': False,
            'last_price_update': 0,
            'error_count': 0,
            'warning_count': 0
        }
        
        # Redis connection for state persistence
        self.redis_client = None
        self._init_redis()
        
        logger.info("System monitor initialized")
    
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=self.config.get('database.redis_host', 'localhost'),
                port=self.config.get('database.redis_port', 6379),
                db=self.config.get('database.redis_db', 0),
                password=self.config.get('database.redis_password', ''),
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.info(f"Redis not available (optional): {e}")
            self.redis_client = None
    
    async def update_system_metrics(self):
        """Update system performance metrics."""
        try:
            # CPU usage
            self.metrics['cpu_usage'] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics['memory_usage'] = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics['disk_usage'] = disk.percent
            
            # Network I/O
            network = psutil.net_io_counters()
            self.metrics['network_io'] = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            }
            
            # Uptime
            self.metrics['uptime'] = time.time() - self.start_time
            
            # Save metrics to Redis
            if self.redis_client:
                self.redis_client.set('bot:metrics', json.dumps(self.metrics))
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    async def health_check(self, bybit_client, strategy) -> bool:
        """Perform comprehensive health check."""
        current_time = time.time()
        
        if current_time - self.last_health_check < self.health_check_interval:
            return True
        
        self.last_health_check = current_time
        
        try:
            # Check API connection
            api_healthy = await bybit_client.health_check()
            if not api_healthy:
                logger.error("API health check failed")
                return False
            
            # Check WebSocket connection
            if not bybit_client.ws_connected:
                logger.warning("WebSocket disconnected, attempting reconnection")
                await bybit_client.connect_websocket()
            
            # Check strategy risk limits
            if not strategy.check_risk_limits():
                logger.error("Risk limits exceeded")
                return False
            
            # Check system resources
            if self.metrics['cpu_usage'] > 90:
                logger.warning(f"High CPU usage: {self.metrics['cpu_usage']}%")
            
            if self.metrics['memory_usage'] > 90:
                logger.warning(f"High memory usage: {self.metrics['memory_usage']}%")
            
            if self.metrics['disk_usage'] > 90:
                logger.warning(f"High disk usage: {self.metrics['disk_usage']}%")
            
            # Check price update frequency
            if strategy.last_price and current_time - strategy.last_update > 60:
                logger.warning("No price updates for more than 60 seconds")
            
            logger.info("Health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def save_state(self, strategy_state: Dict[str, Any]):
        """Save bot state to Redis."""
        if not self.redis_client:
            return
        
        try:
            state_data = {
                'timestamp': time.time(),
                'strategy_state': strategy_state,
                'system_metrics': self.metrics
            }
            
            self.redis_client.set('bot:state', json.dumps(state_data))
            logger.debug("State saved to Redis")
            
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def load_state(self) -> Optional[Dict[str, Any]]:
        """Load bot state from Redis."""
        if not self.redis_client:
            return None
        
        try:
            state_data = self.redis_client.get('bot:state')
            if state_data:
                return json.loads(state_data)
        except Exception as e:
            logger.error(f"Error loading state: {e}")
        
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return self.metrics.copy()
    
    def log_performance(self, strategy_status: Dict[str, Any]):
        """Log performance metrics."""
        performance_data = {
            'timestamp': time.time(),
            'system': self.metrics,
            'strategy': strategy_status
        }
        
        logger.info(f"Performance: CPU={self.metrics['cpu_usage']:.1f}%, "
                   f"Memory={self.metrics['memory_usage']:.1f}%, "
                   f"PnL={strategy_status.get('total_pnl', 0):.2f}, "
                   f"Trades={strategy_status.get('trade_count', 0)}")
        
        # Save to Redis for historical tracking
        if self.redis_client:
            try:
                self.redis_client.lpush('bot:performance_history', json.dumps(performance_data))
                self.redis_client.ltrim('bot:performance_history', 0, 999)  # Keep last 1000 entries
            except Exception as e:
                logger.error(f"Error saving performance data: {e}")


class AlertManager:
    """Alert management for critical events."""
    
    def __init__(self, config):
        self.config = config
        self.alert_on_errors = config.get('monitoring.alert_on_errors', True)
        self.error_threshold = 5  # Number of errors before alert
        self.error_count = 0
        self.last_alert_time = 0
        self.alert_cooldown = 300  # 5 minutes between alerts
        
        logger.info("Alert manager initialized")
    
    def log_error(self, error_message: str):
        """Log error and potentially send alert."""
        self.error_count += 1
        logger.error(error_message)
        
        if self.alert_on_errors and self.error_count >= self.error_threshold:
            current_time = time.time()
            if current_time - self.last_alert_time > self.alert_cooldown:
                self._send_alert(f"Trading bot error threshold reached: {error_message}")
                self.last_alert_time = current_time
                self.error_count = 0
    
    def log_warning(self, warning_message: str):
        """Log warning."""
        logger.warning(warning_message)
    
    def _send_alert(self, message: str):
        """Send alert (placeholder for email/SMS/webhook integration)."""
        logger.critical(f"ALERT: {message}")
        # TODO: Implement actual alert mechanism (email, SMS, webhook, etc.)
    
    def reset_error_count(self):
        """Reset error count after successful recovery."""
        self.error_count = 0 