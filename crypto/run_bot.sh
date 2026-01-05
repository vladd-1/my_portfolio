#!/bin/bash
# Simple launcher script for the trading bot
# Uses system Python which has all dependencies

cd "$(dirname "$0")"

# Run with system Python
python3 trading_bot.py "$@"
