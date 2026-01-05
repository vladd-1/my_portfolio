# WazirX Automated Crypto Trading Bot

An intelligent automated cryptocurrency trading bot that integrates with WazirX exchange to maximize profits using advanced Monte Carlo analysis.

## 🌟 Features

- **Automated Trading**: Executes buy/sell orders automatically based on profit analysis
- **Advanced Analysis**: Uses Monte Carlo simulations to predict 30-day returns
- **Risk Management**: Multiple safety features including position limits, stop-losses, and circuit breakers
- **Paper Trading**: Test strategies without risking real money
- **Portfolio Tracking**: Real-time P&L calculation and performance metrics
- **Database Storage**: Persistent storage of all trades and positions

## ⚠️ Important Warnings

**FINANCIAL RISK**: This bot trades with real money. You could lose significant amounts due to:
- Market volatility
- Software bugs
- API issues
- Network problems

**ONLY INVEST WHAT YOU CAN AFFORD TO LOSE**

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python setup.py
```

### 2. Configuration

The setup wizard will create a `.env` file. You can also copy from the example:

```bash
cp .env.example .env
# Edit .env with your API credentials and settings
```

**Required for Live Trading:**
- WazirX API Key
- WazirX API Secret

Get these from: https://wazirx.com/settings/keys

### 3. Test with Paper Trading

**ALWAYS test with paper trading first!**

```bash
# Run one iteration in paper mode
python trading_bot.py --mode paper --iterations 1

# Run continuously in paper mode
python trading_bot.py --mode paper
```

### 4. Live Trading

**Only after thorough testing:**

```bash
# Run in live mode
python trading_bot.py --mode live
```

## 📊 Usage

### Command Line Options

```bash
# Paper trading mode
python trading_bot.py --mode paper

# Live trading mode
python trading_bot.py --mode live

# Run specific number of iterations
python trading_bot.py --iterations 5

# Analysis only (no trading)
python trading_bot.py --analyze-only
```

### Configuration Options

Edit `.env` file to customize:

- `TRADING_MODE`: `paper` or `live`
- `MAX_POSITION_SIZE`: Maximum USD per position (default: 100)
- `MAX_DAILY_VOLUME`: Maximum USD traded per day (default: 500)
- `MAX_DAILY_LOSS`: Maximum USD loss per day (default: 200)
- `STOP_LOSS_PERCENTAGE`: Stop loss % per position (default: 15)
- `ANALYSIS_INTERVAL`: Seconds between analysis runs (default: 3600)

## 🛡️ Safety Features

### Risk Management
- **Position Size Limits**: Maximum amount per trade
- **Daily Volume Limits**: Maximum total trading per day
- **Daily Loss Limits**: Circuit breaker if losses exceed threshold
- **Stop Loss**: Automatic exit if position drops by set percentage
- **Max Positions**: Limit on concurrent positions

### Circuit Breaker
Automatically stops all trading if portfolio drops by 25% (configurable)

### Paper Trading Mode
Test all strategies without risking real money

## 📁 Project Structure

```
crypto/
├── trading_bot.py              # Main trading bot
├── wazirx_client.py           # WazirX API client
├── config.py                  # Configuration management
├── risk_manager.py            # Risk management system
├── portfolio_tracker.py       # Portfolio tracking
├── database.py                # Database layer
├── crypto_profit_maximizer.py # Analysis engine
├── setup.py                   # Setup wizard
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🔧 How It Works

1. **Analysis**: Runs Monte Carlo simulations on 50+ cryptocurrencies
2. **Ranking**: Scores and ranks based on expected returns and risk metrics
3. **Allocation**: Calculates optimal portfolio allocation
4. **Execution**: Places buy orders for top-ranked cryptocurrencies
5. **Monitoring**: Continuously monitors positions for stop-loss triggers
6. **Rebalancing**: Periodically reanalyzes and rebalances portfolio

## 📈 Analysis Methodology

The bot uses a comprehensive scoring system:

- **Expected Return** (35%): Predicted 30-day returns
- **Upside Potential** (25%): 90th percentile outcomes
- **Risk-Adjusted Return** (20%): Sortino ratio
- **Downside Protection** (15%): 10th percentile risk
- **Sharpe Ratio** (5%): Risk-adjusted performance

## 💾 Database

All trades and positions are stored in SQLite database (`trading_bot.db`):

- Trade history
- Position tracking
- Balance snapshots
- Performance metrics

## 🐛 Troubleshooting

### API Connection Issues
```bash
# Test API connectivity
python -c "from wazirx_client import WazirXClient; client = WazirXClient('key', 'secret'); print(client.test_connectivity())"
```

### Configuration Issues
```bash
# Validate configuration
python -c "from config import config; config.print_summary(); print(config.validate())"
```

### Database Issues
```bash
# Test database
python -c "from database import Database; db = Database(); print('OK'); db.close()"
```

## 📚 API Documentation

WazirX API Documentation: https://docs.wazirx.com/

## ⚖️ Disclaimer

**This software is for educational purposes only.**

- Not financial advice
- Use at your own risk
- No guarantees of profit
- Past performance doesn't guarantee future results
- Cryptocurrency trading is highly risky
- Consult a financial advisor before trading

## 🔐 Security

- Never commit your `.env` file to version control
- Keep API keys secure
- Use API keys with minimal required permissions
- Regularly rotate API keys
- Monitor account activity

## 📝 License

This project is provided as-is without warranty.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test in paper mode first
4. Start with small amounts in live mode

## 🎯 Best Practices

1. **Always start with paper trading**
2. **Test thoroughly before going live**
3. **Start with small amounts**
4. **Monitor regularly**
5. **Set conservative risk limits**
6. **Keep detailed records**
7. **Review performance weekly**
8. **Adjust strategy based on results**

## 📊 Example Output

```
================================================================================
PORTFOLIO SUMMARY
================================================================================

💰 Account Value:
   Total Value:      $10,450.23
   Cash Balance:     $5,230.15
   Crypto Value:     $5,220.08

📊 Performance:
   Initial Capital:  $10,000.00
   Total P&L:        +$450.23 (+4.50%)
   Unrealized P&L:   +$220.08
   Total Fees:       $12.50

📈 Positions (5):
   Symbol       Quantity        Avg Price    Current      Value        P&L
   ---------------------------------------------------------------------------
   btcinr       0.020000        $45000.00    $46000.00    $920.00      +$20.00 (+2.2%)
   ethinr       1.500000        $2500.00     $2600.00     $3900.00     +$150.00 (+4.0%)
   ...
================================================================================
```

---

**Remember: Only invest what you can afford to lose. Cryptocurrency trading carries significant risk.**
