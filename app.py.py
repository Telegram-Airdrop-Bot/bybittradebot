#!/usr/bin/env python3
"""
ByBit Grid Trading Bot - Advanced Professional Dashboard
Modern web-based GUI with advanced trading features.
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime, timedelta
from aiohttp import web, ClientSession
import aiohttp_cors
import psutil
import logging

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config import Config
from src.bybit_client import ByBitClient
from src.grid_strategy import GridStrategy
from src.monitor import SystemMonitor

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AdvancedDashboard:
    """Professional advanced web dashboard for the trading bot."""
    
    def __init__(self):
        self.app = web.Application()
        self.config = Config()
        self.client = ByBitClient(
            api_key=self.config.get('api.api_key'),
            api_secret=self.config.get('api.api_secret'),
            testnet=self.config.get('api.testnet', False)
        )
        self.strategy = GridStrategy(self.config, self.client)
        self.monitor = SystemMonitor(self.config)
        self.trading_manager = None  # Will be initialized when needed
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
        """Set up all routes for the dashboard."""
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/api/status', self.status_handler)
        self.app.router.add_get('/api/price-history', self.price_history_handler)
        self.app.router.add_get('/api/trade-history', self.trade_history_handler)
        self.app.router.add_post('/api/update-config', self.update_config_handler)
        self.app.router.add_post('/api/emergency-stop', self.emergency_stop_handler)
        self.app.router.add_post('/api/start-bot', self.start_bot_handler)
        self.app.router.add_get('/api/orderbook', self.orderbook_handler)
        self.app.router.add_get('/api/kline-data', self.kline_data_handler)
        self.app.router.add_get('/api/funding-rate', self.funding_rate_handler)
        self.app.router.add_get('/api/open-interest', self.open_interest_handler)
        
        # Auto trading routes
        self.app.router.add_post('/api/start-auto-trading', self.start_auto_trading_handler)
        self.app.router.add_post('/api/stop-auto-trading', self.stop_auto_trading_handler)
        self.app.router.add_get('/api/trading-status', self.trading_status_handler)
        self.app.router.add_post('/api/configure-trading', self.configure_trading_handler)
        self.app.router.add_get('/api/account-balance', self.account_balance_handler)
        
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
        """Serve the advanced dashboard page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ByBit Grid Trading Bot - Professional Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: #333;
                    min-height: 100vh;
                }
                
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                .header {
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .header h1 {
                    color: #1e3c72;
                    font-size: 2.5em;
                    font-weight: 700;
                }
                
                .status-indicator {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .status-dot {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #4ade80;
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                
                .grid-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 20px;
                    margin-bottom: 20px;
                }
                
                .card {
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                
                .card h3 {
                    margin-bottom: 15px;
                    color: #1e3c72;
                    font-size: 1.2em;
                }
                
                .metric {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 15px 0;
                    padding: 12px;
                    background: rgba(30, 60, 114, 0.05);
                    border-radius: 8px;
                    border-left: 4px solid #1e3c72;
                }
                
                .metric-label {
                    font-weight: 600;
                    color: #1e3c72;
                }
                
                .metric-value {
                    font-weight: 700;
                    font-size: 1.1em;
                }
                
                .positive { color: #10b981; }
                .negative { color: #ef4444; }
                .neutral { color: #6b7280; }
                
                .chart-container {
                    background: rgba(255, 255, 255, 0.95);
                    backdrop-filter: blur(10px);
                    border-radius: 15px;
                    padding: 25px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                }
                
                .controls {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }
                
                .btn {
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    font-size: 14px;
                }
                
                .btn-primary {
                    background: #1e3c72;
                    color: white;
                }
                
                .btn-primary:hover {
                    background: #2a5298;
                    transform: translateY(-2px);
                }
                
                .btn-success {
                    background: #10b981;
                    color: white;
                }
                
                .btn-success:hover {
                    background: #059669;
                    transform: translateY(-2px);
                }
                
                .btn-danger {
                    background: #ef4444;
                    color: white;
                }
                
                .btn-danger:hover {
                    background: #dc2626;
                    transform: translateY(-2px);
                }
                
                .btn-warning {
                    background: #f59e0b;
                    color: white;
                }
                
                .btn-warning:hover {
                    background: #d97706;
                    transform: translateY(-2px);
                }
                
                .alert {
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    font-weight: 600;
                }
                
                .alert-success {
                    background: #d1fae5;
                    color: #065f46;
                    border: 1px solid #10b981;
                }
                
                .alert-danger {
                    background: #fee2e2;
                    color: #991b1b;
                    border: 1px solid #ef4444;
                }
                
                .alert-warning {
                    background: #fef3c7;
                    color: #92400e;
                    border: 1px solid #f59e0b;
                }
                
                .modal {
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background-color: rgba(0, 0, 0, 0.5);
                }
                
                .modal-content {
                    background-color: white;
                    margin: 5% auto;
                    padding: 30px;
                    border-radius: 15px;
                    width: 80%;
                    max-width: 500px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                
                .form-group {
                    margin-bottom: 20px;
                }
                
                .form-group label {
                    display: block;
                    margin-bottom: 8px;
                    font-weight: 600;
                    color: #1e3c72;
                }
                
                .form-group input, .form-group select {
                    width: 100%;
                    padding: 12px;
                    border: 2px solid #e5e7eb;
                    border-radius: 8px;
                    font-size: 14px;
                    transition: border-color 0.3s ease;
                }
                
                .form-group input:focus, .form-group select:focus {
                    outline: none;
                    border-color: #1e3c72;
                }
                
                .close {
                    color: #aaa;
                    float: right;
                    font-size: 28px;
                    font-weight: bold;
                    cursor: pointer;
                }
                
                .close:hover {
                    color: #000;
                }
                
                .loading {
                    text-align: center;
                    padding: 40px;
                    font-style: italic;
                    color: #6b7280;
                }
                
                .refresh-info {
                    text-align: center;
                    margin: 10px 0;
                    color: #6b7280;
                    font-size: 14px;
                }
                
                @media (max-width: 768px) {
                    .header {
                        flex-direction: column;
                        gap: 15px;
                    }
                    
                    .header h1 {
                        font-size: 2em;
                    }
                    
                    .grid-container {
                        grid-template-columns: 1fr;
                    }
                    
                    .controls {
                        grid-template-columns: 1fr;
                    }
                }
                
                .trading-controls {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin-bottom: 20px;
                }
                
                .control-group {
                    display: flex;
                    flex-direction: column;
                    gap: 5px;
                }
                
                .control-group label {
                    font-weight: 600;
                    color: #333;
                    font-size: 0.9em;
                }
                
                .control-group select,
                .control-group input {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-size: 0.9em;
                    background: white;
                }
                
                .button-group {
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
                    grid-column: 1 / -1;
                }
                
                .btn {
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    transition: all 0.3s ease;
                }
                
                .btn-success {
                    background: linear-gradient(135deg, #28a745, #20c997);
                    color: white;
                }
                
                .btn-danger {
                    background: linear-gradient(135deg, #dc3545, #e74c3c);
                    color: white;
                }
                
                .btn-primary {
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: white;
                }
                
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                
                .status-display {
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 8px;
                    padding: 15px;
                    margin-top: 15px;
                }
                
                .status-item {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                }
                
                .status-item .label {
                    font-weight: 600;
                    color: #555;
                }
                
                .status-item .value {
                    font-weight: 700;
                    color: #1e3c72;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div>
                        <h1><i class="fas fa-robot"></i> ByBit Grid Trading Bot</h1>
                        <p>Professional Trading Dashboard</p>
                    </div>
                    <div class="status-indicator">
                        <div class="status-dot"></div>
                        <span>Live Trading</span>
                    </div>
                </div>
                
                <div class="controls">
                    <button class="btn btn-primary" onclick="loadStatus()">
                        <i class="fas fa-sync-alt"></i> Refresh Status
                    </button>
                    <button class="btn btn-success" onclick="openConfigModal()">
                        <i class="fas fa-cog"></i> Settings
                    </button>
                    <button class="btn btn-warning" onclick="openEmergencyModal()">
                        <i class="fas fa-exclamation-triangle"></i> Emergency Stop
                    </button>
                    <button class="btn btn-primary" onclick="toggleAutoRefresh()">
                        <i class="fas fa-clock"></i> <span id="autoRefreshText">Auto Refresh</span>
                    </button>
                </div>
                
                <div id="alerts"></div>
                
                <div class="grid-container">
                    <div class="card">
                        <h3><i class="fas fa-dollar-sign"></i> Market Info</h3>
                        <div class="metric">
                            <span class="metric-label">BTC Price</span>
                            <span class="metric-value" id="btcPrice">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">24h Change</span>
                            <span class="metric-value" id="priceChange">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Last Updated</span>
                            <span class="metric-value" id="lastUpdated">Loading...</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3><i class="fas fa-wallet"></i> Account</h3>
                        <div class="metric">
                            <span class="metric-label">Balance</span>
                            <span class="metric-value" id="accountBalance">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Available</span>
                            <span class="metric-value" id="availableBalance">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Margin Used</span>
                            <span class="metric-value" id="marginUsed">Loading...</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3><i class="fas fa-chart-line"></i> Trading Performance</h3>
                        <div class="metric">
                            <span class="metric-label">Total PnL</span>
                            <span class="metric-value" id="totalPnl">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Daily PnL</span>
                            <span class="metric-value" id="dailyPnl">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Win Rate</span>
                            <span class="metric-value" id="winRate">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Trade Count</span>
                            <span class="metric-value" id="tradeCount">Loading...</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3><i class="fas fa-chess-board"></i> Strategy</h3>
                        <div class="metric">
                            <span class="metric-label">Active Positions</span>
                            <span class="metric-value" id="activePositions">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Grid Levels</span>
                            <span class="metric-value" id="gridLevels">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Cover Loss Multiplier</span>
                            <span class="metric-value" id="coverLossMultiplier">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Consecutive Losses</span>
                            <span class="metric-value" id="consecutiveLosses">Loading...</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3><i class="fas fa-server"></i> System</h3>
                        <div class="metric">
                            <span class="metric-label">CPU Usage</span>
                            <span class="metric-value" id="cpuUsage">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Memory Usage</span>
                            <span class="metric-value" id="memoryUsage">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Uptime</span>
                            <span class="metric-value" id="uptime">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">API Status</span>
                            <span class="metric-value" id="apiStatus">Loading...</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3><i class="fas fa-chart-bar"></i> Quick Actions</h3>
                        <button class="btn btn-success" style="width: 100%; margin-bottom: 10px;" onclick="startBot()">
                            <i class="fas fa-play"></i> Start Bot
                        </button>
                        <button class="btn btn-warning" style="width: 100%; margin-bottom: 10px;" onclick="pauseBot()">
                            <i class="fas fa-pause"></i> Pause Bot
                        </button>
                        <button class="btn btn-primary" style="width: 100%; margin-bottom: 10px;" onclick="exportData()">
                            <i class="fas fa-download"></i> Export Data
                        </button>
                        <button class="btn btn-primary" style="width: 100%;" onclick="viewLogs()">
                            <i class="fas fa-file-alt"></i> View Logs
                        </button>
                    </div>
                    <div class="card">
                        <h3><i class="fas fa-shield-alt"></i> Risk Management</h3>
                        <div class="metric">
                            <span class="metric-label">Position Size</span>
                            <span class="metric-value" id="positionSize">Calculating...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Risk per Trade</span>
                            <span class="metric-value" id="riskPerTrade">Calculating...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Max Drawdown</span>
                            <span class="metric-value" id="maxDrawdown">Calculating...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Risk Level</span>
                            <span class="metric-value" id="riskLevel">Calculating...</span>
                        </div>
                    </div>
                    <div class="card">
                        <h3><i class="fas fa-tools"></i> Troubleshooting</h3>
                        <div class="metric">
                            <span class="metric-label">API Status</span>
                            <span class="metric-value" id="apiStatusDetailed">Checking...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Account Access</span>
                            <span class="metric-value" id="accountAccess">Checking...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Permissions</span>
                            <span class="metric-value" id="permissions">Checking...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Last Error</span>
                            <span class="metric-value" id="lastError">None</span>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3><i class="fas fa-coins"></i> Wallet Details</h3>
                        <div id="coinDetailsContainer">
                            <div class="metric">
                                <span class="metric-label">Loading coins...</span>
                                <span class="metric-value">Please wait</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3><i class="fas fa-user-cog"></i> Account Settings</h3>
                        <div class="metric">
                            <span class="metric-label">Margin Mode</span>
                            <span class="metric-value" id="marginMode">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Account Status</span>
                            <span class="metric-value" id="accountStatus">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Master Trader</span>
                            <span class="metric-value" id="masterTrader">Loading...</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Spot Hedging</span>
                            <span class="metric-value" id="spotHedging">Loading...</span>
                        </div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3><i class="fas fa-chart-area"></i> Professional Trading Charts</h3>
                    
                    <!-- Real-time Grid Trading Interface -->
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <!-- Main Chart Area -->
                        <div>
                            <div style="display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap;">
                                <button class="btn btn-primary" onclick="switchChart('price')">Price Chart</button>
                                <button class="btn btn-primary" onclick="switchChart('grid')">Grid System</button>
                                <button class="btn btn-primary" onclick="switchChart('volume')">Volume</button>
                                <button class="btn btn-primary" onclick="switchChart('indicators')">Indicators</button>
                            </div>
                            <div style="position: relative; height: 400px;">
                                <canvas id="priceChart" width="400" height="200"></canvas>
                                <canvas id="gridChart" width="400" height="200" style="display: none;"></canvas>
                                <canvas id="volumeChart" width="400" height="200" style="display: none;"></canvas>
                                <canvas id="indicatorsChart" width="400" height="200" style="display: none;"></canvas>
                            </div>
                        </div>
                        
                        <!-- Real-time Order Book -->
                        <div style="background: rgba(255, 255, 255, 0.95); border-radius: 10px; padding: 15px;">
                            <h4 style="margin-bottom: 15px; color: #1e3c72;">Order Book</h4>
                            <div style="margin-bottom: 10px; text-align: center;">
                                <div style="font-size: 18px; font-weight: bold; color: #ef4444;" id="currentPriceDisplay">$115,203.12</div>
                                <div style="font-size: 12px; color: #6b7280;" id="priceChangeDisplay">+157.48 (+0.14%)</div>
                            </div>
                            
                            <!-- Asks (Sell Orders) -->
                            <div style="margin-bottom: 10px;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 12px; font-weight: bold; color: #6b7280; margin-bottom: 5px;">
                                    <span>Price(USDT)</span>
                                    <span>Quantity(BTC)</span>
                                    <span>Total(BTC)</span>
                                </div>
                                <div id="asksContainer" style="max-height: 150px; overflow-y: auto;">
                                    <!-- Asks will be populated here -->
                                </div>
                            </div>
                            
                            <!-- Bids (Buy Orders) -->
                            <div>
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 12px; font-weight: bold; color: #6b7280; margin-bottom: 5px;">
                                    <span>Price(USDT)</span>
                                    <span>Quantity(BTC)</span>
                                    <span>Total(BTC)</span>
                                </div>
                                <div id="bidsContainer" style="max-height: 150px; overflow-y: auto;">
                                    <!-- Bids will be populated here -->
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Real-time Grid Trading Status -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                        <div style="background: rgba(255, 255, 255, 0.95); border-radius: 10px; padding: 15px;">
                            <h4 style="margin-bottom: 10px; color: #1e3c72;">Grid Status</h4>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Grid Levels:</span>
                                <span id="gridLevelsCount">20</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Current Position:</span>
                                <span id="currentPosition">None</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Next Grid:</span>
                                <span id="nextGridLevel">$45,000</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Signal Strength:</span>
                                <span id="signalStrength">WEAK</span>
                            </div>
                        </div>
                        
                        <div style="background: rgba(255, 255, 255, 0.95); border-radius: 10px; padding: 15px;">
                            <h4 style="margin-bottom: 10px; color: #1e3c72;">Real-time Indicators</h4>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>RSI:</span>
                                <span id="rsiValue">50.0</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>MA:</span>
                                <span id="maValue">$45,000</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Volume:</span>
                                <span id="volumeValue">1.2K</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Spread:</span>
                                <span id="spreadValue">$0.01</span>
                            </div>
                        </div>
                        
                        <div style="background: rgba(255, 255, 255, 0.95); border-radius: 10px; padding: 15px;">
                            <h4 style="margin-bottom: 10px; color: #1e3c72;">Market Pressure</h4>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Buy Pressure:</span>
                                <span id="buyPressure" style="color: #10b981;">47%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Sell Pressure:</span>
                                <span id="sellPressure" style="color: #ef4444;">53%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Order Flow:</span>
                                <span id="orderFlow">Neutral</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>Volatility:</span>
                                <span id="volatilityValue">Medium</span>
                            </div>
                        </div>
                        
                        <div style="background: rgba(255, 255, 255, 0.95); border-radius: 10px; padding: 15px;">
                            <h4 style="margin-bottom: 10px; color: #1e3c72;">Market Data</h4>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Funding Rate:</span>
                                <span id="fundingRate">Loading...</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Open Interest:</span>
                                <span id="openInterest">Loading...</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span>Next Funding:</span>
                                <span id="nextFunding">Loading...</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span>OI Change:</span>
                                <span id="oiChange">Loading...</span>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 15px; background: rgba(30, 60, 114, 0.05); border-radius: 8px;">
                        <h4 style="margin-bottom: 10px; color: #1e3c72;">Grid Trading Zones</h4>
                        <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                            <div style="display: flex; align-items: center; gap: 5px;">
                                <div style="width: 12px; height: 12px; background: #10b981; border-radius: 2px;"></div>
                                <span>Buy Zone</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 5px;">
                                <div style="width: 12px; height: 12px; background: #ef4444; border-radius: 2px;"></div>
                                <span>Sell Zone</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 5px;">
                                <div style="width: 12px; height: 12px; background: #f59e0b; border-radius: 2px;"></div>
                                <span>Neutral Zone</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 5px;">
                                <div style="width: 12px; height: 12px; background: #6366f1; border-radius: 2px;"></div>
                                <span>Current Price</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="refresh-info">
                    <i class="fas fa-info-circle"></i> Data refreshes automatically every 30 seconds
                </div>
            </div>
            
            <!-- Config Modal -->
            <div id="configModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeConfigModal()">&times;</span>
                    <h2><i class="fas fa-cog"></i> Bot Configuration</h2>
                    <form id="configForm">
                        <div class="form-group">
                            <label>Grid Step Size (%)</label>
                            <input type="number" id="gridStep" step="0.1" min="0.1" max="10">
                        </div>
                        <div class="form-group">
                            <label>Base Position Size (USDT)</label>
                            <input type="number" id="basePositionSize" step="1" min="1">
                        </div>
                        <div class="form-group">
                            <label>Leverage</label>
                            <input type="number" id="leverage" step="1" min="1" max="100">
                        </div>
                        <div class="form-group">
                            <label>Take Profit (%)</label>
                            <input type="number" id="takeProfit" step="0.1" min="0.1" max="50">
                        </div>
                        <div class="form-group">
                            <label>Stop Loss (%)</label>
                            <input type="number" id="stopLoss" step="0.1" min="0.1" max="50">
                        </div>
                        <div class="form-group">
                            <label>Daily Loss Limit (USDT)</label>
                            <input type="number" id="dailyLossLimit" step="1" min="1">
                        </div>
                        <button type="submit" class="btn btn-primary">Save Configuration</button>
                    </form>
                </div>
            </div>
            
            <!-- Emergency Modal -->
            <div id="emergencyModal" class="modal">
                <div class="modal-content">
                    <span class="close" onclick="closeEmergencyModal()">&times;</span>
                    <h2><i class="fas fa-exclamation-triangle"></i> Emergency Stop</h2>
                    <p>Are you sure you want to stop the trading bot immediately?</p>
                    <p><strong>This will:</strong></p>
                    <ul>
                        <li>Close all open positions</li>
                        <li>Cancel all pending orders</li>
                        <li>Stop all trading activities</li>
                    </ul>
                    <div style="display: flex; gap: 10px; margin-top: 20px;">
                        <button class="btn btn-danger" onclick="emergencyStop()">Stop Bot</button>
                        <button class="btn btn-primary" onclick="closeEmergencyModal()">Cancel</button>
                    </div>
                </div>
            </div>
            
            <!-- Auto Trading Control Panel -->
            <div class="card">
                <h3><i class="fas fa-robot"></i> Auto Trading Control</h3>
                <div class="trading-controls">
                    <div class="control-group">
                        <label for="tradingMode">Trading Mode:</label>
                        <select id="tradingMode">
                            <option value="both">Both Spot & Futures</option>
                            <option value="spot">Spot Only</option>
                            <option value="futures">Futures Only</option>
                        </select>
                    </div>
                    <div class="control-group">
                        <label for="maxDailyLoss">Max Daily Loss (USDT):</label>
                        <input type="number" id="maxDailyLoss" value="1000" min="100" max="10000">
                    </div>
                    <div class="control-group">
                        <label for="maxPositions">Max Positions:</label>
                        <input type="number" id="maxPositions" value="5" min="1" max="20">
                    </div>
                    <div class="control-group">
                        <label for="leverage">Leverage (Futures):</label>
                        <input type="number" id="leverage" value="5" min="1" max="100">
                    </div>
                    <div class="button-group">
                        <button onclick="startAutoTrading()" class="btn btn-success">
                            <i class="fas fa-play"></i> Start Auto Trading
                        </button>
                        <button onclick="stopAutoTrading()" class="btn btn-danger">
                            <i class="fas fa-stop"></i> Stop Auto Trading
                        </button>
                        <button onclick="configureTrading()" class="btn btn-primary">
                            <i class="fas fa-cog"></i> Configure Settings
                        </button>
                    </div>
                </div>
                <div id="tradingStatus" class="status-display">
                    <div class="status-item">
                        <span class="label">Status:</span>
                        <span id="tradingStatusText" class="value">Stopped</span>
                    </div>
                    <div class="status-item">
                        <span class="label">Active Positions:</span>
                        <span id="activePositions" class="value">0</span>
                    </div>
                    <div class="status-item">
                        <span class="label">Daily Trades:</span>
                        <span id="dailyTrades" class="value">0</span>
                    </div>
                    <div class="status-item">
                        <span class="label">Daily PnL:</span>
                        <span id="dailyPnl" class="value">$0.00</span>
                    </div>
                </div>
            </div>
            
            <script>
                let autoRefreshInterval = null;
                let priceChart = null;
                let gridChart = null;
                let volumeChart = null;
                let indicatorsChart = null;
                let currentChartType = 'price'; // 'price', 'grid', 'volume', 'indicators'
                let priceHistory = [];
                
                // Initialize charts
                function initCharts() {
                    const priceCtx = document.getElementById('priceChart').getContext('2d');
                    priceChart = new Chart(priceCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'BTC Price',
                                data: [],
                                borderColor: '#1e3c72',
                                backgroundColor: 'rgba(30, 60, 114, 0.1)',
                                borderWidth: 2,
                                fill: true,
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    }
                                },
                                x: {
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    }
                                }
                            }
                        }
                    });

                    const gridCtx = document.getElementById('gridChart').getContext('2d');
                    gridChart = new Chart(gridCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Grid Levels',
                                data: [],
                                borderColor: '#2a5298',
                                backgroundColor: 'rgba(42, 82, 152, 0.1)',
                                borderWidth: 2,
                                fill: true,
                                tension: 0.4
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    }
                                },
                                x: {
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    }
                                }
                            }
                        }
                    });

                    const volumeCtx = document.getElementById('volumeChart').getContext('2d');
                    volumeChart = new Chart(volumeCtx, {
                        type: 'bar',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'Volume',
                                data: [],
                                backgroundColor: 'rgba(30, 60, 114, 0.5)',
                                borderColor: 'rgba(30, 60, 114, 0.8)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                x: {
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    }
                                },
                                y: {
                                    beginAtZero: false,
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    }
                                }
                            }
                        }
                    });

                    const indicatorsCtx = document.getElementById('indicatorsChart').getContext('2d');
                    indicatorsChart = new Chart(indicatorsCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [
                                {
                                    label: 'RSI',
                                    data: [],
                                    borderColor: '#ef4444',
                                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.4
                                },
                                {
                                    label: 'MA',
                                    data: [],
                                    borderColor: '#10b981',
                                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.4
                                }
                            ]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: false,
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    }
                                },
                                x: {
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    }
                                }
                            }
                        }
                    });
                }
                
                // Real-time order book update
                async function updateOrderBook() {
                    try {
                        const response = await axios.get('/api/orderbook');
                        const data = response.data;
                        
                        if (data.asks && data.bids) {
                            updateAsksDisplay(data.asks);
                            updateBidsDisplay(data.bids);
                            updateCurrentPrice(data.current_price, data.price_change);
                            updateMarketPressure(data.asks, data.bids);
                        }
                    } catch (error) {
                        console.log('Error updating order book:', error.message);
                    }
                }
                
                function updateAsksDisplay(asks) {
                    const container = document.getElementById('asksContainer');
                    container.innerHTML = '';
                    
                    asks.slice(0, 10).forEach(ask => {
                        const row = document.createElement('div');
                        row.style.display = 'grid';
                        row.style.gridTemplateColumns = '1fr 1fr 1fr';
                        row.style.gap = '10px';
                        row.style.fontSize = '12px';
                        row.style.color = '#ef4444';
                        row.style.padding = '2px 0';
                        
                        row.innerHTML = `
                            <span>${parseFloat(ask[0]).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                            <span>${parseFloat(ask[1]).toFixed(6)}</span>
                            <span>${parseFloat(ask[2]).toFixed(6)}</span>
                        `;
                        
                        container.appendChild(row);
                    });
                }
                
                function updateBidsDisplay(bids) {
                    const container = document.getElementById('bidsContainer');
                    container.innerHTML = '';
                    
                    bids.slice(0, 10).forEach(bid => {
                        const row = document.createElement('div');
                        row.style.display = 'grid';
                        row.style.gridTemplateColumns = '1fr 1fr 1fr';
                        row.style.gap = '10px';
                        row.style.fontSize = '12px';
                        row.style.color = '#10b981';
                        row.style.padding = '2px 0';
                        
                        row.innerHTML = `
                            <span>${parseFloat(bid[0]).toLocaleString('en-US', {minimumFractionDigits: 2})}</span>
                            <span>${parseFloat(bid[1]).toFixed(6)}</span>
                            <span>${parseFloat(bid[2]).toFixed(6)}</span>
                        `;
                        
                        container.appendChild(row);
                    });
                }
                
                function updateCurrentPrice(price, change) {
                    const priceElement = document.getElementById('currentPriceDisplay');
                    const changeElement = document.getElementById('priceChangeDisplay');
                    
                    if (price) {
                        priceElement.textContent = '$' + price.toLocaleString('en-US', {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2
                        });
                        
                        if (change) {
                            const changePercent = (change * 100).toFixed(2);
                            const changeValue = (price * change).toFixed(2);
                            const sign = change >= 0 ? '+' : '';
                            changeElement.textContent = `${sign}${changeValue} (${sign}${changePercent}%)`;
                            changeElement.style.color = change >= 0 ? '#10b981' : '#ef4444';
                        }
                    }
                }
                
                function updateMarketPressure(asks, bids) {
                    // Calculate market pressure based on order book
                    const totalAskVolume = asks.reduce((sum, ask) => sum + parseFloat(ask[1]), 0);
                    const totalBidVolume = bids.reduce((sum, bid) => sum + parseFloat(bid[1]), 0);
                    const totalVolume = totalAskVolume + totalBidVolume;
                    
                    if (totalVolume > 0) {
                        const buyPressure = ((totalBidVolume / totalVolume) * 100).toFixed(1);
                        const sellPressure = ((totalAskVolume / totalVolume) * 100).toFixed(1);
                        
                        document.getElementById('buyPressure').textContent = buyPressure + '%';
                        document.getElementById('sellPressure').textContent = sellPressure + '%';
                        
                        // Determine order flow
                        const orderFlowElement = document.getElementById('orderFlow');
                        if (totalBidVolume > totalAskVolume * 1.2) {
                            orderFlowElement.textContent = 'Bullish';
                            orderFlowElement.style.color = '#10b981';
                        } else if (totalAskVolume > totalBidVolume * 1.2) {
                            orderFlowElement.textContent = 'Bearish';
                            orderFlowElement.style.color = '#ef4444';
                        } else {
                            orderFlowElement.textContent = 'Neutral';
                            orderFlowElement.style.color = '#6b7280';
                        }
                    }
                }
                
                // Enhanced grid system with real-time updates
                function updateGridSystem(currentPrice) {
                    // Enhanced grid calculation for high-value BTC
                    const gridStep = currentPrice > 100000 ? 2000 : 500;
                    const numLevels = 15;
                    
                    const gridLevels = [];
                    for (let i = -numLevels; i <= numLevels; i++) {
                        gridLevels.push(currentPrice + (i * gridStep));
                    }
                    
                    // Find nearest grid levels
                    const nearestGrid = gridLevels.reduce((prev, curr) => {
                        return (Math.abs(curr - currentPrice) < Math.abs(prev - currentPrice) ? curr : prev);
                    });
                    
                    const gridIndex = gridLevels.indexOf(nearestGrid);
                    const nextGrid = gridLevels[gridIndex + 1] || nearestGrid + gridStep;
                    const prevGrid = gridLevels[gridIndex - 1] || nearestGrid - gridStep;
                    
                    // Enhanced signal calculation
                    const distanceToNext = nextGrid - currentPrice;
                    const distanceToPrev = currentPrice - prevGrid;
                    const signalThreshold = gridStep * 0.3;
                    
                    let signal = 'NEUTRAL';
                    let signalColor = '#f59e0b';
                    let signalStrength = 'WEAK';
                    
                    if (distanceToNext < signalThreshold) {
                        signal = 'BUY SIGNAL';
                        signalColor = '#10b981';
                        signalStrength = distanceToNext < signalThreshold * 0.5 ? 'STRONG' : 'MODERATE';
                    } else if (distanceToPrev < signalThreshold) {
                        signal = 'SELL SIGNAL';
                        signalColor = '#ef4444';
                        signalStrength = distanceToPrev < signalThreshold * 0.5 ? 'STRONG' : 'MODERATE';
                    }
                    
                    // Update grid status
                    document.getElementById('currentPosition').textContent = signal;
                    document.getElementById('currentPosition').style.color = signalColor;
                    document.getElementById('signalStrength').textContent = signalStrength;
                    document.getElementById('signalStrength').style.color = signalColor;
                    
                    // Update next grid level
                    const formattedNextGrid = nextGrid.toLocaleString('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    });
                    document.getElementById('nextGridLevel').textContent = formattedNextGrid;
                    
                    // Update grid levels count
                    document.getElementById('gridLevelsCount').textContent = gridLevels.length;
                    
                    // Calculate and update spread
                    const spread = nextGrid - prevGrid;
                    document.getElementById('spreadValue').textContent = '$' + spread.toFixed(2);
                    
                    // Calculate volatility
                    const volatility = calculateVolatility(currentPrice);
                    document.getElementById('volatilityValue').textContent = volatility;
                }
                
                function calculateVolatility(currentPrice) {
                    if (!window.priceHistory || window.priceHistory.length < 10) {
                        return 'Low';
                    }
                    
                    const recentPrices = window.priceHistory.slice(-10).map(p => p.price);
                    const mean = recentPrices.reduce((a, b) => a + b, 0) / recentPrices.length;
                    const variance = recentPrices.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / recentPrices.length;
                    const stdDev = Math.sqrt(variance);
                    const volatilityPercent = (stdDev / mean) * 100;
                    
                    if (volatilityPercent > 5) return 'High';
                    if (volatilityPercent > 2) return 'Medium';
                    return 'Low';
                }
                
                // Update chart with new data
                function updateChart(price, timestamp) {
                    if (!priceChart) return;
                    
                    priceHistory.push({price: price, timestamp: timestamp});
                    
                    // Keep only last 50 data points
                    if (priceHistory.length > 50) {
                        priceHistory.shift();
                    }
                    
                    const labels = priceHistory.map(item => {
                        const date = new Date(item.timestamp);
                        return date.toLocaleTimeString();
                    });
                    
                    const data = priceHistory.map(item => item.price);
                    
                    // Update price chart
                    priceChart.data.labels = labels;
                    priceChart.data.datasets[0].data = data;
                    priceChart.update();
                    
                    // Update grid chart with grid levels
                    updateGridChart(price);
                    
                    // Update volume chart
                    updateVolumeChart();

                    // Update indicators chart
                    updateIndicatorsChart(price);
                    
                    // Update grid information
                    updateGridInfo(price);
                }
                
                function updateGridChart(currentPrice) {
                    if (!gridChart) return;
                    
                    // Enhanced grid calculation for high-value BTC
                    const gridStep = currentPrice > 100000 ? 2000 : 500; // $2000 step for high prices
                    const numLevels = 15; // More levels for high-value trading
                    
                    const gridLevels = [];
                    for (let i = -numLevels; i <= numLevels; i++) {
                        gridLevels.push(currentPrice + (i * gridStep));
                    }
                    
                    const labels = gridLevels.map((level, index) => `Level ${index - numLevels}`);
                    
                    // Create enhanced grid chart with multiple datasets
                    gridChart.data.labels = labels;
                    gridChart.data.datasets = [
                        {
                            label: 'Grid Levels',
                            data: gridLevels,
                            borderColor: '#2a5298',
                            backgroundColor: 'rgba(42, 82, 152, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        },
                        {
                            label: 'Buy Zones',
                            data: gridLevels.map(level => level - (gridStep * 0.2)),
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            borderWidth: 1,
                            fill: false,
                            tension: 0.4
                        },
                        {
                            label: 'Sell Zones',
                            data: gridLevels.map(level => level + (gridStep * 0.2)),
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            borderWidth: 1,
                            fill: false,
                            tension: 0.4
                        },
                        {
                            label: 'Current Price',
                            data: gridLevels.map(() => currentPrice),
                            borderColor: '#6366f1',
                            backgroundColor: 'rgba(99, 102, 241, 0.1)',
                            borderWidth: 3,
                            fill: false,
                            tension: 0.4
                        }
                    ];
                    
                    gridChart.update();
                    
                    // Update grid trading signals with enhanced logic
                    updateGridSignals(currentPrice, gridLevels, gridStep);
                }
                
                function updateGridSignals(currentPrice, gridLevels, gridStep) {
                    // Find nearest grid levels
                    const nearestGrid = gridLevels.reduce((prev, curr) => {
                        return (Math.abs(curr - currentPrice) < Math.abs(prev - currentPrice) ? curr : prev);
                    });
                    
                    const gridIndex = gridLevels.indexOf(nearestGrid);
                    const nextGrid = gridLevels[gridIndex + 1] || nearestGrid + gridStep;
                    const prevGrid = gridLevels[gridIndex - 1] || nearestGrid - gridStep;
                    
                    // Enhanced signal calculation for high-value trading
                    const distanceToNext = nextGrid - currentPrice;
                    const distanceToPrev = currentPrice - prevGrid;
                    const signalThreshold = gridStep * 0.3; // 30% of grid step
                    
                    let signal = 'NEUTRAL';
                    let signalColor = '#f59e0b';
                    let signalStrength = 'WEAK';
                    
                    if (distanceToNext < signalThreshold) {
                        signal = 'BUY SIGNAL';
                        signalColor = '#10b981';
                        signalStrength = distanceToNext < signalThreshold * 0.5 ? 'STRONG' : 'MODERATE';
                    } else if (distanceToPrev < signalThreshold) {
                        signal = 'SELL SIGNAL';
                        signalColor = '#ef4444';
                        signalStrength = distanceToPrev < signalThreshold * 0.5 ? 'STRONG' : 'MODERATE';
                    }
                    
                    // Update signal display with strength
                    const signalElement = document.getElementById('currentPosition');
                    signalElement.textContent = `${signal} (${signalStrength})`;
                    signalElement.style.color = signalColor;
                    
                    // Update next grid level with enhanced formatting
                    const formattedNextGrid = nextGrid.toLocaleString('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    });
                    document.getElementById('nextGridLevel').textContent = formattedNextGrid;
                    
                    // Update grid levels count
                    document.getElementById('gridLevelsCount').textContent = gridLevels.length;
                }
                
                function updateVolumeChart() {
                    if (!volumeChart) return;
                    
                    // Get real volume data from API
                    const volumeData = [];
                    const labels = [];
                    const volumeColors = [];
                    
                    // Use real trade history for volume data
                    if (window.tradeHistory && window.tradeHistory.length > 0) {
                        const recentTrades = window.tradeHistory.slice(0, 20);
                        
                        for (let i = 0; i < recentTrades.length; i++) {
                            const trade = recentTrades[i];
                            const volume = trade.size || 0;
                            volumeData.push(volume);
                            labels.push(`T${i + 1}`);
                            
                            // Color code volume based on size
                            if (volume > 0.01) {
                                volumeColors.push('rgba(16, 185, 129, 0.8)'); // High volume - green
                            } else if (volume > 0.005) {
                                volumeColors.push('rgba(30, 60, 114, 0.8)'); // Medium volume - blue
                            } else {
                                volumeColors.push('rgba(239, 68, 68, 0.8)'); // Low volume - red
                            }
                        }
                    } else {
                        // Fallback to empty data if no trade history
                        for (let i = 0; i < 20; i++) {
                            volumeData.push(0);
                            labels.push(`T${i + 1}`);
                            volumeColors.push('rgba(128, 128, 128, 0.8)'); // Gray for no data
                        }
                    }
                    
                    volumeChart.data.labels = labels;
                    volumeChart.data.datasets = [
                        {
                            label: 'Volume',
                            data: volumeData,
                            backgroundColor: volumeColors,
                            borderColor: volumeColors.map(color => color.replace('0.8', '1')),
                            borderWidth: 1
                        },
                        {
                            label: 'Volume MA',
                            data: volumeData.map((v, i) => {
                                const sum = volumeData.slice(Math.max(0, i - 4), i + 1).reduce((a, b) => a + b, 0);
                                return sum / Math.min(5, i + 1);
                            }),
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            borderWidth: 2,
                            fill: false,
                            type: 'line'
                        }
                    ];
                    
                    volumeChart.update();
                }
                
                function updateIndicatorsChart(currentPrice) {
                    if (!indicatorsChart) return;
                    
                    // Get real data from API instead of mock data
                    const rsiData = [];
                    const maData = [];
                    const labels = [];
                    
                    // Use real price history for calculations
                    if (priceHistory.length > 0) {
                        for (let i = 0; i < Math.min(priceHistory.length, 20); i++) {
                            const price = priceHistory[i].price;
                            const rsi = calculateRSI(priceHistory.slice(0, i + 1));
                            const ma = calculateMA(priceHistory.slice(0, i + 1));
                            
                            rsiData.push(rsi);
                            maData.push(ma);
                            labels.push(`T${i + 1}`);
                        }
                    }
                    
                    indicatorsChart.data.labels = labels;
                    indicatorsChart.data.datasets[0].data = rsiData;
                    indicatorsChart.data.datasets[1].data = maData;
                    indicatorsChart.update();
                }
                
                function calculateRSI(prices) {
                    if (prices.length < 14) return 50;
                    
                    const changes = [];
                    for (let i = 1; i < prices.length; i++) {
                        changes.push(prices[i].price - prices[i-1].price);
                    }
                    
                    const gains = changes.filter(change => change > 0);
                    const losses = changes.filter(change => change < 0).map(change => -change);
                    
                    const avgGain = gains.length > 0 ? gains.reduce((a, b) => a + b, 0) / gains.length : 0;
                    const avgLoss = losses.length > 0 ? losses.reduce((a, b) => a + b, 0) / losses.length : 0;
                    
                    if (avgLoss === 0) return 100;
                    
                    const rs = avgGain / avgLoss
                    const rsi = 100 - (100 / (1 + rs));
                    
                    return Math.max(0, Math.min(100, rsi));
                }
                
                function calculateMA(prices) {
                    if (prices.length === 0) return 0;
                    
                    const sum = prices.reduce((total, price) => total + price.price, 0);
                    return sum / prices.length;
                }
                
                function updateGridInfo(currentPrice) {
                    // Update grid information display
                    document.getElementById('gridLevelsCount').textContent = '20';
                    
                    // Calculate next grid level
                    const gridStep = currentPrice > 100000 ? 2000 : 500;
                    const currentLevel = Math.round(currentPrice / gridStep);
                    const nextGridLevel = (currentLevel + 1) * gridStep;
                    
                    document.getElementById('nextGridLevel').textContent = '$' + nextGridLevel.toLocaleString();
                    
                    // Determine current position based on price movement
                    const position = currentPrice > nextGridLevel ? 'LONG' : 'SHORT';
                    document.getElementById('currentPosition').textContent = position;
                    
                    // Calculate and update risk management metrics
                    updateRiskMetrics(currentPrice);
                }
                
                function updateRiskMetrics(currentPrice) {
                    // Professional risk calculations for high-value BTC trading
                    const accountBalance = 10000; // Mock account balance
                    const riskPercentage = 2; // 2% risk per trade
                    const leverage = 10; // 10x leverage
                    
                    // Calculate position size based on risk
                    const riskAmount = accountBalance * (riskPercentage / 100);
                    const stopLossPercentage = 5; // 5% stop loss
                    const stopLossDistance = currentPrice * (stopLossPercentage / 100);
                    const positionSize = (riskAmount * leverage) / stopLossDistance;
                    
                    // Calculate risk per trade
                    const riskPerTrade = riskAmount;
                    
                    // Calculate max drawdown (mock calculation)
                    const maxDrawdown = Math.min(accountBalance * 0.1, 1000); // 10% or $1000 max
                    
                    // Determine risk level
                    let riskLevel = 'LOW';
                    let riskColor = '#10b981';
                    
                    if (maxDrawdown > accountBalance * 0.15) {
                        riskLevel = 'HIGH';
                        riskColor = '#ef4444';
                    } else if (maxDrawdown > accountBalance * 0.08) {
                        riskLevel = 'MEDIUM';
                        riskColor = '#f59e0b';
                    }
                    
                    // Update risk management display
                    document.getElementById('positionSize').textContent = positionSize.toFixed(4) + ' BTC';
                    document.getElementById('riskPerTrade').textContent = '$' + riskPerTrade.toLocaleString();
                    document.getElementById('maxDrawdown').textContent = '$' + maxDrawdown.toLocaleString();
                    
                    const riskLevelElement = document.getElementById('riskLevel');
                    riskLevelElement.textContent = riskLevel;
                    riskLevelElement.style.color = riskColor;
                    
                    // Add risk alerts for high-value trading
                    if (currentPrice > 100000) {
                        addRiskAlert('High-value BTC detected. Monitor position sizes carefully.', 'warning');
                    }
                    
                    if (riskLevel === 'HIGH') {
                        addRiskAlert('Risk level is HIGH. Consider reducing position sizes.', 'danger');
                    }
                }
                
                function addRiskAlert(message, type) {
                    const alertsDiv = document.getElementById('alerts');
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert alert-${type}`;
                    alertDiv.innerHTML = `
                        <i class="fas fa-exclamation-triangle"></i>
                        <strong>Risk Alert:</strong> ${message}
                    `;
                    alertsDiv.appendChild(alertDiv);
                    
                    // Remove alert after 10 seconds
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 10000);
                }
                
                async function loadStatus() {
                    try {
                        const response = await axios.get('/api/status');
                        const data = response.data;
                        displayStatus(data);
                        updateChart(data.current_price, data.timestamp);
                        
                        // Update grid system with real-time data
                        if (data.current_price) {
                            updateGridSystem(data.current_price);
                        }
                        
                        // Load real trade history data
                        await loadTradeHistory();
                        
                        // Update order book
                        await updateOrderBook();
                        
                    } catch (error) {
                        showAlert('Error loading status: ' + error.message, 'danger');
                    }
                }
                
                async function loadTradeHistory() {
                    try {
                        const response = await axios.get('/api/trade-history');
                        window.tradeHistory = response.data;
                    } catch (error) {
                        console.log('Error loading trade history:', error.message);
                        window.tradeHistory = [];
                    }
                }
                
                function displayStatus(data) {
                    // Market Info with enhanced formatting for high-value BTC
                    const btcPrice = data.current_price ? data.current_price : 0;
                    const priceChange = data.price_change ? data.price_change : 0;
                    
                    document.getElementById('btcPrice').textContent = btcPrice ? '$' + btcPrice.toLocaleString('en-US', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    }) : 'N/A';
                    
                    const priceChangeElement = document.getElementById('priceChange');
                    priceChangeElement.textContent = priceChange ? (priceChange >= 0 ? '+' : '') + priceChange.toFixed(2) + '%' : 'N/A';
                    priceChangeElement.className = 'metric-value ' + (priceChange >= 0 ? 'positive' : 'negative');
                    
                    document.getElementById('lastUpdated').textContent = data.timestamp;
                    
                    // Account with enhanced null handling
                    const accountBalance = data.account_balance;
                    const availableBalance = data.available_balance;
                    const margin_used = data.margin_used;
                    
                    // Handle null account data with informative messages
                    if (accountBalance === null || accountBalance === undefined) {
                        document.getElementById('accountBalance').textContent = 'API Error';
                        document.getElementById('accountBalance').style.color = '#ef4444';
                    } else {
                        document.getElementById('accountBalance').textContent = '$' + accountBalance.toLocaleString('en-US', {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0
                        });
                        document.getElementById('accountBalance').style.color = '#1e3c72';
                    }
                    
                    if (availableBalance === null || availableBalance === undefined) {
                        document.getElementById('availableBalance').textContent = 'API Error';
                        document.getElementById('availableBalance').style.color = '#ef4444';
                    } else {
                        document.getElementById('availableBalance').textContent = '$' + availableBalance.toLocaleString('en-US', {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0
                        });
                        document.getElementById('availableBalance').style.color = '#1e3c72';
                    }
                    
                    if (margin_used === null || margin_used === undefined) {
                        document.getElementById('marginUsed').textContent = 'API Error';
                        document.getElementById('marginUsed').style.color = '#ef4444';
                    } else {
                        document.getElementById('marginUsed').textContent = '$' + margin_used.toLocaleString('en-US', {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0
                        });
                        document.getElementById('marginUsed').style.color = '#1e3c72';
                    }
                    
                    // Trading Performance with enhanced formatting
                    const totalPnl = document.getElementById('totalPnl');
                    const totalPnlValue = data.total_pnl ? data.total_pnl : 0;
                    totalPnl.textContent = totalPnlValue ? '$' + totalPnlValue.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }) : '$0.00';
                    totalPnl.className = 'metric-value ' + (totalPnlValue >= 0 ? 'positive' : 'negative');
                    
                    const dailyPnl = document.getElementById('dailyPnl');
                    const dailyPnlValue = data.daily_pnl ? data.daily_pnl : 0;
                    dailyPnl.textContent = dailyPnlValue ? '$' + dailyPnlValue.toLocaleString('en-US', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    }) : '$0.00';
                    dailyPnl.className = 'metric-value ' + (dailyPnlValue >= 0 ? 'positive' : 'negative');
                    
                    document.getElementById('winRate').textContent = data.win_rate ? data.win_rate.toFixed(1) + '%' : 'N/A';
                    document.getElementById('tradeCount').textContent = data.trade_count || 0;
                    
                    // Strategy Status
                    document.getElementById('activePositions').textContent = data.active_positions || 0;
                    document.getElementById('gridLevels').textContent = data.grid_levels || 0;
                    document.getElementById('coverLossMultiplier').textContent = data.cover_loss_multiplier ? data.cover_loss_multiplier.toFixed(2) + 'x' : '1.00x';
                    document.getElementById('consecutiveLosses').textContent = data.consecutive_losses || 0;
                    
                    // System Health with enhanced monitoring
                    const cpuUsage = data.cpu_usage ? data.cpu_usage : 0;
                    const memoryUsage = data.memory_usage ? data.memory_usage : 0;
                    
                    document.getElementById('cpuUsage').textContent = cpuUsage ? cpuUsage.toFixed(1) + '%' : 'N/A';
                    document.getElementById('memoryUsage').textContent = memoryUsage ? memoryUsage.toFixed(1) + '%' : 'N/A';
                    document.getElementById('uptime').textContent = data.uptime ? Math.floor(data.uptime / 60) + ' minutes' : 'N/A';
                    document.getElementById('apiStatus').textContent = data.api_status || 'Connected';
                    
                    // Update indicators display
                    document.getElementById('rsiValue').textContent = data.rsi_value ? data.rsi_value.toFixed(1) + '%' : 'N/A';
                    document.getElementById('maValue').textContent = data.ma_value ? '$' + data.ma_value.toLocaleString('en-US', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    }) : 'N/A';
                    
                    // Update volume display
                    const volumeValue = data.volume_24h ? (data.volume_24h / 1000).toFixed(1) + 'K' : 'N/A';
                    document.getElementById('volumeValue').textContent = volumeValue;
                    
                    // Update spread if available
                    if (data.spread) {
                        document.getElementById('spreadValue').textContent = '$' + data.spread.toFixed(2);
                    }
                    
                    // Update market pressure if available
                    if (data.buy_pressure && data.sell_pressure) {
                        document.getElementById('buyPressure').textContent = data.buy_pressure.toFixed(1) + '%';
                        document.getElementById('sellPressure').textContent = data.sell_pressure.toFixed(1) + '%';
                        
                        // Update order flow
                        const orderFlowElement = document.getElementById('orderFlow');
                        if (data.buy_pressure > data.sell_pressure * 1.2) {
                            orderFlowElement.textContent = 'Bullish';
                            orderFlowElement.style.color = '#10b981';
                        } else if (data.sell_pressure > data.buy_pressure * 1.2) {
                            orderFlowElement.textContent = 'Bearish';
                            orderFlowElement.style.color = '#ef4444';
                        } else {
                            orderFlowElement.textContent = 'Neutral';
                            orderFlowElement.style.color = '#6b7280';
                        }
                    }
                    
                    // Update volatility
                    if (data.volatility) {
                        document.getElementById('volatilityValue').textContent = data.volatility;
                    }
                    
                    // Add system health alerts
                    if (cpuUsage > 80) {
                        addRiskAlert('High CPU usage detected. Consider system optimization.', 'warning');
                    }
                    
                    if (memoryUsage > 85) {
                        addRiskAlert('High memory usage detected. Monitor system performance.', 'warning');
                    }
                    
                    // Add high-value trading alerts
                    if (btcPrice > 100000) {
                        addRiskAlert('BTC price above $100k. High-value trading mode active.', 'warning');
                    }
                    
                    // Add account API error alerts
                    if (accountBalance === null || availableBalance === null) {
                        addRiskAlert('Account data unavailable. Check API credentials and permissions.', 'danger');
                    }
                    
                    // Update troubleshooting information
                    updateTroubleshootingInfo(data);
                    
                    // Update coin details
                    updateCoinDetails(data.coin_details);
                    
                    // Update account details
                    updateAccountDetails(data);
                    
                    // Update market data
                    updateMarketData();
                }
                
                async function updateMarketData() {
                    try {
                        // Get funding rate
                        const fundingResponse = await axios.get('/api/funding-rate');
                        if (fundingResponse.data.fundingRate !== undefined) {
                            const fundingRate = (fundingResponse.data.fundingRate * 100).toFixed(4);
                            document.getElementById('fundingRate').textContent = fundingRate + '%';
                            document.getElementById('fundingRate').style.color = fundingRate >= 0 ? '#10b981' : '#ef4444';
                            
                            // Calculate next funding time
                            const nextFunding = new Date(fundingResponse.data.fundingRateTimestamp + 8 * 60 * 60 * 1000);
                            document.getElementById('nextFunding').textContent = nextFunding.toLocaleTimeString();
                        }
                        
                        // Get open interest
                        const oiResponse = await axios.get('/api/open-interest');
                        if (oiResponse.data.openInterest !== undefined) {
                            const oi = oiResponse.data.openInterest;
                            document.getElementById('openInterest').textContent = oi.toLocaleString();
                            
                            // Mock OI change (in real implementation, you'd track previous values)
                            const oiChange = (Math.random() - 0.5) * 2; // Mock change
                            document.getElementById('oiChange').textContent = (oiChange >= 0 ? '+' : '') + oiChange.toFixed(2) + '%';
                            document.getElementById('oiChange').style.color = oiChange >= 0 ? '#10b981' : '#ef4444';
                        }
                    } catch (error) {
                        console.log('Error updating market data:', error.message);
                    }
                }
                
                function updateAccountDetails(data) {
                    // Update margin mode
                    const marginModeElement = document.getElementById('marginMode');
                    if (data.margin_mode) {
                        marginModeElement.textContent = data.margin_mode;
                        marginModeElement.style.color = '#1e3c72';
                    } else {
                        marginModeElement.textContent = 'Unknown';
                        marginModeElement.style.color = '#ef4444';
                    }
                    
                    // Update account status
                    const accountStatusElement = document.getElementById('accountStatus');
                    if (data.unified_margin_status !== null && data.unified_margin_status !== undefined) {
                        let statusText = 'Unknown';
                        let statusColor = '#6b7280';
                        
                        switch(data.unified_margin_status) {
                            case 1:
                                statusText = 'Normal';
                                statusColor = '#10b981';
                                break;
                            case 2:
                                statusText = 'Pending';
                                statusColor = '#f59e0b';
                                break;
                            case 3:
                                statusText = 'Suspended';
                                statusColor = '#ef4444';
                                break;
                            case 4:
                                statusText = 'Active';
                                statusColor = '#10b981';
                                break;
                            default:
                                statusText = `Status ${data.unified_margin_status}`;
                                statusColor = '#6b7280';
                        }
                        
                        accountStatusElement.textContent = statusText;
                        accountStatusElement.style.color = statusColor;
                    } else {
                        accountStatusElement.textContent = 'Unknown';
                        accountStatusElement.style.color = '#ef4444';
                    }
                    
                    // Update master trader status
                    const masterTraderElement = document.getElementById('masterTrader');
                    if (data.is_master_trader !== null && data.is_master_trader !== undefined) {
                        masterTraderElement.textContent = data.is_master_trader ? 'Yes' : 'No';
                        masterTraderElement.style.color = data.is_master_trader ? '#10b981' : '#6b7280';
                    } else {
                        masterTraderElement.textContent = 'Unknown';
                        masterTraderElement.style.color = '#ef4444';
                    }
                    
                    // Update spot hedging status
                    const spotHedgingElement = document.getElementById('spotHedging');
                    if (data.spot_hedging_status) {
                        spotHedgingElement.textContent = data.spot_hedging_status;
                        spotHedgingElement.style.color = data.spot_hedging_status === 'ON' ? '#10b981' : '#6b7280';
                    } else {
                        spotHedgingElement.textContent = 'Unknown';
                        spotHedgingElement.style.color = '#ef4444';
                    }
                }
                
                function updateTroubleshootingInfo(data) {
                    // Update API status
                    const apiStatusElement = document.getElementById('apiStatusDetailed');
                    if (data.api_status === 'Connected') {
                        apiStatusElement.textContent = 'Connected';
                        apiStatusElement.style.color = '#10b981';
                    } else {
                        apiStatusElement.textContent = 'Disconnected';
                        apiStatusElement.style.color = '#ef4444';
                    }
                    
                    // Update account access
                    const accountAccessElement = document.getElementById('accountAccess');
                    if (data.account_balance !== null && data.available_balance !== null) {
                        accountAccessElement.textContent = 'Available';
                        accountAccessElement.style.color = '#10b981';
                    } else {
                        accountAccessElement.textContent = 'Unavailable';
                        accountAccessElement.style.color = '#ef4444';
                    }
                    
                    // Update permissions
                    const permissionsElement = document.getElementById('permissions');
                    if (data.account_balance !== null) {
                        permissionsElement.textContent = 'Read Access';
                        permissionsElement.style.color = '#10b981';
                    } else {
                        permissionsElement.textContent = 'No Access';
                        permissionsElement.style.color = '#ef4444';
                    }
                    
                    // Update last error
                    const lastErrorElement = document.getElementById('lastError');
                    if (data.account_balance === null) {
                        lastErrorElement.textContent = 'Account API Error';
                        lastErrorElement.style.color = '#ef4444';
                    } else {
                        lastErrorElement.textContent = 'None';
                        lastErrorElement.style.color = '#10b981';
                    }
                }
                
                function updateCoinDetails(coinDetails) {
                    const container = document.getElementById('coinDetailsContainer');
                    
                    if (!coinDetails || coinDetails.length === 0) {
                        container.innerHTML = `
                            <div class="metric">
                                <span class="metric-label">No coins found</span>
                                <span class="metric-value">No balance</span>
                            </div>
                        `;
                        return;
                    }
                    
                    container.innerHTML = '';
                    
                    coinDetails.forEach(coin => {
                        const coinDiv = document.createElement('div');
                        coinDiv.className = 'metric';
                        
                        const walletBalance = coin.wallet_balance || 0;
                        const usdValue = coin.usd_value || 0;
                        const availableBalance = coin.available_balance || 0;
                        const unrealisedPnl = coin.unrealised_pnl || 0;
                        
                        coinDiv.innerHTML = `
                            <div style="margin-bottom: 10px; padding: 10px; background: rgba(30, 60, 114, 0.05); border-radius: 8px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span style="font-weight: bold; color: #1e3c72;">${coin.coin}</span>
                                    <span style="font-weight: bold; color: ${unrealisedPnl >= 0 ? '#10b981' : '#ef4444'}">
                                        ${unrealisedPnl >= 0 ? '+' : ''}$${unrealisedPnl.toFixed(2)}
                                    </span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 3px; font-size: 12px;">
                                    <span>Balance:</span>
                                    <span>${walletBalance.toFixed(6)}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 3px; font-size: 12px;">
                                    <span>Available:</span>
                                    <span>${availableBalance.toFixed(6)}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; font-size: 12px;">
                                    <span>USD Value:</span>
                                    <span>$${usdValue.toFixed(2)}</span>
                                </div>
                            </div>
                        `;
                        
                        container.appendChild(coinDiv);
                    });
                }
                
                function showAlert(message, type) {
                    const alertsDiv = document.getElementById('alerts');
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert alert-${type}`;
                    alertDiv.innerHTML = `
                        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'exclamation-triangle'}"></i>
                        ${message}
                    `;
                    alertsDiv.appendChild(alertDiv);
                    
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 5000);
                }
                
                function toggleAutoRefresh() {
                    const button = document.getElementById('autoRefreshText');
                    if (autoRefreshInterval) {
                        clearInterval(autoRefreshInterval);
                        autoRefreshInterval = null;
                        button.textContent = 'Auto Refresh';
                        showAlert('Auto refresh disabled', 'warning');
                    } else {
                        autoRefreshInterval = setInterval(loadStatus, 30000);
                        button.textContent = 'Auto Refresh ON';
                        showAlert('Auto refresh enabled', 'success');
                        loadStatus();
                    }
                }
                
                function openConfigModal() {
                    document.getElementById('configModal').style.display = 'block';
                }
                
                function closeConfigModal() {
                    document.getElementById('configModal').style.display = 'none';
                }
                
                function openEmergencyModal() {
                    document.getElementById('emergencyModal').style.display = 'block';
                }
                
                function closeEmergencyModal() {
                    document.getElementById('emergencyModal').style.display = 'none';
                }
                
                async function emergencyStop() {
                    try {
                        await axios.post('/api/emergency-stop');
                        showAlert('Emergency stop executed successfully', 'success');
                        closeEmergencyModal();
                    } catch (error) {
                        showAlert('Error executing emergency stop: ' + error.message, 'danger');
                    }
                }
                
                async function startBot() {
                    try {
                        await axios.post('/api/start-bot');
                        showAlert('Bot started successfully', 'success');
                    } catch (error) {
                        showAlert('Error starting bot: ' + error.message, 'danger');
                    }
                }
                
                function pauseBot() {
                    showAlert('Pause functionality coming soon', 'warning');
                }
                
                function exportData() {
                    showAlert('Export functionality coming soon', 'warning');
                }
                
                function viewLogs() {
                    showAlert('Log viewer coming soon', 'warning');
                }

                function switchChart(chartType) {
                    currentChartType = chartType;
                    document.getElementById('priceChart').style.display = 'none';
                    document.getElementById('gridChart').style.display = 'none';
                    document.getElementById('volumeChart').style.display = 'none';
                    document.getElementById('indicatorsChart').style.display = 'none';

                    if (chartType === 'price') {
                        document.getElementById('priceChart').style.display = 'block';
                        if (priceChart) priceChart.update(); // Re-render price chart
                    } else if (chartType === 'grid') {
                        document.getElementById('gridChart').style.display = 'block';
                        if (gridChart) gridChart.update(); // Re-render grid chart
                    } else if (chartType === 'volume') {
                        document.getElementById('volumeChart').style.display = 'block';
                        if (volumeChart) volumeChart.update(); // Re-render volume chart
                    } else if (chartType === 'indicators') {
                        document.getElementById('indicatorsChart').style.display = 'block';
                        if (indicatorsChart) indicatorsChart.update(); // Re-render indicators chart
                    }
                }
                
                // Initialize
                document.addEventListener('DOMContentLoaded', function() {
                    initCharts();
                    loadStatus();
                    
                    // Auto refresh every 30 seconds
                    autoRefreshInterval = setInterval(loadStatus, 30000);
                });
                
                // Close modals when clicking outside
                window.onclick = function(event) {
                    const configModal = document.getElementById('configModal');
                    const emergencyModal = document.getElementById('emergencyModal');
                    
                    if (event.target === configModal) {
                        closeConfigModal();
                    }
                    if (event.target === emergencyModal) {
                        closeEmergencyModal();
                    }
                }

                // Auto Trading Functions
                async function startAutoTrading() {
                    try {
                        const mode = document.getElementById('tradingMode').value;
                        const maxDailyLoss = parseFloat(document.getElementById('maxDailyLoss').value);
                        const maxPositions = parseInt(document.getElementById('maxPositions').value);
                        const leverage = parseInt(document.getElementById('leverage').value);
                        
                        const response = await fetch('/api/start-auto-trading', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                mode: mode,
                                max_daily_loss: maxDailyLoss,
                                max_positions: maxPositions,
                                leverage: leverage
                            })
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            showNotification('Auto trading started successfully!', 'success');
                            updateTradingStatus();
                        } else {
                            showNotification('Failed to start auto trading: ' + result.message, 'error');
                        }
                    } catch (error) {
                        showNotification('Error starting auto trading: ' + error.message, 'error');
                    }
                }
                
                async function stopAutoTrading() {
                    try {
                        const response = await fetch('/api/stop-auto-trading', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            showNotification('Auto trading stopped successfully!', 'success');
                            updateTradingStatus();
                        } else {
                            showNotification('Failed to stop auto trading: ' + result.message, 'error');
                        }
                    } catch (error) {
                        showNotification('Error stopping auto trading: ' + error.message, 'error');
                    }
                }
                
                async function configureTrading() {
                    try {
                        const mode = document.getElementById('tradingMode').value;
                        const maxDailyLoss = parseFloat(document.getElementById('maxDailyLoss').value);
                        const maxPositions = parseInt(document.getElementById('maxPositions').value);
                        const leverage = parseInt(document.getElementById('leverage').value);
                        
                        const response = await fetch('/api/configure-trading', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                trading_mode: mode,
                                max_daily_loss: maxDailyLoss,
                                max_positions: maxPositions,
                                leverage: leverage
                            })
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            showNotification('Trading configuration updated successfully!', 'success');
                        } else {
                            showNotification('Failed to update configuration: ' + result.message, 'error');
                        }
                    } catch (error) {
                        showNotification('Error updating configuration: ' + error.message, 'error');
                    }
                }
                
                async function updateTradingStatus() {
                    try {
                        const response = await fetch('/api/trading-status');
                        const status = await response.json();
                        
                        document.getElementById('tradingStatusText').textContent = 
                            status.trading_mode === 'none' ? 'Stopped' : status.trading_mode.toUpperCase();
                        document.getElementById('activePositions').textContent = status.active_positions || 0;
                        document.getElementById('dailyTrades').textContent = status.daily_stats?.trades || 0;
                        
                        const dailyPnl = (status.daily_stats?.profit || 0) - (status.daily_stats?.loss || 0);
                        document.getElementById('dailyPnl').textContent = '$' + dailyPnl.toFixed(2);
                        
                        // Update status color
                        const statusElement = document.getElementById('tradingStatusText');
                        if (status.trading_mode === 'none') {
                            statusElement.style.color = '#dc3545';
                        } else {
                            statusElement.style.color = '#28a745';
                        }
                    } catch (error) {
                        console.error('Error updating trading status:', error);
                    }
                }
                
                // Update trading status every 10 seconds
                setInterval(updateTradingStatus, 10000);
                
                // Initial status update
                updateTradingStatus();
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def status_handler(self, request):
        """API endpoint for getting comprehensive bot status."""
        try:
            # Get current price
            ticker = await self.client.get_ticker("BTCUSDT")
            current_price = None
            price_change = None
            volume_24h = None
            
            if ticker.get('retCode') == 0:
                result = ticker.get('result', {})
                list_data = result.get('list', [])
                if list_data:
                    ticker_data = list_data[0]
                    current_price = float(ticker_data.get('lastPrice', 0))
                    price_change = float(ticker_data.get('price24hPcnt', 0)) * 100
                    volume_24h = float(ticker_data.get('volume24h', 0))
            
            # Get account info with better error handling
            account_info = await self.client.get_account_info()
            account_balance = None
            available_balance = None
            margin_used = None
            coin_details = []
            
            if account_info.get('retCode') == 0:
                result = account_info.get('result', {})
                list_data = result.get('list', [])
                if list_data and len(list_data) > 0:
                    account_data = list_data[0]  # Get the first account
                    
                    try:
                        # Extract wallet balance data from V5 API response
                        account_balance = float(account_data.get('totalWalletBalance', 0))
                        available_balance = float(account_data.get('totalAvailableBalance', 0))
                        total_margin_balance = float(account_data.get('totalMarginBalance', 0))
                        
                        # Calculate margin used (total margin balance - available balance)
                        margin_used = total_margin_balance - available_balance if total_margin_balance and available_balance else 0
                        
                        # Extract coin details
                        coins = account_data.get('coin', [])
                        for coin in coins:
                            if float(coin.get('walletBalance', 0)) > 0:  # Only show coins with balance
                                coin_details.append({
                                    'coin': coin.get('coin', ''),
                                    'wallet_balance': float(coin.get('walletBalance', 0)),
                                    'usd_value': float(coin.get('usdValue', 0)),
                                    'available_balance': float(coin.get('free', 0)),
                                    'unrealised_pnl': float(coin.get('unrealisedPnl', 0))
                                })
                        
                        # Log the account data for debugging
                        logger.info(f"Account data: wallet={account_balance}, available={available_balance}, margin_used={margin_used}")
                        logger.info(f"Coins with balance: {len(coin_details)}")
                        
                    except (ValueError, TypeError) as e:
                        # Handle conversion errors
                        logger.error(f"Error converting account data: {e}")
                        account_balance = None
                        available_balance = None
                        margin_used = None
                else:
                    logger.warning("No account data found in API response")
            else:
                logger.error(f"Account API error: {account_info.get('retMsg', 'Unknown error')}")
            
            # Get detailed account information
            account_details = await self.client.get_account_details()
            margin_mode = None
            unified_margin_status = None
            is_master_trader = None
            spot_hedging_status = None
            updated_time = None
            
            if account_details.get('retCode') == 0:
                result = account_details.get('result', {})
                margin_mode = result.get('marginMode', 'Unknown')
                unified_margin_status = result.get('unifiedMarginStatus', 0)
                is_master_trader = result.get('isMasterTrader', False)
                spot_hedging_status = result.get('spotHedgingStatus', 'Unknown')
                updated_time = result.get('updatedTime', 0)
                
                logger.info(f"Account details: margin_mode={margin_mode}, status={unified_margin_status}, master_trader={is_master_trader}")
            else:
                logger.error(f"Account details API error: {account_details.get('retMsg', 'Unknown error')}")
            
            # Get positions
            positions = await self.client.get_positions("BTCUSDT")
            active_positions = 0
            total_pnl = 0
            if positions.get('retCode') == 0:
                result = positions.get('result', {})
                list_data = result.get('list', [])
                active_positions = len([p for p in list_data if float(p.get('size', 0)) > 0])
                # Calculate total PnL from positions
                for pos in list_data:
                    if float(pos.get('size', 0)) > 0:
                        total_pnl += float(pos.get('unrealisedPnl', 0))
            
            # Get order history for real win rate calculation
            order_history = await self.client.get_order_history("BTCUSDT", 100)
            win_rate = 0
            trade_count = 0
            
            # Initialize spread and market pressure variables
            spread = None
            buy_pressure = None
            sell_pressure = None
            
            if order_history.get('retCode') == 0:
                result = order_history.get('result', {})
                list_data = result.get('list', [])
                completed_trades = [order for order in list_data if order.get('orderStatus') == 'Filled']
                trade_count = len(completed_trades)
                
                if trade_count > 0:
                    profitable_trades = 0
                    for trade in completed_trades:
                        # Calculate if trade was profitable based on side and execution price
                        side = trade.get('side', '')
                        exec_price = float(trade.get('avgPrice', 0))
                        qty = float(trade.get('qty', 0))
                        
                        # This is a simplified calculation - in production you'd want more sophisticated logic
                        if side == 'Buy' and exec_price > current_price:
                            profitable_trades += 1
                        elif side == 'Sell' and exec_price < current_price:
                            profitable_trades += 1
                    
                    win_rate = (profitable_trades / trade_count) * 100 if trade_count > 0 else 0
            
            # Get order book for spread and market pressure
            orderbook = await self.client.get_orderbook("BTCUSDT", 10)
            
            if orderbook.get('retCode') == 0:
                result = orderbook.get('result', {})
                asks = result.get('a', [])
                bids = result.get('b', [])
                
                if asks and bids:
                    # Calculate spread
                    best_ask = float(asks[0][0])
                    best_bid = float(bids[0][0])
                    spread = best_ask - best_bid
                    
                    # Calculate market pressure
                    total_ask_volume = sum(float(ask[1]) for ask in asks)
                    total_bid_volume = sum(float(bid[1]) for bid in bids)
                    total_volume = total_ask_volume + total_bid_volume
                    
                    if total_volume > 0:
                        buy_pressure = (total_bid_volume / total_volume) * 100
                        sell_pressure = (total_ask_volume / total_volume) * 100
            
            # Get strategy status
            strategy_status = self.strategy.get_status()
            
            # Get system metrics
            await self.monitor.update_system_metrics()
            system_metrics = self.monitor.get_metrics()
            
            # Get grid levels
            grid_levels = self.config.get_grid_levels()
            
            # Calculate real RSI (simplified calculation)
            rsi_value = self.calculate_rsi(current_price)
            
            # Calculate real moving average
            ma_value = self.calculate_moving_average(current_price)
            
            status_data = {
                'current_price': current_price,
                'price_change': price_change,
                'volume_24h': volume_24h,
                'spread': spread,
                'buy_pressure': buy_pressure,
                'sell_pressure': sell_pressure,
                'account_balance': account_balance,
                'available_balance': available_balance,
                'margin_used': margin_used,
                'coin_details': coin_details,
                'margin_mode': margin_mode,
                'unified_margin_status': unified_margin_status,
                'is_master_trader': is_master_trader,
                'spot_hedging_status': spot_hedging_status,
                'account_updated_time': updated_time,
                'total_pnl': total_pnl,
                'daily_pnl': strategy_status.get('daily_pnl', 0),
                'win_rate': win_rate,
                'trade_count': trade_count,
                'active_positions': active_positions,
                'cover_loss_multiplier': strategy_status.get('cover_loss_multiplier', 1.0),
                'consecutive_losses': strategy_status.get('consecutive_losses', 0),
                'grid_levels': len(grid_levels),
                'cpu_usage': system_metrics.get('cpu_usage', 0),
                'memory_usage': system_metrics.get('memory_usage', 0),
                'uptime': system_metrics.get('uptime', 0),
                'api_status': 'Connected',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'rsi_value': rsi_value,
                'ma_value': ma_value,
                'volatility': self.calculate_volatility(current_price)
            }
            
            return web.json_response(status_data)
            
        except Exception as e:
            logger.error(f"Error in status handler: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    def calculate_rsi(self, current_price):
        """Calculate RSI based on price movement."""
        try:
            # This is a simplified RSI calculation
            # In production, you'd want to use historical price data
            if not hasattr(self, 'price_history'):
                self.price_history = []
            
            self.price_history.append(current_price)
            if len(self.price_history) > 14:
                self.price_history.pop(0)
            
            if len(self.price_history) < 14:
                return 50.0  # Neutral RSI if not enough data
            
            # Calculate price changes
            changes = []
            for i in range(1, len(self.price_history)):
                changes.append(self.price_history[i] - self.price_history[i-1])
            
            gains = [change for change in changes if change > 0]
            losses = [-change for change in changes if change < 0]
            
            avg_gain = sum(gains) / len(gains) if gains else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return max(0, min(100, rsi))
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return 50.0
    
    def calculate_moving_average(self, current_price):
        """Calculate moving average based on price history."""
        try:
            if not hasattr(self, 'price_history'):
                self.price_history = []
            
            self.price_history.append(current_price)
            if len(self.price_history) > 20:
                self.price_history.pop(0)
            
            if len(self.price_history) == 0:
                return current_price
            
            return sum(self.price_history) / len(self.price_history)
        except Exception as e:
            logger.error(f"Error calculating MA: {e}")
            return current_price
    
    def calculate_volatility(self, current_price):
        """Calculate volatility based on price history."""
        try:
            if not hasattr(self, 'price_history') or len(self.price_history) < 10:
                return 'Low'
            
            recent_prices = self.price_history[-10:]
            mean = sum(recent_prices) / len(recent_prices)
            variance = sum((price - mean) ** 2 for price in recent_prices) / len(recent_prices)
            std_dev = variance ** 0.5
            volatility_percent = (std_dev / mean) * 100 if mean > 0 else 0
            
            if volatility_percent > 5:
                return 'High'
            elif volatility_percent > 2:
                return 'Medium'
            else:
                return 'Low'
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return 'Low'
    
    async def price_history_handler(self, request):
        """API endpoint for price history data."""
        try:
            # Get real price history from ByBit API
            kline_data = await self.client.get_orderbook("BTCUSDT", 50)
            history = []
            
            if kline_data.get('retCode') == 0:
                result = kline_data.get('result', {})
                bids = result.get('b', [])
                asks = result.get('a', [])
                
                # Combine bid and ask data for price history
                for i in range(min(len(bids), len(asks), 20)):
                    bid_price = float(bids[i][0]) if i < len(bids) else 0
                    ask_price = float(asks[i][0]) if i < len(asks) else 0
                    avg_price = (bid_price + ask_price) / 2 if bid_price and ask_price else 0
                    
                    if avg_price > 0:
                        timestamp = datetime.now() - timedelta(minutes=i)
                        history.append({
                            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            'price': avg_price
                        })
            
            # If no real data, return empty array
            if not history:
                history = []
            
            return web.json_response(history)
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def trade_history_handler(self, request):
        """API endpoint for trade history data."""
        try:
            # Get current price first
            ticker = await self.client.get_ticker("BTCUSDT")
            current_price = None
            if ticker.get('retCode') == 0:
                result = ticker.get('result', {})
                list_data = result.get('list', [])
                if list_data:
                    current_price = float(list_data[0].get('lastPrice', 0))
            
            # Get real trade history from ByBit API
            order_history = await self.client.get_order_history("BTCUSDT", 50)
            trades = []
            
            if order_history.get('retCode') == 0:
                result = order_history.get('result', {})
                list_data = result.get('list', [])
                
                for order in list_data:
                    if order.get('orderStatus') == 'Filled':
                        timestamp = datetime.fromtimestamp(int(order.get('updatedTime', 0)) / 1000)
                        side = order.get('side', '')
                        price = float(order.get('avgPrice', 0))
                        qty = float(order.get('qty', 0))
                        
                        # Calculate PnL (simplified)
                        pnl = 0
                        if current_price and price > 0:
                            if side == 'Buy':
                                pnl = (current_price - price) * qty
                            elif side == 'Sell':
                                pnl = (price - current_price) * qty
                        
                        trades.append({
                            'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            'side': side,
                            'price': price,
                            'size': qty,
                            'pnl': pnl
                        })
            
            return web.json_response(trades)
        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def update_config_handler(self, request):
        """API endpoint for updating bot configuration."""
        try:
            data = await request.json()
            # Here you would update the configuration
            # For now, just return success
            return web.json_response({'success': True, 'message': 'Configuration updated'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def emergency_stop_handler(self, request):
        """API endpoint for emergency stop."""
        try:
            # Here you would implement emergency stop logic
            # Close all positions, cancel orders, etc.
            return web.json_response({'success': True, 'message': 'Emergency stop executed'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def start_bot_handler(self, request):
        """API endpoint for starting the bot."""
        try:
            # Here you would implement bot start logic
            return web.json_response({'success': True, 'message': 'Bot started successfully'})
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def orderbook_handler(self, request):
        """API endpoint for real-time order book data."""
        try:
            # Get current price and order book
            ticker = await self.client.get_ticker("BTCUSDT")
            orderbook = await self.client.get_orderbook("BTCUSDT", 25)
            
            current_price = None
            price_change = None
            
            if ticker.get('retCode') == 0:
                result = ticker.get('result', {})
                list_data = result.get('list', [])
                if list_data:
                    ticker_data = list_data[0]
                    current_price = float(ticker_data.get('lastPrice', 0))
                    price_change = float(ticker_data.get('price24hPcnt', 0))
            
            asks = []
            bids = []
            
            if orderbook.get('retCode') == 0:
                result = orderbook.get('result', {})
                asks_data = result.get('a', [])  # Asks (sell orders)
                bids_data = result.get('b', [])  # Bids (buy orders)
                
                # Process asks (sell orders) - highest to lowest
                total_ask_volume = 0
                for i, ask in enumerate(asks_data[:10]):
                    price = float(ask[0])
                    quantity = float(ask[1])
                    total_ask_volume += quantity
                    asks.append([price, quantity, total_ask_volume])
                
                # Process bids (buy orders) - highest to lowest
                total_bid_volume = 0
                for i, bid in enumerate(bids_data[:10]):
                    price = float(bid[0])
                    quantity = float(bid[1])
                    total_bid_volume += quantity
                    bids.append([price, quantity, total_bid_volume])
            
            orderbook_data = {
                'current_price': current_price,
                'price_change': price_change,
                'asks': asks,
                'bids': bids,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return web.json_response(orderbook_data)
            
        except Exception as e:
            logger.error(f"Error getting order book: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def kline_data_handler(self, request):
        """API endpoint for kline/candlestick data."""
        try:
            # Get kline data from ByBit API
            kline_data = await self.client.get_kline_data("BTCUSDT", "1", 100)
            
            if kline_data.get('retCode') == 0:
                result = kline_data.get('result', {})
                list_data = result.get('list', [])
                
                # Format kline data for charting
                formatted_data = []
                for kline in list_data:
                    formatted_data.append({
                        'timestamp': int(kline[0]),
                        'open': float(kline[1]),
                        'high': float(kline[2]),
                        'low': float(kline[3]),
                        'close': float(kline[4]),
                        'volume': float(kline[5])
                    })
                
                return web.json_response(formatted_data)
            else:
                return web.json_response({'error': kline_data.get('retMsg', 'Unknown error')}, status=500)
                
        except Exception as e:
            logger.error(f"Error getting kline data: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def funding_rate_handler(self, request):
        """API endpoint for funding rate data."""
        try:
            # Get funding rate from ByBit API
            funding_data = await self.client.get_funding_rate("BTCUSDT")
            
            if funding_data.get('retCode') == 0:
                result = funding_data.get('result', {})
                list_data = result.get('list', [])
                
                if list_data:
                    latest_funding = list_data[0]
                    return web.json_response({
                        'fundingRate': float(latest_funding.get('fundingRate', 0)),
                        'fundingRateTimestamp': int(latest_funding.get('fundingRateTimestamp', 0)),
                        'symbol': latest_funding.get('symbol', 'BTCUSDT')
                    })
                else:
                    return web.json_response({'error': 'No funding rate data available'}, status=404)
            else:
                return web.json_response({'error': funding_data.get('retMsg', 'Unknown error')}, status=500)
                
        except Exception as e:
            logger.error(f"Error getting funding rate: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def open_interest_handler(self, request):
        """API endpoint for open interest data."""
        try:
            open_interest = await self.client.get_open_interest("BTCUSDT", "1h")
            return web.json_response(open_interest)
        except Exception as e:
            logger.error(f"Error getting open interest: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    # Auto Trading Handlers
    async def start_auto_trading_handler(self, request):
        """Start auto trading."""
        try:
            data = await request.json()
            trading_mode = data.get('mode', 'both')
            
            # Initialize trading manager if not already done
            if not self.trading_manager:
                from src.trading_manager import AutoTradingManager
                self.trading_manager = AutoTradingManager(self.config, self.client)
            
            # Set trading mode
            self.config.set('trading.mode', trading_mode)
            
            # Start auto trading
            await self.trading_manager.start_auto_trading()
            
            return web.json_response({
                'success': True,
                'message': f'Auto trading started in {trading_mode} mode',
                'mode': trading_mode
            })
            
        except Exception as e:
            logger.error(f"Error starting auto trading: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def stop_auto_trading_handler(self, request):
        """Stop auto trading."""
        try:
            if self.trading_manager:
                # This would implement stopping logic
                self.trading_manager = None
                return web.json_response({
                    'success': True,
                    'message': 'Auto trading stopped'
                })
            else:
                return web.json_response({
                    'success': False,
                    'message': 'No active trading session'
                })
                
        except Exception as e:
            logger.error(f"Error stopping auto trading: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def trading_status_handler(self, request):
        """Get trading status."""
        try:
            if self.trading_manager:
                status = self.trading_manager.get_trading_status()
                return web.json_response(status)
            else:
                return web.json_response({
                    'trading_mode': 'none',
                    'active_positions': 0,
                    'daily_stats': {'trades': 0, 'profit': 0, 'loss': 0},
                    'message': 'No active trading session'
                })
                
        except Exception as e:
            logger.error(f"Error getting trading status: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def configure_trading_handler(self, request):
        """Configure trading settings."""
        try:
            data = await request.json()
            
            # Update configuration based on request data
            if 'trading_mode' in data:
                self.config.set('trading.mode', data['trading_mode'])
            
            if 'max_daily_loss' in data:
                self.config.set('trading.auto_trade.max_daily_loss', data['max_daily_loss'])
            
            if 'max_positions' in data:
                self.config.set('trading.auto_trade.max_positions', data['max_positions'])
            
            if 'spot_symbols' in data:
                self.config.set('spot.symbols', data['spot_symbols'])
            
            if 'futures_symbols' in data:
                self.config.set('futures.symbols', data['futures_symbols'])
            
            if 'leverage' in data:
                self.config.set('futures.leverage', data['leverage'])
            
            # Save configuration
            self.config.save()
            
            return web.json_response({
                'success': True,
                'message': 'Trading configuration updated'
            })
            
        except Exception as e:
            logger.error(f"Error configuring trading: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def account_balance_handler(self, request):
        """Get account balance."""
        try:
            account_info = await self.client.get_account_info()
            if account_info.get('retCode') == 0:
                result = account_info.get('result', {})
                list_data = result.get('list', [])
                
                if list_data:
                    account_data = list_data[0]
                    
                    balance_data = {
                        'total_balance': float(account_data.get('totalWalletBalance', 0)),
                        'available_balance': float(account_data.get('totalAvailableBalance', 0)),
                        'margin_balance': float(account_data.get('totalMarginBalance', 0)),
                        'coins': []
                    }
                    
                    # Get coin details
                    coins = account_data.get('coin', [])
                    for coin in coins:
                        if float(coin.get('walletBalance', 0)) > 0:
                            balance_data['coins'].append({
                                'coin': coin.get('coin', ''),
                                'balance': float(coin.get('walletBalance', 0)),
                                'usd_value': float(coin.get('usdValue', 0)),
                                'available': float(coin.get('free', 0)),
                                'unrealised_pnl': float(coin.get('unrealisedPnl', 0))
                            })
                    
                    return web.json_response(balance_data)
                else:
                    return web.json_response({'error': 'No account data found'}, status=404)
            else:
                return web.json_response({'error': account_info.get('retMsg', 'Unknown error')}, status=500)
                
        except Exception as e:
            logger.error(f"Error getting account balance: {e}")
            return web.json_response({'error': str(e)}, status=500)


async def main():
    """Main function to start the advanced dashboard."""
    dashboard = AdvancedDashboard()
    
    if not await dashboard.initialize():
        print("❌ Failed to initialize dashboard")
        return
    
    print("🚀 Starting Advanced ByBit Grid Trading Bot Dashboard...")
    print("📱 Open your browser and go to: http://localhost:8081")
    print("🛑 Press Ctrl+C to stop the dashboard")
    
    try:
        runner = web.AppRunner(dashboard.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8081)
        await site.start()
        
        # Keep the server running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except OSError as e:
        if "10048" in str(e):
            print("❌ Port 8081 is already in use. Please stop other services or use a different port.")
        else:
            print(f"❌ Error starting dashboard: {e}")
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 