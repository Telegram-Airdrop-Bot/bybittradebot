#!/usr/bin/env python3
"""
ByBit Grid Trading Bot - Web Dashboard
Simple web interface for monitoring the bot.
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from aiohttp import web, ClientSession
import aiohttp_cors

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.bybit_client import ByBitClient
from src.grid_strategy import GridStrategy
from src.monitor import SystemMonitor


class WebDashboard:
    """Web dashboard for monitoring the trading bot."""
    
    def __init__(self):
        self.config = Config()
        self.client = None
        self.strategy = None
        self.monitor = None
        self.app = web.Application()
        self.setup_routes()
    
    async def initialize(self):
        """Initialize dashboard components."""
        try:
            api_key = self.config.get('api.api_key')
            api_secret = self.config.get('api.api_secret')
            testnet = self.config.get('api.testnet', False)
            
            self.client = ByBitClient(api_key, api_secret, testnet)
            self.strategy = GridStrategy(self.config, self.client)
            self.monitor = SystemMonitor(self.config)
            
            return True
        except Exception as e:
            print(f"Error initializing dashboard: {e}")
            return False
    
    def setup_routes(self):
        """Setup web routes."""
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/api/status', self.status_handler)
        
        # Setup CORS
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def index_handler(self, request):
        """Serve the main dashboard page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ByBit Grid Trading Bot - Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .status-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }
                .card {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 20px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                .card h3 {
                    margin-top: 0;
                    color: #fff;
                    border-bottom: 2px solid rgba(255, 255, 255, 0.3);
                    padding-bottom: 10px;
                }
                .metric {
                    display: flex;
                    justify-content: space-between;
                    margin: 10px 0;
                    padding: 5px 0;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                .metric-label {
                    font-weight: bold;
                }
                .metric-value {
                    color: #4ade80;
                }
                .negative {
                    color: #f87171;
                }
                .positive {
                    color: #4ade80;
                }
                .refresh-btn {
                    background: #4ade80;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 16px;
                    margin: 10px;
                }
                .refresh-btn:hover {
                    background: #22c55e;
                }
                .auto-refresh {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 20px 0;
                }
                .auto-refresh input {
                    margin-right: 10px;
                }
                .loading {
                    text-align: center;
                    padding: 20px;
                    font-style: italic;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 ByBit Grid Trading Bot</h1>
                    <p>Real-time monitoring dashboard</p>
                </div>
                
                <div style="text-align: center;">
                    <button class="refresh-btn" onclick="loadStatus()">🔄 Refresh Status</button>
                    <div class="auto-refresh">
                        <input type="checkbox" id="autoRefresh" onchange="toggleAutoRefresh()">
                        <label for="autoRefresh">Auto-refresh every 30 seconds</label>
                    </div>
                </div>
                
                <div id="status" class="loading">Loading status...</div>
            </div>
            
            <script>
                let autoRefreshInterval = null;
                
                async function loadStatus() {
                    try {
                        const response = await fetch('/api/status');
                        const data = await response.json();
                        displayStatus(data);
                    } catch (error) {
                        document.getElementById('status').innerHTML = '<div class="card"><h3>Error</h3><p>Failed to load status: ' + error.message + '</p></div>';
                    }
                }
                
                function displayStatus(data) {
                    const statusDiv = document.getElementById('status');
                    
                    const html = `
                        <div class="status-grid">
                            <div class="card">
                                <h3>💰 Market Info</h3>
                                <div class="metric">
                                    <span class="metric-label">Current BTC Price:</span>
                                    <span class="metric-value">$${data.current_price ? data.current_price.toLocaleString() : 'N/A'}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Last Updated:</span>
                                    <span class="metric-value">${data.timestamp}</span>
                                </div>
                            </div>
                            
                            <div class="card">
                                <h3>💳 Account</h3>
                                <div class="metric">
                                    <span class="metric-label">Balance:</span>
                                    <span class="metric-value">$${data.account_balance ? data.account_balance.toLocaleString() : 'N/A'}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Available:</span>
                                    <span class="metric-value">$${data.available_balance ? data.available_balance.toLocaleString() : 'N/A'}</span>
                                </div>
                            </div>
                            
                            <div class="card">
                                <h3>📈 Trading</h3>
                                <div class="metric">
                                    <span class="metric-label">Total PnL:</span>
                                    <span class="metric-value ${data.total_pnl >= 0 ? 'positive' : 'negative'}">$${data.total_pnl ? data.total_pnl.toLocaleString() : '0.00'}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Daily PnL:</span>
                                    <span class="metric-value ${data.daily_pnl >= 0 ? 'positive' : 'negative'}">$${data.daily_pnl ? data.daily_pnl.toLocaleString() : '0.00'}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Trade Count:</span>
                                    <span class="metric-value">${data.trade_count || 0}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Active Positions:</span>
                                    <span class="metric-value">${data.active_positions || 0}</span>
                                </div>
                            </div>
                            
                            <div class="card">
                                <h3>🎯 Strategy</h3>
                                <div class="metric">
                                    <span class="metric-label">Cover Loss Multiplier:</span>
                                    <span class="metric-value">${data.cover_loss_multiplier ? data.cover_loss_multiplier.toFixed(2) : '1.00'}x</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Consecutive Losses:</span>
                                    <span class="metric-value">${data.consecutive_losses || 0}</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Grid Levels:</span>
                                    <span class="metric-value">${data.grid_levels || 0}</span>
                                </div>
                            </div>
                            
                            <div class="card">
                                <h3>💻 System</h3>
                                <div class="metric">
                                    <span class="metric-label">CPU Usage:</span>
                                    <span class="metric-value">${data.cpu_usage ? data.cpu_usage.toFixed(1) : '0.0'}%</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Memory Usage:</span>
                                    <span class="metric-value">${data.memory_usage ? data.memory_usage.toFixed(1) : '0.0'}%</span>
                                </div>
                                <div class="metric">
                                    <span class="metric-label">Uptime:</span>
                                    <span class="metric-value">${data.uptime ? Math.floor(data.uptime / 60) : 0} minutes</span>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    statusDiv.innerHTML = html;
                }
                
                function toggleAutoRefresh() {
                    const checkbox = document.getElementById('autoRefresh');
                    if (checkbox.checked) {
                        autoRefreshInterval = setInterval(loadStatus, 30000);
                        loadStatus();
                    } else {
                        if (autoRefreshInterval) {
                            clearInterval(autoRefreshInterval);
                            autoRefreshInterval = null;
                        }
                    }
                }
                
                // Load status on page load
                loadStatus();
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def status_handler(self, request):
        """API endpoint for getting bot status."""
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
            account_balance = None
            available_balance = None
            if account_info.get('retCode') == 0:
                result = account_info.get('result', {})
                list_data = result.get('list', [])
                if list_data:
                    wallet = list_data[0]
                    account_balance = float(wallet.get('walletBalance', 0))
                    available_balance = float(wallet.get('availableBalance', 0))
            
            # Get strategy status
            strategy_status = self.strategy.get_status()
            
            # Get system metrics
            await self.monitor.update_system_metrics()
            system_metrics = self.monitor.get_metrics()
            
            # Get grid levels
            grid_levels = self.config.get_grid_levels()
            
            status_data = {
                'current_price': current_price,
                'account_balance': account_balance,
                'available_balance': available_balance,
                'total_pnl': strategy_status.get('total_pnl', 0),
                'daily_pnl': strategy_status.get('daily_pnl', 0),
                'trade_count': strategy_status.get('trade_count', 0),
                'active_positions': strategy_status.get('active_positions', 0),
                'cover_loss_multiplier': strategy_status.get('cover_loss_multiplier', 1.0),
                'consecutive_losses': strategy_status.get('consecutive_losses', 0),
                'grid_levels': len(grid_levels),
                'cpu_usage': system_metrics.get('cpu_usage', 0),
                'memory_usage': system_metrics.get('memory_usage', 0),
                'uptime': system_metrics.get('uptime', 0),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return web.json_response(status_data)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)


async def main():
    """Main function to start the web dashboard."""
    dashboard = WebDashboard()
    
    if not await dashboard.initialize():
        print("❌ Failed to initialize dashboard")
        return
    
    print("🌐 Starting ByBit Grid Trading Bot Dashboard...")
    print("📱 Open your browser and go to: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop the dashboard")
    
    try:
        runner = web.AppRunner(dashboard.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 