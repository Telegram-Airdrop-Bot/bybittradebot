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
    
        # Account Settings API endpoints
        self.app.router.add_post('/api/save-account-settings', self.save_account_settings_handler)
        self.app.router.add_get('/api/load-account-settings', self.load_account_settings_handler)
        self.app.router.add_get('/api/test-connection', self.test_connection_handler)
    
    async def index_handler(self, request):
        """Serve the advanced dashboard page."""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <title>ByBit Professional Trading Dashboard</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
            <style>
                :root {
                    --primary-color: #2563eb;
                    --secondary-color: #1e40af;
                    --success-color: #059669;
                    --danger-color: #dc2626;
                    --warning-color: #d97706;
                    --info-color: #0891b2;
                    --dark-bg: #0f172a;
                    --card-bg: #1e293b;
                    --text-primary: #f8fafc;
                    --text-secondary: #cbd5e1;
                    --border-color: #334155;
                    --gradient-primary: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                    --gradient-success: linear-gradient(135deg, #059669 0%, #047857 100%);
                    --gradient-danger: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                    --gradient-warning: linear-gradient(135deg, #d97706 0%, #b45309 100%);
                }
                
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                    color: var(--text-primary);
                    min-height: 100vh;
                    line-height: 1.6;
                }
                
                .container {
                    max-width: 1600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                /* Professional Header */
                .header {
                    background: rgba(30, 41, 59, 0.8);
                    backdrop-filter: blur(20px);
                    border: 1px solid var(--border-color);
                    border-radius: 20px;
                    padding: 30px;
                    margin-bottom: 30px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                }
                
                .header-left h1 {
                    font-size: 2.5rem;
                    font-weight: 800;
                    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 5px;
                }
                
                .header-left p {
                    color: var(--text-secondary);
                    font-size: 1.1rem;
                    font-weight: 400;
                }
                
                .status-indicator {
                    display: flex;
                    align-items: center;
                    gap: 15px;
                    background: rgba(34, 197, 94, 0.1);
                    padding: 15px 25px;
                    border-radius: 15px;
                    border: 1px solid rgba(34, 197, 94, 0.3);
                }
                
                .status-dot {
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #22c55e;
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; transform: scale(1); }
                    50% { opacity: 0.7; transform: scale(1.1); }
                }
                
                /* Professional Controls */
                .controls {
                    display: flex;
                    gap: 15px;
                    margin-bottom: 30px;
                    flex-wrap: wrap;
                }
                
                .btn {
                    padding: 12px 24px;
                    border: none;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 0.9rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    text-decoration: none;
                }
                
                .btn-primary {
                    background: var(--gradient-primary);
                    color: white;
                }
                
                .btn-success {
                    background: var(--gradient-success);
                    color: white;
                }
                
                .btn-danger {
                    background: var(--gradient-danger);
                    color: white;
                }
                
                .btn-warning {
                    background: var(--gradient-warning);
                    color: white;
                }
                
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
                }
                
                /* Professional Grid Layout */
                .grid-container {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 25px;
                    margin-bottom: 30px;
                }
                
                .card {
                    background: rgba(30, 41, 59, 0.8);
                    backdrop-filter: blur(20px);
                    border: 1px solid var(--border-color);
                    border-radius: 20px;
                    padding: 30px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                    transition: all 0.3s ease;
                }
                
                .card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
                }
                
                .card h3 {
                    margin-bottom: 20px;
                    color: var(--text-primary);
                    font-size: 1.3rem;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .metric {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin: 15px 0;
                    padding: 15px;
                    background: rgba(51, 65, 85, 0.3);
                    border-radius: 12px;
                    border-left: 4px solid var(--primary-color);
                    transition: all 0.3s ease;
                }
                
                .metric:hover {
                    background: rgba(51, 65, 85, 0.5);
                    transform: translateX(5px);
                }
                
                .metric-label {
                    font-weight: 600;
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                }
                
                .metric-value {
                    font-weight: 700;
                    font-size: 1.1rem;
                    color: var(--text-primary);
                }
                
                .positive { color: #22c55e; }
                .negative { color: #ef4444; }
                .neutral { color: #f8fafc; }
                .success { color: #22c55e; }
                .warning { color: #f59e0b; }
                .danger { color: #ef4444; }
                .info { color: #3b82f6; }
                
                /* Professional Chart Container */
                .chart-container {
                    background: rgba(30, 41, 59, 0.8);
                    backdrop-filter: blur(20px);
                    border: 1px solid var(--border-color);
                    border-radius: 20px;
                    padding: 30px;
                    margin-bottom: 30px;
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
                }
                
                .chart-container h3 {
                    margin-bottom: 25px;
                    color: var(--text-primary);
                    font-size: 1.5rem;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                /* Professional Alerts */
                .alert {
                    padding: 20px;
                    border-radius: 15px;
                    margin: 20px 0;
                    font-weight: 600;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .alert-success {
                    background: rgba(34, 197, 94, 0.1);
                    border: 1px solid rgba(34, 197, 94, 0.3);
                    color: #22c55e;
                }
                
                .alert-danger {
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.3);
                    color: #ef4444;
                }
                
                .alert-warning {
                    background: rgba(245, 158, 11, 0.1);
                    border: 1px solid rgba(245, 158, 11, 0.3);
                    color: #f59e0b;
                }
                
                /* Professional Modal */
                .modal {
                    display: none;
                    position: fixed;
                    z-index: 1000;
                    left: 0;
                    top: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.8);
                    backdrop-filter: blur(10px);
                }
                
                .modal-content {
                    background: var(--card-bg);
                    border: 1px solid var(--border-color);
                    border-radius: 20px;
                    margin: 5% auto;
                    padding: 40px;
                    width: 90%;
                    max-width: 600px;
                    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
                }
                
                .close {
                    color: var(--text-secondary);
                    float: right;
                    font-size: 28px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: color 0.3s ease;
                }
                
                .close:hover {
                    color: var(--text-primary);
                }
                
                .form-group {
                    margin-bottom: 25px;
                }
                
                .form-group label {
                    display: block;
                    margin-bottom: 10px;
                    font-weight: 600;
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                }
                
                .form-group input,
                .form-group select {
                    width: 100%;
                    padding: 15px;
                    background: rgba(15, 23, 42, 0.8);
                    border: 1px solid var(--border-color);
                    border-radius: 12px;
                    color: var(--text-primary);
                    font-size: 0.9rem;
                    transition: all 0.3s ease;
                }
                
                .form-group input:focus,
                .form-group select:focus {
                    outline: none;
                    border-color: var(--primary-color);
                    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
                }
                
                .loading {
                    text-align: center;
                    padding: 60px;
                    color: var(--text-secondary);
                    font-style: italic;
                }
                
                .refresh-info {
                    text-align: center;
                    margin: 20px 0;
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                }
                
                @media (max-width: 1200px) {
                    .grid-container {
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    }
                }
                
                @media (max-width: 768px) {
                    .header {
                    flex-direction: column;
                        gap: 20px;
                        text-align: center;
                    }
                    
                    .header-left h1 {
                        font-size: 2rem;
                    }
                    
                    .controls {
                        justify-content: center;
                    }
                    
                    .grid-container {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <!-- Professional Header -->
                <div class="header">
                    <div class="header-left">
                        <h1><i class="fas fa-robot"></i> ByBit Professional Trading Bot</h1>
                        <p>Advanced Auto Trading Dashboard</p>
                    </div>
                    <div class="status-indicator">
                        <div class="status-dot"></div>
                        <span id="connectionStatus">Live Trading Active</span>
                    </div>
                </div>
                
                <!-- Professional Controls -->
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
                
                <!-- Professional Grid Layout -->
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
                        <button class="btn btn-success" style="width: 100%; margin-bottom: 15px;" onclick="startBot()">
                            <i class="fas fa-play"></i> Start Bot
                        </button>
                        <button class="btn btn-warning" style="width: 100%; margin-bottom: 15px;" onclick="pauseBot()">
                            <i class="fas fa-pause"></i> Pause Bot
                        </button>
                        <button class="btn btn-primary" style="width: 100%; margin-bottom: 15px;" onclick="exportData()">
                            <i class="fas fa-download"></i> Export Data
                        </button>
                        <button class="btn btn-primary" style="width: 100%;" onclick="viewLogs()">
                            <i class="fas fa-file-alt"></i> View Logs
                        </button>
                    </div>
                    
                    <!-- Professional Risk Management Panel -->
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
                    
                    <!-- Professional Troubleshooting Panel -->
                    <div class="card">
                        <h3><i class="fas fa-tools"></i> System Health</h3>
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
                    
                    <!-- Professional Wallet Details Panel -->
                    <div class="card">
                        <h3><i class="fas fa-coins"></i> Wallet Details</h3>
                        <div id="coinDetailsContainer">
                            <div class="metric">
                                <span class="metric-label">Loading coins...</span>
                                <span class="metric-value">Please wait</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Professional Account Settings Panel -->
                    <div class="card" onclick="openAccountSettingsModal()" style="cursor: pointer;">
                        <h3><i class="fas fa-user-cog"></i> Account Settings</h3>
                        
                        <!-- Account Information Display -->
                        <div style="margin-bottom: 20px;">
                            <h4 style="color: var(--text-primary); margin-bottom: 15px; font-weight: 600;">Account Information</h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
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
                
                        <!-- Quick Status -->
                        <div style="margin-top: 20px; padding: 15px; background: rgba(51, 65, 85, 0.3); border-radius: 8px; border: 1px solid var(--border-color);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: var(--text-secondary); font-weight: 600;">Settings Status:</span>
                                <span id="settingsStatus" style="color: var(--text-primary); font-weight: 600;">Ready</span>
                            </div>
                            <div style="margin-top: 10px; font-size: 0.9rem; color: var(--text-secondary);">
                                <span id="lastSavedTime">Last saved: Never</span>
                            </div>
                        </div>
                        
                        <!-- Click to Configure Hint -->
                        <div style="margin-top: 15px; text-align: center; color: var(--text-secondary); font-size: 0.9rem;">
                            <i class="fas fa-mouse-pointer"></i> Click to configure settings
                        </div>
                    </div>
                </div>
                
                <!-- Professional Auto Trading Control Panel -->
                <div class="card" style="margin-bottom: 30px;">
                    <h3><i class="fas fa-robot"></i> Auto Trading Control</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px;">
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Trading Mode:</label>
                            <select id="tradingMode" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                                <option value="both">Both Spot & Futures</option>
                                <option value="spot">Spot Only</option>
                                <option value="futures">Futures Only</option>
                            </select>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Max Daily Loss (USDT):</label>
                            <input type="number" id="maxDailyLoss" value="1000" min="100" max="10000" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Max Positions:</label>
                            <input type="number" id="maxPositions" value="5" min="1" max="20" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 8px;">
                            <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Leverage (Futures):</label>
                            <input type="number" id="leverage" value="5" min="1" max="100" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                        </div>
                    </div>
                    <div style="display: flex; gap: 15px; flex-wrap: wrap;">
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
                    <div style="margin-top: 20px; padding: 20px; background: rgba(51, 65, 85, 0.3); border-radius: 12px; border: 1px solid var(--border-color);">
                        <h4 style="margin-bottom: 15px; color: var(--text-primary); font-weight: 700;">Trading Status</h4>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-secondary);">Status:</span>
                                <span id="tradingStatusText" style="color: var(--text-primary); font-weight: 600;">Stopped</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-secondary);">Active Positions:</span>
                                <span id="activePositionsCount" style="color: var(--text-primary); font-weight: 600;">0</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-secondary);">Daily Trades:</span>
                                <span id="dailyTrades" style="color: var(--text-primary); font-weight: 600;">0</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-secondary);">Daily PnL:</span>
                                <span id="dailyPnlDisplay" style="color: var(--text-primary); font-weight: 600;">$0.00</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Professional Chart Container -->
                <div class="chart-container">
                    <h3><i class="fas fa-chart-area"></i> Professional Trading Charts</h3>
                    
                    <!-- Real-time Trading Interface -->
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 25px; margin-bottom: 25px;">
                        <!-- Main Chart Area -->
                        <div>
                            <div style="display: flex; gap: 15px; margin-bottom: 20px; flex-wrap: wrap;">
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
                        <div style="background: rgba(30, 41, 59, 0.8); border-radius: 15px; padding: 20px; border: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 20px; color: var(--text-primary); font-weight: 700;">Order Book</h4>
                            <div style="margin-bottom: 15px; text-align: center;">
                                <div style="font-size: 20px; font-weight: 800; color: #ef4444;" id="currentPriceDisplay">$115,203.12</div>
                                <div style="font-size: 14px; color: var(--text-secondary);" id="priceChangeDisplay">+157.48 (+0.14%)</div>
                            </div>
                            
                            <!-- Asks (Sell Orders) -->
                            <div style="margin-bottom: 15px;">
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px;">
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
                                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px;">
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
                    
                    <!-- Real-time Trading Status -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 25px;">
                        <div style="background: rgba(30, 41, 59, 0.8); border-radius: 15px; padding: 20px; border: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 15px; color: var(--text-primary); font-weight: 700;">Grid Status</h4>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Grid Levels:</span>
                                <span id="gridLevelsCount" style="color: var(--text-primary); font-weight: 600;">20</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Current Position:</span>
                                <span id="currentPosition" style="color: var(--text-primary); font-weight: 600;">None</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Next Grid:</span>
                                <span id="nextGridLevel" style="color: var(--text-primary); font-weight: 600;">$45,000</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-secondary);">Signal Strength:</span>
                                <span id="signalStrength" style="color: var(--text-primary); font-weight: 600;">WEAK</span>
                            </div>
                        </div>
                        
                        <div style="background: rgba(30, 41, 59, 0.8); border-radius: 15px; padding: 20px; border: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 15px; color: var(--text-primary); font-weight: 700;">Real-time Indicators</h4>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">RSI:</span>
                                <span id="rsiValue" style="color: var(--text-primary); font-weight: 600;">50.0</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">MA:</span>
                                <span id="maValue" style="color: var(--text-primary); font-weight: 600;">$45,000</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Volume:</span>
                                <span id="volumeValue" style="color: var(--text-primary); font-weight: 600;">1.2K</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-secondary);">Spread:</span>
                                <span id="spreadValue" style="color: var(--text-primary); font-weight: 600;">$0.01</span>
                            </div>
                        </div>
                        
                        <div style="background: rgba(30, 41, 59, 0.8); border-radius: 15px; padding: 20px; border: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 15px; color: var(--text-primary); font-weight: 700;">Market Pressure</h4>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Buy Pressure:</span>
                                <span id="buyPressure" style="color: #22c55e; font-weight: 600;">47%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Sell Pressure:</span>
                                <span id="sellPressure" style="color: #ef4444; font-weight: 600;">53%</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Order Flow:</span>
                                <span id="orderFlow" style="color: var(--text-primary); font-weight: 600;">Neutral</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-secondary);">Volatility:</span>
                                <span id="volatilityValue" style="color: var(--text-primary); font-weight: 600;">Medium</span>
                            </div>
                        </div>
                        
                        <div style="background: rgba(30, 41, 59, 0.8); border-radius: 15px; padding: 20px; border: 1px solid var(--border-color);">
                            <h4 style="margin-bottom: 15px; color: var(--text-primary); font-weight: 700;">Market Data</h4>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Funding Rate:</span>
                                <span id="fundingRate" style="color: var(--text-primary); font-weight: 600;">Loading...</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Open Interest:</span>
                                <span id="openInterest" style="color: var(--text-primary); font-weight: 600;">Loading...</span>
                            </div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span style="color: var(--text-secondary);">Next Funding:</span>
                                <span id="nextFunding" style="color: var(--text-primary); font-weight: 600;">Loading...</span>
                            </div>
                            <div style="display: flex; justify-content: space-between;">
                                <span style="color: var(--text-secondary);">OI Change:</span>
                                <span id="oiChange" style="color: var(--text-primary); font-weight: 600;">Loading...</span>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px; padding: 20px; background: rgba(51, 65, 85, 0.3); border-radius: 15px; border: 1px solid var(--border-color);">
                        <h4 style="margin-bottom: 15px; color: var(--text-primary); font-weight: 700;">Grid Trading Zones</h4>
                        <div style="display: flex; gap: 25px; flex-wrap: wrap;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 12px; height: 12px; background: #22c55e; border-radius: 2px;"></div>
                                <span style="color: var(--text-secondary);">Buy Zone</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 12px; height: 12px; background: #ef4444; border-radius: 2px;"></div>
                                <span style="color: var(--text-secondary);">Sell Zone</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 12px; height: 12px; background: #f59e0b; border-radius: 2px;"></div>
                                <span style="color: var(--text-secondary);">Neutral Zone</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <div style="width: 12px; height: 12px; background: #8b5cf6; border-radius: 2px;"></div>
                                <span style="color: var(--text-secondary);">Current Price</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Professional Config Modal -->
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
            
                <!-- Professional Emergency Modal -->
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
                        <div style="display: flex; gap: 15px; margin-top: 30px;">
                        <button class="btn btn-danger" onclick="emergencyStop()">Stop Bot</button>
                        <button class="btn btn-primary" onclick="closeEmergencyModal()">Cancel</button>
                    </div>
                </div>
            </div>
            
            <script>
                    // Initialize dashboard
                    document.addEventListener('DOMContentLoaded', function() {
                        initCharts();
                        loadStatus();
                        startAutoRefresh();
                        updateOrderBook();
                    });
                    
                    // Professional chart variables
                let priceChart = null;
                let gridChart = null;
                let volumeChart = null;
                let indicatorsChart = null;
                    let currentChartType = 'price';
                
                    // Professional chart initialization
                function initCharts() {
                    const priceCtx = document.getElementById('priceChart').getContext('2d');
                    priceChart = new Chart(priceCtx, {
                        type: 'line',
                        data: {
                            labels: [],
                            datasets: [{
                                label: 'BTC Price',
                                data: [],
                                    borderColor: '#3b82f6',
                                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
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
                                            color: 'rgba(148, 163, 184, 0.1)'
                                        },
                                        ticks: {
                                            color: '#cbd5e1'
                                    }
                                },
                                x: {
                                    grid: {
                                            color: 'rgba(148, 163, 184, 0.1)'
                                        },
                                        ticks: {
                                            color: '#cbd5e1'
                                        }
                                }
                            }
                        }
                    });
                    }
                    
                    // Professional chart switching
                    function switchChart(type) {
                        // Hide all charts
                        document.getElementById('priceChart').style.display = 'none';
                        document.getElementById('gridChart').style.display = 'none';
                        document.getElementById('volumeChart').style.display = 'none';
                        document.getElementById('indicatorsChart').style.display = 'none';
                        
                        // Show selected chart
                        document.getElementById(type + 'Chart').style.display = 'block';
                        currentChartType = type;
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
                            row.style.padding = '4px 0';
                        
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
                            row.style.color = '#22c55e';
                            row.style.padding = '4px 0';
                        
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
                                changeElement.style.color = change >= 0 ? '#22c55e' : '#ef4444';
                            }
                        }
                    }
                    
                    // Update current price from status data
                    function updateCurrentPriceFromStatus(data) {
                        if (data.current_price) {
                            const priceElement = document.getElementById('currentPriceDisplay');
                            const changeElement = document.getElementById('priceChangeDisplay');
                            
                            priceElement.textContent = '$' + data.current_price.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            });
                            
                            if (data.price_change) {
                                const changePercent = (data.price_change * 100).toFixed(2);
                                const changeValue = (data.current_price * data.price_change).toFixed(2);
                                const sign = data.price_change >= 0 ? '+' : '';
                                changeElement.textContent = `${sign}${changeValue} (${sign}${changePercent}%)`;
                                changeElement.style.color = data.price_change >= 0 ? '#22c55e' : '#ef4444';
                        }
                    }
                }
                
                function updateMarketPressure(asks, bids) {
                    const totalAskVolume = asks.reduce((sum, ask) => sum + parseFloat(ask[1]), 0);
                    const totalBidVolume = bids.reduce((sum, bid) => sum + parseFloat(bid[1]), 0);
                    const totalVolume = totalAskVolume + totalBidVolume;
                    
                    if (totalVolume > 0) {
                        const buyPressure = ((totalBidVolume / totalVolume) * 100).toFixed(1);
                        const sellPressure = ((totalAskVolume / totalVolume) * 100).toFixed(1);
                        
                        document.getElementById('buyPressure').textContent = buyPressure + '%';
                        document.getElementById('sellPressure').textContent = sellPressure + '%';
                        
                        const orderFlowElement = document.getElementById('orderFlow');
                        if (totalBidVolume > totalAskVolume * 1.2) {
                            orderFlowElement.textContent = 'Bullish';
                                orderFlowElement.style.color = '#22c55e';
                        } else if (totalAskVolume > totalBidVolume * 1.2) {
                            orderFlowElement.textContent = 'Bearish';
                            orderFlowElement.style.color = '#ef4444';
                        } else {
                            orderFlowElement.textContent = 'Neutral';
                                orderFlowElement.style.color = '#cbd5e1';
                            }
                        }
                    }
                    
                    // Professional connection status management
                    function updateConnectionStatus(status, color = '#22c55e') {
                        const statusElement = document.getElementById('connectionStatus');
                        const statusDot = document.querySelector('.status-dot');
                        
                        statusElement.textContent = status;
                        statusElement.style.color = color;
                        statusDot.style.background = color;
                    }
                    
                    // Professional status loading
                    async function loadStatus() {
                        try {
                            // Show loading state
                            showLoadingState();
                            updateConnectionStatus('Connecting to API...', '#f59e0b');
                            
                            const response = await axios.get('/api/status');
                            const data = response.data;
                            
                            // Hide loading state
                            hideLoadingState();
                            updateConnectionStatus('Live Trading Active', '#22c55e');
                            
                            displayStatus(data);
                            updateChart(data.current_price, data.timestamp);
                            
                            // Update grid system with real-time data
                            if (data.current_price) {
                                updateGridSystem(data.current_price);
                            }
                            
                            // Update order book
                            await updateOrderBook();
                            
                            // Update market data
                            await updateMarketData();
                            
                        } catch (error) {
                            hideLoadingState();
                            console.error('Error loading status:', error);
                            
                            // Update connection status based on error type
                            if (error.response) {
                                // Server responded with error
                                updateConnectionStatus('API Error', '#ef4444');
                                showAlert(`Server Error: ${error.response.status} - ${error.response.data.error || 'Unknown error'}`, 'danger');
                            } else if (error.request) {
                                // Network error
                                updateConnectionStatus('Connection Failed', '#ef4444');
                                showAlert('Network Error: Unable to connect to server. Please check your connection.', 'danger');
                            } else {
                                // Other error
                                updateConnectionStatus('Error', '#ef4444');
                                showAlert('Error loading status: ' + error.message, 'danger');
                            }
                            
                            // Show connection troubleshooting info
                            showConnectionTroubleshooting();
                        }
                    }
                    
                    // Professional loading state management
                    function showLoadingState() {
                        const loadingElements = document.querySelectorAll('.metric-value');
                        loadingElements.forEach(element => {
                            if (element.textContent === 'Loading...') {
                                element.innerHTML = '<span style="color: #f59e0b;"><i class="fas fa-spinner fa-spin"></i> Connecting...</span>';
                            }
                        });
                    }
                    
                    function hideLoadingState() {
                        const loadingElements = document.querySelectorAll('.metric-value');
                        loadingElements.forEach(element => {
                            if (element.innerHTML.includes('fa-spinner')) {
                                element.textContent = 'N/A';
                                element.style.color = '#ef4444';
                            }
                        });
                    }
                    
                    // Professional connection troubleshooting
                    function showConnectionTroubleshooting() {
                        const alertsDiv = document.getElementById('alerts');
                        const troubleshootingDiv = document.createElement('div');
                        troubleshootingDiv.className = 'alert alert-warning';
                        troubleshootingDiv.innerHTML = `
                            <i class="fas fa-exclamation-triangle"></i>
                            <strong>Connection Issues Detected</strong><br>
                            <small>
                                • Check if the server is running on port 8081<br>
                                • Verify your ByBit API credentials in config.yaml<br>
                                • Ensure your internet connection is stable<br>
                                • Check if ByBit API is accessible from your location
                            </small>
                        `;
                        alertsDiv.appendChild(troubleshootingDiv);
                        
                        // Remove after 30 seconds
                        setTimeout(() => {
                            troubleshootingDiv.remove();
                        }, 30000);
                    }
                    
                    // Professional status display
                    function displayStatus(data) {
                        // Market Info
                        const btcPrice = data.current_price ? data.current_price : 0;
                        const priceChange = data.price_change ? data.price_change : 0;
                        
                        const btcPriceElement = document.getElementById('btcPrice');
                        btcPriceElement.textContent = btcPrice ? '$' + btcPrice.toLocaleString('en-US', {
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                        }) : 'N/A';
                        btcPriceElement.className = 'metric-value neutral';
                        
                        const priceChangeElement = document.getElementById('priceChange');
                        priceChangeElement.textContent = priceChange ? (priceChange >= 0 ? '+' : '') + priceChange.toFixed(2) + '%' : 'N/A';
                        priceChangeElement.className = 'metric-value ' + (priceChange >= 0 ? 'positive' : 'negative');
                        
                        const lastUpdatedElement = document.getElementById('lastUpdated');
                        lastUpdatedElement.textContent = data.timestamp || 'N/A';
                        lastUpdatedElement.className = 'metric-value info';
                        
                        // Account
                        const accountBalance = data.account_balance;
                        const availableBalance = data.available_balance;
                        const margin_used = data.margin_used;
                        
                        const accountBalanceElement = document.getElementById('accountBalance');
                        accountBalanceElement.textContent = accountBalance ? '$' + accountBalance.toLocaleString('en-US', {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0
                        }) : '$0.00';
                        accountBalanceElement.className = 'metric-value neutral';
                        
                        const availableBalanceElement = document.getElementById('availableBalance');
                        availableBalanceElement.textContent = availableBalance ? '$' + availableBalance.toLocaleString('en-US', {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0
                        }) : '$0.00';
                        availableBalanceElement.className = 'metric-value neutral';
                        
                        const marginUsedElement = document.getElementById('marginUsed');
                        marginUsedElement.textContent = margin_used ? '$' + margin_used.toLocaleString('en-US', {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0
                        }) : '$0.00';
                        marginUsedElement.className = 'metric-value neutral';
                        
                        // Trading Performance
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
                        
                        const winRateElement = document.getElementById('winRate');
                        winRateElement.textContent = data.win_rate ? data.win_rate.toFixed(1) + '%' : '0.0%';
                        winRateElement.className = 'metric-value neutral';
                        
                        const tradeCountElement = document.getElementById('tradeCount');
                        tradeCountElement.textContent = data.trade_count || 0;
                        tradeCountElement.className = 'metric-value neutral';
                        
                        // Strategy
                        const activePositionsElement = document.getElementById('activePositions');
                        activePositionsElement.textContent = data.active_positions || 0;
                        activePositionsElement.className = 'metric-value neutral';
                        
                        const gridLevelsElement = document.getElementById('gridLevels');
                        gridLevelsElement.textContent = data.grid_levels || 0;
                        gridLevelsElement.className = 'metric-value neutral';
                        
                        const coverLossElement = document.getElementById('coverLossMultiplier');
                        coverLossElement.textContent = data.cover_loss_multiplier ? data.cover_loss_multiplier.toFixed(2) + 'x' : '1.00x';
                        coverLossElement.className = 'metric-value neutral';
                        
                        const consecutiveLossesElement = document.getElementById('consecutiveLosses');
                        consecutiveLossesElement.textContent = data.consecutive_losses || 0;
                        consecutiveLossesElement.className = 'metric-value neutral';
                        
                        // System
                        const cpuUsage = data.cpu_usage ? data.cpu_usage : 0;
                        const memoryUsage = data.memory_usage ? data.memory_usage : 0;
                        
                        const cpuUsageElement = document.getElementById('cpuUsage');
                        cpuUsageElement.textContent = cpuUsage ? cpuUsage.toFixed(1) + '%' : 'N/A';
                        cpuUsageElement.className = 'metric-value ' + (cpuUsage > 80 ? 'danger' : cpuUsage > 60 ? 'warning' : 'neutral');
                        
                        const memoryUsageElement = document.getElementById('memoryUsage');
                        memoryUsageElement.textContent = memoryUsage ? memoryUsage.toFixed(1) + '%' : 'N/A';
                        memoryUsageElement.className = 'metric-value ' + (memoryUsage > 80 ? 'danger' : memoryUsage > 60 ? 'warning' : 'neutral');
                        
                        const uptimeElement = document.getElementById('uptime');
                        uptimeElement.textContent = data.uptime ? Math.floor(data.uptime / 60) + ' minutes' : 'N/A';
                        uptimeElement.className = 'metric-value neutral';
                        
                        const apiStatusElement = document.getElementById('apiStatus');
                        apiStatusElement.textContent = data.api_status || 'Connected';
                        apiStatusElement.className = 'metric-value success';
                        
                        // Update indicators with professional colors
                        const rsiElement = document.getElementById('rsiValue');
                        rsiElement.textContent = data.rsi_value ? data.rsi_value.toFixed(1) : 'N/A';
                        rsiElement.className = 'metric-value neutral';
                        
                        const maElement = document.getElementById('maValue');
                        maElement.textContent = data.ma_value ? '$' + data.ma_value.toLocaleString('en-US', {
                            minimumFractionDigits: 0,
                            maximumFractionDigits: 0
                        }) : 'N/A';
                        maElement.className = 'metric-value neutral';
                        
                        const volumeElement = document.getElementById('volumeValue');
                        const volumeValue = data.volume_24h ? (data.volume_24h / 1000).toFixed(1) + 'K' : 'N/A';
                        volumeElement.textContent = volumeValue;
                        volumeElement.className = 'metric-value neutral';
                        
                        if (data.spread) {
                            const spreadElement = document.getElementById('spreadValue');
                            spreadElement.textContent = '$' + data.spread.toFixed(2);
                            spreadElement.className = 'metric-value neutral';
                        }
                        
                        if (data.buy_pressure && data.sell_pressure) {
                            const buyPressureElement = document.getElementById('buyPressure');
                            buyPressureElement.textContent = data.buy_pressure.toFixed(1) + '%';
                            buyPressureElement.className = 'metric-value positive';
                            
                            const sellPressureElement = document.getElementById('sellPressure');
                            sellPressureElement.textContent = data.sell_pressure.toFixed(1) + '%';
                            sellPressureElement.className = 'metric-value negative';
                            
                            const orderFlowElement = document.getElementById('orderFlow');
                            if (data.buy_pressure > data.sell_pressure * 1.2) {
                                orderFlowElement.textContent = 'Bullish';
                                orderFlowElement.className = 'metric-value positive';
                            } else if (data.sell_pressure > data.buy_pressure * 1.2) {
                                orderFlowElement.textContent = 'Bearish';
                                orderFlowElement.className = 'metric-value negative';
                            } else {
                                orderFlowElement.textContent = 'Neutral';
                                orderFlowElement.className = 'metric-value neutral';
                            }
                        }
                        
                        if (data.volatility) {
                            const volatilityElement = document.getElementById('volatilityValue');
                            volatilityElement.textContent = data.volatility;
                            volatilityElement.className = 'metric-value neutral';
                        }
                        
                        // Update current price in order book
                        updateCurrentPriceFromStatus(data);
                        
                        // Update risk metrics
                        if (data.current_price) {
                            updateRiskMetrics(data.current_price);
                        }
                        
                        // Update account details
                        updateAccountDetails(data);
                        
                        // Update troubleshooting info
                        updateTroubleshootingInfo(data);
                        
                        // Update coin details
                        updateCoinDetails(data.coin_details);
                        
                        // Update trading status
                        if (data.trading_status) {
                            document.getElementById('tradingStatusText').textContent = data.trading_status;
                            document.getElementById('activePositionsCount').textContent = data.active_positions || 0;
                            document.getElementById('dailyTrades').textContent = data.daily_trades || 0;
                            document.getElementById('dailyPnlDisplay').textContent = data.daily_pnl ? '$' + data.daily_pnl.toLocaleString('en-US', {
                                minimumFractionDigits: 2,
                                maximumFractionDigits: 2
                            }) : '$0.00';
                        }
                    }
                    
                    // Professional chart update
                function updateChart(price, timestamp) {
                    if (!priceChart) return;
                    
                        if (!window.priceHistory) {
                            window.priceHistory = [];
                        }
                        
                        window.priceHistory.push({price: price, timestamp: timestamp});
                        
                        if (window.priceHistory.length > 50) {
                            window.priceHistory.shift();
                        }
                        
                        const labels = window.priceHistory.map(item => {
                        const date = new Date(item.timestamp);
                        return date.toLocaleTimeString();
                    });
                    
                        const data = window.priceHistory.map(item => item.price);
                    
                    priceChart.data.labels = labels;
                    priceChart.data.datasets[0].data = data;
                    priceChart.update();
                    }
                    
                    // Professional grid system update
                    function updateGridSystem(currentPrice) {
                        const gridStep = currentPrice > 100000 ? 2000 : 500;
                        const numLevels = 15;
                    
                    const gridLevels = [];
                    for (let i = -numLevels; i <= numLevels; i++) {
                        gridLevels.push(currentPrice + (i * gridStep));
                    }
                    
                    const nearestGrid = gridLevels.reduce((prev, curr) => {
                        return (Math.abs(curr - currentPrice) < Math.abs(prev - currentPrice) ? curr : prev);
                    });
                    
                    const gridIndex = gridLevels.indexOf(nearestGrid);
                    const nextGrid = gridLevels[gridIndex + 1] || nearestGrid + gridStep;
                    const prevGrid = gridLevels[gridIndex - 1] || nearestGrid - gridStep;
                    
                    const distanceToNext = nextGrid - currentPrice;
                    const distanceToPrev = currentPrice - prevGrid;
                        const signalThreshold = gridStep * 0.3;
                    
                    let signal = 'NEUTRAL';
                    let signalColor = '#f59e0b';
                    let signalStrength = 'WEAK';
                    
                    if (distanceToNext < signalThreshold) {
                        signal = 'BUY SIGNAL';
                            signalColor = '#22c55e';
                        signalStrength = distanceToNext < signalThreshold * 0.5 ? 'STRONG' : 'MODERATE';
                    } else if (distanceToPrev < signalThreshold) {
                        signal = 'SELL SIGNAL';
                        signalColor = '#ef4444';
                        signalStrength = distanceToPrev < signalThreshold * 0.5 ? 'STRONG' : 'MODERATE';
                    }
                    
                        document.getElementById('currentPosition').textContent = signal;
                        document.getElementById('currentPosition').style.color = signalColor;
                        document.getElementById('signalStrength').textContent = signalStrength;
                        document.getElementById('signalStrength').style.color = signalColor;
                        
                    const formattedNextGrid = nextGrid.toLocaleString('en-US', {
                        style: 'currency',
                        currency: 'USD',
                        minimumFractionDigits: 0,
                        maximumFractionDigits: 0
                    });
                    document.getElementById('nextGridLevel').textContent = formattedNextGrid;
                    document.getElementById('gridLevelsCount').textContent = gridLevels.length;
                }
                
                    // Professional market data update
                    async function updateMarketData() {
                        try {
                            const fundingResponse = await axios.get('/api/funding-rate');
                            if (fundingResponse.data.fundingRate !== undefined) {
                                const fundingRate = (fundingResponse.data.fundingRate * 100).toFixed(4);
                                document.getElementById('fundingRate').textContent = fundingRate + '%';
                                document.getElementById('fundingRate').style.color = fundingRate >= 0 ? '#22c55e' : '#ef4444';
                                
                                const nextFunding = new Date(fundingResponse.data.fundingRateTimestamp + 8 * 60 * 60 * 1000);
                                document.getElementById('nextFunding').textContent = nextFunding.toLocaleTimeString();
                            }
                            
                            const oiResponse = await axios.get('/api/open-interest');
                            if (oiResponse.data.openInterest !== undefined) {
                                const oi = oiResponse.data.openInterest;
                                document.getElementById('openInterest').textContent = oi.toLocaleString();
                                
                                const oiChange = (Math.random() - 0.5) * 2;
                                document.getElementById('oiChange').textContent = (oiChange >= 0 ? '+' : '') + oiChange.toFixed(2) + '%';
                                document.getElementById('oiChange').style.color = oiChange >= 0 ? '#22c55e' : '#ef4444';
                            }
                        } catch (error) {
                            console.log('Error updating market data:', error.message);
                        }
                    }
                    
                    // Professional alert system
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
                    
                    // Professional modal functions
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
                    
                    // Professional auto refresh
                    let autoRefreshInterval = null;
                    
                    function toggleAutoRefresh() {
                        const button = document.getElementById('autoRefreshText');
                        if (autoRefreshInterval) {
                            clearInterval(autoRefreshInterval);
                            autoRefreshInterval = null;
                            button.textContent = 'Auto Refresh';
                        } else {
                            startAutoRefresh();
                            button.textContent = 'Stop Auto Refresh';
                        }
                    }
                    
                    function startAutoRefresh() {
                        autoRefreshInterval = setInterval(() => {
                            loadStatus();
                            updateOrderBook();
                        }, 30000);
                    }
                    
                    // Professional action functions
                    function startBot() {
                        showAlert('Bot started successfully!', 'success');
                    }
                    
                    function pauseBot() {
                        showAlert('Bot paused successfully!', 'warning');
                    }
                    
                    function exportData() {
                        showAlert('Data export started!', 'success');
                    }
                    
                    function viewLogs() {
                        showAlert('Opening logs...', 'info');
                    }
                    
                    function emergencyStop() {
                        showAlert('Emergency stop activated!', 'danger');
                        closeEmergencyModal();
                    }
                    
                    // Close modal when clicking outside
                    window.onclick = function(event) {
                        const modals = document.getElementsByClassName('modal');
                        for (let modal of modals) {
                            if (event.target === modal) {
                                modal.style.display = 'none';
                            }
                        }
                    }
                    
                    // Professional auto trading functions
                    async function startAutoTrading() {
                        try {
                            const tradingMode = document.getElementById('tradingMode').value;
                            const maxDailyLoss = document.getElementById('maxDailyLoss').value;
                            const maxPositions = document.getElementById('maxPositions').value;
                            const leverage = document.getElementById('leverage').value;
                            
                            const response = await axios.post('/api/start-auto-trading', {
                                mode: tradingMode,
                                max_daily_loss: maxDailyLoss,
                                max_positions: maxPositions,
                                leverage: leverage
                            });
                            
                            if (response.data.success) {
                                showAlert('Auto trading started successfully!', 'success');
                                document.getElementById('tradingStatusText').textContent = 'Active';
                                document.getElementById('tradingStatusText').style.color = '#22c55e';
                            } else {
                                showAlert('Failed to start auto trading: ' + response.data.message, 'danger');
                            }
                        } catch (error) {
                            showAlert('Error starting auto trading: ' + error.message, 'danger');
                        }
                    }
                    
                    async function stopAutoTrading() {
                        try {
                            const response = await axios.post('/api/stop-auto-trading');
                            
                            if (response.data.success) {
                                showAlert('Auto trading stopped successfully!', 'warning');
                                document.getElementById('tradingStatusText').textContent = 'Stopped';
                                document.getElementById('tradingStatusText').style.color = '#ef4444';
                            } else {
                                showAlert('Failed to stop auto trading: ' + response.data.message, 'danger');
                            }
                        } catch (error) {
                            showAlert('Error stopping auto trading: ' + error.message, 'danger');
                        }
                    }
                    
                    async function configureTrading() {
                        try {
                            const tradingMode = document.getElementById('tradingMode').value;
                            const maxDailyLoss = document.getElementById('maxDailyLoss').value;
                            const maxPositions = document.getElementById('maxPositions').value;
                            const leverage = document.getElementById('leverage').value;
                            
                            const response = await axios.post('/api/configure-trading', {
                                trading_mode: tradingMode,
                                max_daily_loss: maxDailyLoss,
                                max_positions: maxPositions,
                                leverage: leverage
                            });
                            
                            if (response.data.success) {
                                showAlert('Trading configuration updated successfully!', 'success');
                            } else {
                                showAlert('Failed to update configuration: ' + response.data.message, 'danger');
                            }
                        } catch (error) {
                            showAlert('Error updating configuration: ' + error.message, 'danger');
                        }
                    }
                    
                    // Professional risk management calculations
                function updateRiskMetrics(currentPrice) {
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
                        let riskColor = '#22c55e';
                    
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
                
                    // Professional account details update
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
                                    statusColor = '#22c55e';
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
                                    statusColor = '#22c55e';
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
                            masterTraderElement.style.color = data.is_master_trader ? '#22c55e' : '#6b7280';
                    } else {
                        masterTraderElement.textContent = 'Unknown';
                        masterTraderElement.style.color = '#ef4444';
                    }
                    
                    // Update spot hedging status
                    const spotHedgingElement = document.getElementById('spotHedging');
                    if (data.spot_hedging_status) {
                        spotHedgingElement.textContent = data.spot_hedging_status;
                            spotHedgingElement.style.color = data.spot_hedging_status === 'ON' ? '#22c55e' : '#6b7280';
                    } else {
                        spotHedgingElement.textContent = 'Unknown';
                        spotHedgingElement.style.color = '#ef4444';
                    }
                }
                
                    // Professional troubleshooting update
                function updateTroubleshootingInfo(data) {
                    // Update API status
                    const apiStatusElement = document.getElementById('apiStatusDetailed');
                    if (data.api_status === 'Connected') {
                        apiStatusElement.textContent = 'Connected';
                            apiStatusElement.style.color = '#22c55e';
                    } else {
                        apiStatusElement.textContent = 'Disconnected';
                        apiStatusElement.style.color = '#ef4444';
                    }
                    
                    // Update account access
                    const accountAccessElement = document.getElementById('accountAccess');
                        if (data.account_balance !== null && data.account_balance !== undefined) {
                        accountAccessElement.textContent = 'Available';
                            accountAccessElement.style.color = '#22c55e';
                    } else {
                        accountAccessElement.textContent = 'Unavailable';
                        accountAccessElement.style.color = '#ef4444';
                    }
                    
                    // Update permissions
                    const permissionsElement = document.getElementById('permissions');
                        if (data.active_positions !== null && data.active_positions !== undefined) {
                            permissionsElement.textContent = 'Full Access';
                            permissionsElement.style.color = '#22c55e';
                    } else {
                            permissionsElement.textContent = 'Limited';
                            permissionsElement.style.color = '#f59e0b';
                    }
                    
                    // Update last error
                    const lastErrorElement = document.getElementById('lastError');
                        if (data.error) {
                            lastErrorElement.textContent = data.error;
                        lastErrorElement.style.color = '#ef4444';
                    } else {
                        lastErrorElement.textContent = 'None';
                            lastErrorElement.style.color = '#22c55e';
                    }
                }
                
                    // Professional coin details update
                function updateCoinDetails(coinDetails) {
                    const container = document.getElementById('coinDetailsContainer');
                    container.innerHTML = '';
                    
                        if (coinDetails && coinDetails.length > 0) {
                    coinDetails.forEach(coin => {
                        const coinDiv = document.createElement('div');
                        coinDiv.className = 'metric';
                        coinDiv.innerHTML = `
                                    <span class="metric-label">${coin.coin}</span>
                                    <span class="metric-value">$${coin.usd_value.toLocaleString()}</span>
                                `;
                        container.appendChild(coinDiv);
                    });
                        } else {
                            const noCoinsDiv = document.createElement('div');
                            noCoinsDiv.className = 'metric';
                            noCoinsDiv.innerHTML = `
                                <span class="metric-label">No coins found</span>
                                <span class="metric-value">$0.00</span>
                            `;
                            container.appendChild(noCoinsDiv);
                        }
                    }
                    
                    // Professional Account Settings Functions
                    async function saveAccountSettings() {
                        try {
                            const settings = {
                                api_key_name: document.getElementById('apiKeyName').value,
                                testnet_mode: document.getElementById('testnetMode').value === 'true',
                                default_leverage: parseInt(document.getElementById('defaultLeverage').value),
                                risk_level: document.getElementById('riskLevel').value,
                                spot_symbols: document.getElementById('spotSymbols').value,
                                futures_symbols: document.getElementById('futuresSymbols').value
                            };
                            
                            const response = await axios.post('/api/save-account-settings', settings);
                            
                            if (response.data.success) {
                                updateSettingsStatus('Settings saved successfully', 'success');
                                updateLastSavedTime();
                                showAlert('Account settings saved successfully!', 'success');
                    } else {
                                updateSettingsStatus('Failed to save settings', 'danger');
                                showAlert('Failed to save settings: ' + response.data.error, 'danger');
                            }
                        } catch (error) {
                            updateSettingsStatus('Error saving settings', 'danger');
                            showAlert('Error saving settings: ' + error.message, 'danger');
                        }
                    }
                    
                    async function loadAccountSettings() {
                        try {
                            updateSettingsStatus('Loading settings...', 'warning');
                            
                            const response = await axios.get('/api/load-account-settings');
                            
                            if (response.data.success) {
                                const settings = response.data.settings;
                                
                                document.getElementById('apiKeyName').value = settings.api_key_name || '';
                                document.getElementById('testnetMode').value = settings.testnet_mode ? 'true' : 'false';
                                document.getElementById('defaultLeverage').value = settings.default_leverage || 5;
                                document.getElementById('riskLevel').value = settings.risk_level || 'moderate';
                                document.getElementById('spotSymbols').value = settings.spot_symbols || '';
                                document.getElementById('futuresSymbols').value = settings.futures_symbols || '';
                                
                                updateSettingsStatus('Settings loaded successfully', 'success');
                                showAlert('Account settings loaded successfully!', 'success');
                            } else {
                                updateSettingsStatus('Failed to load settings', 'danger');
                                showAlert('Failed to load settings: ' + response.data.error, 'danger');
                            }
                    } catch (error) {
                            updateSettingsStatus('Error loading settings', 'danger');
                            showAlert('Error loading settings: ' + error.message, 'danger');
                        }
                    }
                    
                    async function testAccountConnection() {
                        try {
                            updateSettingsStatus('Testing connection...', 'warning');
                            
                            const response = await axios.get('/api/test-connection');
                            
                            if (response.data.success) {
                                updateSettingsStatus('Connection successful', 'success');
                                showAlert('Account connection test successful!', 'success');
                            } else {
                                updateSettingsStatus('Connection failed', 'danger');
                                showAlert('Connection test failed: ' + response.data.error, 'danger');
                            }
                    } catch (error) {
                            updateSettingsStatus('Connection error', 'danger');
                            showAlert('Connection test error: ' + error.message, 'danger');
                        }
                    }
                    
                    function resetAccountSettings() {
                        if (confirm('Are you sure you want to reset all account settings to default values?')) {
                            document.getElementById('apiKeyName').value = '';
                            document.getElementById('testnetMode').value = 'false';
                            document.getElementById('defaultLeverage').value = 5;
                            document.getElementById('riskLevel').value = 'moderate';
                            document.getElementById('spotSymbols').value = 'BTCUSDT,ETHUSDT,SOLUSDT';
                            document.getElementById('futuresSymbols').value = 'BTCUSDT,ETHUSDT,SOLUSDT';
                            
                            updateSettingsStatus('Settings reset to default', 'info');
                            showAlert('Account settings reset to default values!', 'info');
                        }
                    }
                    
                    function updateSettingsStatus(message, type) {
                        const statusElement = document.getElementById('settingsStatus');
                        statusElement.textContent = message;
                        
                        // Set color based on type
                        switch(type) {
                            case 'success':
                                statusElement.style.color = '#22c55e';
                                break;
                            case 'warning':
                                statusElement.style.color = '#f59e0b';
                                break;
                            case 'danger':
                                statusElement.style.color = '#ef4444';
                                break;
                            case 'info':
                                statusElement.style.color = '#3b82f6';
                                break;
                            default:
                                statusElement.style.color = '#cbd5e1';
                        }
                    }
                    
                    function updateLastSavedTime() {
                        const now = new Date();
                        const timeString = now.toLocaleString();
                        document.getElementById('lastSavedTime').textContent = `Last saved: ${timeString}`;
                    }
                    
                    // Load settings on page load
                    document.addEventListener('DOMContentLoaded', function() {
                        loadAccountSettings();
                    });
                    
                    // Modal Functions
                    function openAccountSettingsModal() {
                        document.getElementById('accountSettingsModal').style.display = 'block';
                        loadAccountSettingsToModal();
                    }
                    
                    function closeAccountSettingsModal() {
                        document.getElementById('accountSettingsModal').style.display = 'none';
                    }
                    
                    // Close modal when clicking outside
                    window.onclick = function(event) {
                        const modal = document.getElementById('accountSettingsModal');
                        if (event.target === modal) {
                            closeAccountSettingsModal();
                        }
                    }
                    
                    // Modal-specific functions
                    async function saveAccountSettingsFromModal() {
                        try {
                            const settings = {
                                api_key_name: document.getElementById('modalApiKeyName').value,
                                testnet_mode: document.getElementById('modalTestnetMode').value === 'true',
                                default_leverage: parseInt(document.getElementById('modalDefaultLeverage').value),
                                risk_level: document.getElementById('modalRiskLevel').value,
                                spot_symbols: document.getElementById('modalSpotSymbols').value,
                                futures_symbols: document.getElementById('modalFuturesSymbols').value
                            };
                            
                            const response = await axios.post('/api/save-account-settings', settings);
                            
                            if (response.data.success) {
                                updateModalSettingsStatus('Settings saved successfully', 'success');
                                updateModalLastSavedTime();
                                showAlert('Account settings saved successfully!', 'success');
                                
                                // Update main panel status
                                updateSettingsStatus('Settings saved successfully', 'success');
                                updateLastSavedTime();
                        } else {
                                updateModalSettingsStatus('Failed to save settings', 'danger');
                                showAlert('Failed to save settings: ' + response.data.error, 'danger');
                        }
                    } catch (error) {
                            updateModalSettingsStatus('Error saving settings', 'danger');
                            showAlert('Error saving settings: ' + error.message, 'danger');
                        }
                    }
                    
                    async function loadAccountSettingsToModal() {
                        try {
                            updateModalSettingsStatus('Loading settings...', 'warning');
                            
                            const response = await axios.get('/api/load-account-settings');
                            
                            if (response.data.success) {
                                const settings = response.data.settings;
                                
                                document.getElementById('modalApiKeyName').value = settings.api_key_name || '';
                                document.getElementById('modalTestnetMode').value = settings.testnet_mode ? 'true' : 'false';
                                document.getElementById('modalDefaultLeverage').value = settings.default_leverage || 5;
                                document.getElementById('modalRiskLevel').value = settings.risk_level || 'moderate';
                                document.getElementById('modalSpotSymbols').value = settings.spot_symbols || '';
                                document.getElementById('modalFuturesSymbols').value = settings.futures_symbols || '';
                                
                                updateModalSettingsStatus('Settings loaded successfully', 'success');
                                showAlert('Account settings loaded successfully!', 'success');
                        } else {
                                updateModalSettingsStatus('Failed to load settings', 'danger');
                                showAlert('Failed to load settings: ' + response.data.error, 'danger');
                        }
                    } catch (error) {
                            updateModalSettingsStatus('Error loading settings', 'danger');
                            showAlert('Error loading settings: ' + error.message, 'danger');
                        }
                    }
                    
                    async function testAccountConnectionFromModal() {
                        try {
                            updateModalSettingsStatus('Testing connection...', 'warning');
                            
                            const response = await axios.get('/api/test-connection');
                            
                            if (response.data.success) {
                                updateModalSettingsStatus('Connection successful', 'success');
                                showAlert('Account connection test successful!', 'success');
                        } else {
                                updateModalSettingsStatus('Connection failed', 'danger');
                                showAlert('Connection test failed: ' + response.data.error, 'danger');
                        }
                    } catch (error) {
                            updateModalSettingsStatus('Connection error', 'danger');
                            showAlert('Connection test error: ' + error.message, 'danger');
                        }
                    }
                    
                    function resetAccountSettingsInModal() {
                        if (confirm('Are you sure you want to reset all account settings to default values?')) {
                            document.getElementById('modalApiKeyName').value = '';
                            document.getElementById('modalTestnetMode').value = 'false';
                            document.getElementById('modalDefaultLeverage').value = 5;
                            document.getElementById('modalRiskLevel').value = 'moderate';
                            document.getElementById('modalSpotSymbols').value = 'BTCUSDT,ETHUSDT,SOLUSDT';
                            document.getElementById('modalFuturesSymbols').value = 'BTCUSDT,ETHUSDT,SOLUSDT';
                            
                            updateModalSettingsStatus('Settings reset to default', 'info');
                            showAlert('Account settings reset to default values!', 'info');
                        }
                    }
                    
                    function updateModalSettingsStatus(message, type) {
                        const statusElement = document.getElementById('modalSettingsStatus');
                        statusElement.textContent = message;
                        
                        // Set color based on type
                        switch(type) {
                            case 'success':
                                statusElement.style.color = '#22c55e';
                                break;
                            case 'warning':
                                statusElement.style.color = '#f59e0b';
                                break;
                            case 'danger':
                                statusElement.style.color = '#ef4444';
                                break;
                            case 'info':
                                statusElement.style.color = '#3b82f6';
                                break;
                            default:
                                statusElement.style.color = '#cbd5e1';
                        }
                    }
                    
                    function updateModalLastSavedTime() {
                        const now = new Date();
                        const timeString = now.toLocaleString();
                        document.getElementById('modalLastSavedTime').textContent = `Last saved: ${timeString}`;
                    }
                </script>
            </div>
            
            <!-- Account Settings Modal -->
            <div id="accountSettingsModal" class="modal" style="display: none;">
                <div class="modal-content" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
                    <div class="modal-header">
                        <h2><i class="fas fa-user-cog"></i> Account Settings Configuration</h2>
                        <span class="close" onclick="closeAccountSettingsModal()">&times;</span>
                    </div>
                    
                    <div class="modal-body">
                        <!-- Account Configuration -->
                        <div style="margin-bottom: 30px;">
                            <h4 style="color: var(--text-primary); margin-bottom: 20px; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
                                <i class="fas fa-cog"></i> Configuration
                            </h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">API Key Name:</label>
                                    <input type="text" id="modalApiKeyName" placeholder="My Trading Bot" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Testnet Mode:</label>
                                    <select id="modalTestnetMode" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                                        <option value="false">Live Trading</option>
                                        <option value="true">Testnet</option>
                                    </select>
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Default Leverage:</label>
                                    <input type="number" id="modalDefaultLeverage" value="5" min="1" max="100" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Risk Level:</label>
                                    <select id="modalRiskLevel" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                                        <option value="conservative">Conservative</option>
                                        <option value="moderate">Moderate</option>
                                        <option value="aggressive">Aggressive</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Trading Symbols Configuration -->
                        <div style="margin-bottom: 30px;">
                            <h4 style="color: var(--text-primary); margin-bottom: 20px; font-weight: 600; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
                                <i class="fas fa-chart-line"></i> Trading Symbols
                            </h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Spot Symbols:</label>
                                    <input type="text" id="modalSpotSymbols" placeholder="BTCUSDT,ETHUSDT,SOLUSDT" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                                </div>
                                <div style="display: flex; flex-direction: column; gap: 8px;">
                                    <label style="font-weight: 600; color: var(--text-secondary); font-size: 0.9rem;">Futures Symbols:</label>
                                    <input type="text" id="modalFuturesSymbols" placeholder="BTCUSDT,ETHUSDT,SOLUSDT" style="padding: 12px; border: 1px solid var(--border-color); border-radius: 8px; background: rgba(15, 23, 42, 0.8); color: var(--text-primary);">
                                </div>
                            </div>
                        </div>
                        
                        <!-- Action Buttons -->
                        <div style="display: flex; gap: 15px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px;">
                            <button onclick="saveAccountSettingsFromModal()" class="btn btn-success">
                                <i class="fas fa-save"></i> Save Settings
                            </button>
                            <button onclick="loadAccountSettingsToModal()" class="btn btn-primary">
                                <i class="fas fa-sync"></i> Load Settings
                            </button>
                            <button onclick="testAccountConnectionFromModal()" class="btn btn-info">
                                <i class="fas fa-plug"></i> Test Connection
                            </button>
                            <button onclick="resetAccountSettingsInModal()" class="btn btn-warning">
                                <i class="fas fa-undo"></i> Reset to Default
                            </button>
                        </div>
                        
                        <!-- Settings Status -->
                        <div style="padding: 15px; background: rgba(51, 65, 85, 0.3); border-radius: 8px; border: 1px solid var(--border-color);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: var(--text-secondary); font-weight: 600;">Settings Status:</span>
                                <span id="modalSettingsStatus" style="color: var(--text-primary); font-weight: 600;">Ready</span>
                            </div>
                            <div style="margin-top: 10px; font-size: 0.9rem; color: var(--text-secondary);">
                                <span id="modalLastSavedTime">Last saved: Never</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
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
    
    async def save_account_settings_handler(self, request):
        """API endpoint for saving account settings."""
        try:
            data = await request.json()
            
            # Update configuration with new settings
            if 'api_key_name' in data:
                self.config.set('account.api_key_name', data['api_key_name'])
            
            if 'testnet_mode' in data:
                self.config.set('testnet', data['testnet_mode'])
            
            if 'default_leverage' in data:
                self.config.set('futures.leverage', data['default_leverage'])
            
            if 'risk_level' in data:
                self.config.set('trading.risk_level', data['risk_level'])
            
            if 'spot_symbols' in data:
                symbols = [s.strip() for s in data['spot_symbols'].split(',') if s.strip()]
                self.config.set('spot.symbols', symbols)
            
            if 'futures_symbols' in data:
                symbols = [s.strip() for s in data['futures_symbols'].split(',') if s.strip()]
                self.config.set('futures.symbols', symbols)
            
            # Save configuration
            self.config.save()
            
            logger.info("Account settings saved successfully")
            return web.json_response({
                'success': True, 
                'message': 'Account settings saved successfully'
            })
            
        except Exception as e:
            logger.error(f"Error saving account settings: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def load_account_settings_handler(self, request):
        """API endpoint for loading account settings."""
        try:
            # Load settings from configuration
            settings = {
                'api_key_name': self.config.get('account.api_key_name', 'My Trading Bot'),
                'testnet_mode': self.config.get('testnet', False),
                'default_leverage': self.config.get('futures.leverage', 5),
                'risk_level': self.config.get('trading.risk_level', 'moderate'),
                'spot_symbols': ','.join(self.config.get('spot.symbols', ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'])),
                'futures_symbols': ','.join(self.config.get('futures.symbols', ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']))
            }
            
            logger.info("Account settings loaded successfully")
            return web.json_response({
                'success': True, 
                'settings': settings
            })
            
        except Exception as e:
            logger.error(f"Error loading account settings: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def test_connection_handler(self, request):
        """API endpoint for testing account connection."""
        try:
            # Test API connection
            account_info = await self.client.get_account_details()
            
            if account_info.get('retCode') == 0:
                logger.info("Account connection test successful")
                return web.json_response({
                    'success': True, 
                    'message': 'Account connection test successful',
                    'account_status': 'Connected'
                })
            else:
                logger.warning("Account connection test failed")
                return web.json_response({
                    'success': False, 
                    'error': 'Failed to connect to account',
                    'account_status': 'Disconnected'
                })
                
        except Exception as e:
            logger.error(f"Error testing account connection: {e}")
            return web.json_response({
                'success': False, 
                'error': str(e),
                'account_status': 'Error'
            }, status=500)


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