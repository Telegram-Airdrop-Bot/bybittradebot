#!/usr/bin/env python3
"""
ByBit Grid Trading Bot - Test Script
Test the bot functionality before live trading.
"""

import asyncio
import sys
import os
from loguru import logger

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.bybit_client import ByBitClient
from src.grid_strategy import GridStrategy
from src.monitor import SystemMonitor


async def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    try:
        config = Config()
        print("✓ Configuration loaded successfully")
        print(f"  - Symbol: {config.get('trading.symbol')}")
        print(f"  - Leverage: {config.get('trading.leverage')}")
        print(f"  - Grid levels: {len(config.get_grid_levels())}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


async def test_api_connection():
    """Test ByBit API connection."""
    print("\nTesting API connection...")
    try:
        config = Config()
        api_key = config.get('api.api_key')
        api_secret = config.get('api.api_secret')
        testnet = config.get('api.testnet', True)  # Use testnet for testing
        
        if not api_key or not api_secret:
            print("✗ API credentials not configured")
            return False
        
        client = ByBitClient(api_key, api_secret, testnet)
        
        # Test basic API call
        ticker = await client.get_ticker("BTCUSDT")
        if ticker.get('retCode') == 0:
            print("✓ API connection successful")
            result = ticker.get('result', {})
            list_data = result.get('list', [])
            if list_data:
                price = list_data[0].get('lastPrice', 'N/A')
                print(f"  - Current BTC price: {price}")
            return True
        else:
            print(f"✗ API error: {ticker.get('retMsg', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ API connection error: {e}")
        return False


async def test_websocket():
    """Test WebSocket connection."""
    print("\nTesting WebSocket connection...")
    try:
        config = Config()
        api_key = config.get('api.api_key')
        api_secret = config.get('api.api_secret')
        testnet = config.get('api.testnet', True)
        
        client = ByBitClient(api_key, api_secret, testnet)
        
        connected = await client.connect_websocket()
        if connected:
            print("✓ WebSocket connection successful")
            await client.disconnect_websocket()
            return True
        else:
            print("✗ WebSocket connection failed")
            return False
            
    except Exception as e:
        print(f"✗ WebSocket error: {e}")
        return False


async def test_strategy():
    """Test grid strategy initialization."""
    print("\nTesting grid strategy...")
    try:
        config = Config()
        api_key = config.get('api.api_key')
        api_secret = config.get('api.api_secret')
        testnet = config.get('api.testnet', True)
        
        client = ByBitClient(api_key, api_secret, testnet)
        strategy = GridStrategy(config, client)
        
        # Test strategy initialization
        initialized = await strategy.initialize()
        if initialized:
            print("✓ Strategy initialized successfully")
            print(f"  - Grid levels: {len(strategy.grid_levels)}")
            print(f"  - Base position size: {strategy.base_position_size}")
            print(f"  - Leverage: {strategy.leverage}")
            return True
        else:
            print("✗ Strategy initialization failed")
            return False
            
    except Exception as e:
        print(f"✗ Strategy error: {e}")
        return False


async def test_monitoring():
    """Test monitoring system."""
    print("\nTesting monitoring system...")
    try:
        config = Config()
        monitor = SystemMonitor(config)
        
        # Test system metrics
        await monitor.update_system_metrics()
        metrics = monitor.get_metrics()
        
        print("✓ Monitoring system initialized")
        print(f"  - CPU usage: {metrics['cpu_usage']:.1f}%")
        print(f"  - Memory usage: {metrics['memory_usage']:.1f}%")
        print(f"  - Uptime: {metrics['uptime']:.1f}s")
        
        return True
        
    except Exception as e:
        print(f"✗ Monitoring error: {e}")
        return False


async def test_price_simulation():
    """Test price update simulation."""
    print("\nTesting price update simulation...")
    try:
        config = Config()
        api_key = config.get('api.api_key')
        api_secret = config.get('api.api_secret')
        testnet = config.get('api.testnet', True)
        
        client = ByBitClient(api_key, api_secret, testnet)
        strategy = GridStrategy(config, client)
        
        # Get current price
        ticker = await client.get_ticker("BTCUSDT")
        if ticker.get('retCode') == 0:
            result = ticker.get('result', {})
            list_data = result.get('list', [])
            if list_data:
                current_price = float(list_data[0].get('lastPrice', 0))
                print(f"  - Current price: {current_price}")
                
                # Simulate price update
                await strategy.update_price(current_price)
                print("✓ Price update simulation successful")
                
                status = strategy.get_status()
                print(f"  - Active positions: {status['active_positions']}")
                print(f"  - Total PnL: {status['total_pnl']:.2f}")
                
                return True
        
        print("✗ Price simulation failed")
        return False
        
    except Exception as e:
        print(f"✗ Price simulation error: {e}")
        return False


async def run_all_tests():
    """Run all tests."""
    print("=== ByBit Grid Trading Bot - Test Suite ===\n")
    
    tests = [
        ("Configuration", test_config),
        ("API Connection", test_api_connection),
        ("WebSocket", test_websocket),
        ("Strategy", test_strategy),
        ("Monitoring", test_monitoring),
        ("Price Simulation", test_price_simulation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Bot is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix issues before live trading.")
        return False


async def main():
    """Main test function."""
    # Configure logging for tests
    logger.remove()
    logger.add(sys.stdout, level="WARNING")
    
    success = await run_all_tests()
    
    if success:
        print("\nNext steps:")
        print("1. Review configuration in config.yaml")
        print("2. Test with testnet first")
        print("3. Start with small position sizes")
        print("4. Monitor performance closely")
    else:
        print("\nPlease fix the failed tests before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 