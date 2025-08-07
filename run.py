#!/usr/bin/env python3
"""
ByBit Grid Trading Bot - Entry Point
Run this script to start the trading bot.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import main

if __name__ == "__main__":
    asyncio.run(main()) 