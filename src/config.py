import yaml
import os
from typing import Dict, Any, List
from loguru import logger


class Config:
    """Configuration management for the grid trading bot."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _validate_config(self):
        """Validate configuration parameters."""
        required_sections = ['api', 'trading']
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate API configuration
        if not self.config['api']['api_key'] or not self.config['api']['api_secret']:
            logger.warning("API credentials not set. Please configure in config.yaml")
        
        # Validate trading configuration
        trading_mode = self.config.get('trading', {}).get('mode', 'both')
        if trading_mode not in ['spot', 'futures', 'both']:
            logger.warning(f"Invalid trading mode: {trading_mode}. Using 'both'")
            self.config['trading']['mode'] = 'both'
        
        logger.info("Configuration validation completed")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports nested keys with dot notation)."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_grid_levels(self) -> List[float]:
        """Get grid levels based on configuration."""
        trading_mode = self.config.get('trading', {}).get('mode', 'both')
        
        if trading_mode in ['spot', 'both']:
            spot_config = self.config.get('spot', {})
            symbols = spot_config.get('symbols', ['BTCUSDT'])
            grid_levels = spot_config.get('grid_levels', 10)
            
            # For now, return a simple list of levels
            # In a real implementation, you'd calculate based on current price
            return [i * 1000 for i in range(1, grid_levels + 1)]
        elif trading_mode == 'futures':
            futures_config = self.config.get('futures', {})
            symbols = futures_config.get('symbols', ['BTCUSDT'])
            grid_levels = futures_config.get('grid_levels', 15)
            
            # For now, return a simple list of levels
            return [i * 1000 for i in range(1, grid_levels + 1)]
        else:
            # Default fallback
            return [i * 1000 for i in range(1, 11)]
    
    def update(self, key: str, value: Any):
        """Update configuration value."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.info(f"Configuration updated: {key} = {value}")
    
    def set(self, key: str, value: Any):
        """Set configuration value (alias for update)."""
        self.update(key, value)
    
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False)
            logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise 