import asyncio
import time
import json
import hmac
import hashlib
import urllib.parse
from typing import Dict, Any, Optional, List
import requests
from loguru import logger
import aiohttp
import websockets


class ByBitClient:
    """High-performance ByBit API client with comprehensive error handling."""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # Set base URL
        self.base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
        
        # WebSocket connection
        self.ws = None
        self.ws_connected = False
        self.last_ping = 0
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        
        # Rate limiting
        self.request_times = []
        self.max_requests_per_second = 10
        
        # Connection state
        self.connected = False
        self.last_error = None
        
        logger.info(f"ByBit client initialized (testnet: {testnet})")
    
    async def connect_websocket(self):
        """Connect to ByBit WebSocket for real-time data."""
        try:
            ws_url = "wss://stream-testnet.bybit.com/v5/public/linear" if self.testnet else "wss://stream.bybit.com/v5/public/linear"
            
            self.ws = await websockets.connect(ws_url)
            self.ws_connected = True
            self.reconnect_attempts = 0
            
            # Subscribe to ticker updates
            subscribe_msg = {
                "op": "subscribe",
                "args": ["tickers.BTCUSDT"]
            }
            await self.ws.send(json.dumps(subscribe_msg))
            
            logger.info("WebSocket connected successfully")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self.ws_connected = False
            return False
    
    async def disconnect_websocket(self):
        """Disconnect WebSocket."""
        if self.ws and self.ws_connected:
            await self.ws.close()
            self.ws_connected = False
            logger.info("WebSocket disconnected")
    
    async def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        self.request_times = [t for t in self.request_times if current_time - t < 1]
        
        if len(self.request_times) >= self.max_requests_per_second:
            sleep_time = 1 - (current_time - self.request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        self.request_times.append(current_time)
    
    def _sign_request(self, params: Dict[str, Any]) -> str:
        """Sign API request."""
        # Sort parameters alphabetically as required by ByBit API
        sorted_params = dict(sorted(params.items()))
        query_string = urllib.parse.urlencode(sorted_params)
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def _make_request(self, method: str, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make authenticated API request with retry logic."""
        params = params or {}
        params['api_key'] = self.api_key
        params['timestamp'] = int(time.time() * 1000)
        params['recv_window'] = 5000
        params['sign'] = self._sign_request(params)
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(3):
            try:
                await self._rate_limit()
                
                if method == 'GET':
                    response = requests.get(url, params=params)
                elif method == 'POST':
                    response = requests.post(url, json=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"HTTP {response.status_code}: {response.text}")
                    return {"retCode": response.status_code, "retMsg": response.text}
                    
            except Exception as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(1)
        
        return {"retCode": -1, "retMsg": "All request attempts failed"}
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information."""
        try:
            return await self._make_request('GET', '/v5/account/wallet-balance', {"accountType": "UNIFIED"})
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_account_details(self) -> Dict[str, Any]:
        """Get detailed account information including margin mode, account status, etc."""
        try:
            return await self._make_request('GET', '/v5/account/info')
        except Exception as e:
            logger.error(f"Error getting account details: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_positions(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get current positions."""
        try:
            return await self._make_request('GET', '/v5/position/list', {"category": "linear", "symbol": symbol})
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_orderbook(self, symbol: str = "BTCUSDT", limit: int = 25) -> Dict[str, Any]:
        """Get order book."""
        try:
            return await self._make_request('GET', '/v5/market/orderbook', {"category": "linear", "symbol": symbol, "limit": limit})
        except Exception as e:
            logger.error(f"Error getting orderbook: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_ticker(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get current ticker information."""
        try:
            return await self._make_request('GET', '/v5/market/tickers', {"category": "linear", "symbol": symbol})
        except Exception as e:
            logger.error(f"Error getting ticker: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_kline_data(self, symbol: str = "BTCUSDT", interval: str = "1", limit: int = 200) -> Dict[str, Any]:
        """Get kline/candlestick data."""
        try:
            return await self._make_request('GET', '/v5/market/kline', {
                "category": "linear",
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            })
        except Exception as e:
            logger.error(f"Error getting kline data: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_funding_rate(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get funding rate information."""
        try:
            return await self._make_request('GET', '/v5/market/funding/history', {
                "category": "linear",
                "symbol": symbol,
                "limit": 1
            })
        except Exception as e:
            logger.error(f"Error getting funding rate: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_open_interest(self, symbol: str = "BTCUSDT", period: str = "1h") -> Dict[str, Any]:
        """Get open interest data."""
        try:
            return await self._make_request('GET', '/v5/market/open-interest', {
                "category": "linear",
                "symbol": symbol,
                "period": period
            })
        except Exception as e:
            logger.error(f"Error getting open interest: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_mark_price(self, symbol: str = "BTCUSDT") -> Dict[str, Any]:
        """Get mark price information."""
        try:
            return await self._make_request('GET', '/v5/market/mark-price-kline', {
                "category": "linear",
                "symbol": symbol,
                "interval": "1",
                "limit": 1
            })
        except Exception as e:
            logger.error(f"Error getting mark price: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def place_order(self, symbol: str, side: str, order_type: str, qty: float, 
                         price: float = None, stop_loss: float = None, take_profit: float = None) -> Dict[str, Any]:
        """Place order with comprehensive parameters."""
        try:
            payload = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(qty),
                "timeInForce": "GTC"
            }
            
            if price:
                payload["price"] = str(price)
            
            if stop_loss:
                payload["stopLoss"] = str(stop_loss)
            
            if take_profit:
                payload["takeProfit"] = str(take_profit)
            
            return await self._make_request('POST', '/v5/order/create', payload)
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel order."""
        try:
            return await self._make_request('POST', '/v5/order/cancel', {
                "category": "linear",
                "symbol": symbol,
                "orderId": order_id
            })
        except Exception as e:
            logger.error(f"Error canceling order: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """Cancel all orders for a symbol."""
        try:
            return await self._make_request('POST', '/v5/order/cancel-all', {
                "category": "linear",
                "symbol": symbol
            })
        except Exception as e:
            logger.error(f"Error canceling all orders: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_order_history(self, symbol: str, limit: int = 50) -> Dict[str, Any]:
        """Get order history."""
        try:
            return await self._make_request('GET', '/v5/order/realtime', {
                "category": "linear",
                "symbol": symbol,
                "limit": limit
            })
        except Exception as e:
            logger.error(f"Error getting order history: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """Set leverage for a symbol."""
        try:
            return await self._make_request('POST', '/v5/position/set-leverage', {
                "category": "linear",
                "symbol": symbol,
                "buyLeverage": str(leverage),
                "sellLeverage": str(leverage)
            })
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
            return {"retCode": -1, "retMsg": str(e)}
    
    async def get_real_time_price(self, symbol: str = "BTCUSDT") -> Optional[float]:
        """Get real-time price from WebSocket."""
        if not self.ws_connected:
            return None
        
        try:
            # This would be implemented with actual WebSocket message handling
            # For now, we'll use REST API as fallback
            ticker = await self.get_ticker(symbol)
            if ticker.get('retCode') == 0:
                result = ticker.get('result', {})
                list_data = result.get('list', [])
                if list_data:
                    return float(list_data[0].get('lastPrice', 0))
        except Exception as e:
            logger.error(f"Error getting real-time price: {e}")
        
        return None
    
    async def health_check(self) -> bool:
        """Perform health check on API connection."""
        try:
            await self.get_ticker("BTCUSDT")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def reconnect(self):
        """Reconnect to API with exponential backoff."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached")
            return False
        
        delay = min(2 ** self.reconnect_attempts, 60)
        logger.info(f"Attempting to reconnect in {delay} seconds...")
        await asyncio.sleep(delay)
        
        self.reconnect_attempts += 1
        return await self.health_check() 