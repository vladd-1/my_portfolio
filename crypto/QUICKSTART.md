# 🚀 Quick Start Guide - WazirX Trading Bot

## ⚡ Get Started in 5 Minutes

### Step 1: Get WazirX API Credentials

1. Log in to https://wazirx.com
2. Go to **Settings** → **API Keys**
3. Create a new API key with **trading permissions**
4. Save your API Key and Secret securely

### Step 2: Configure the Bot

```bash
cd /home/vladd/portfolio/crypto

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

**Set these values in .env:**
```
WAZIRX_API_KEY=your_api_key_here
WAZIRX_API_SECRET=your_api_secret_here
TRADING_MODE=paper
```

### Step 3: Test in Paper Mode

```bash
# Run one iteration (no real money)
python3 trading_bot.py --mode paper --iterations 1
```

This will:
- ✅ Analyze 50+ cryptocurrencies
- ✅ Generate top 10 recommendations
- ✅ Simulate portfolio allocation
- ✅ Show expected returns

### Step 4: Monitor Results

```bash
# View dashboard
python3 dashboard.py --once
```

---

## 📊 Example Output

When you run the bot, you'll see:

```
================================================================================
WAZIRX AUTOMATED TRADING BOT
================================================================================

🤖 Mode: PAPER TRADING (Simulation)

💰 Initial Capital: $10,000.00
✅ Bot initialized successfully

================================================================================
🔍 RUNNING PROFIT ANALYSIS
================================================================================

✅ Analysis complete: 10 tradeable recommendations

Rank   Crypto               Symbol       Allocation   Expected Return
--------------------------------------------------------------------------------
1      Pepe                 pepeinr       10.74%         16.19%
2      Kaspa                kasinr        10.46%         13.93%
3      Sui                  suiinr        10.42%         13.00%
...
```

---

## 🎯 Common Commands

### Paper Trading (Safe Testing)
```bash
# Run once
python3 trading_bot.py --mode paper --iterations 1

# Run continuously
python3 trading_bot.py --mode paper

# Analysis only (no trades)
python3 trading_bot.py --analyze-only
```

### Live Trading (Real Money)
```bash
# ⚠️ ONLY AFTER THOROUGH TESTING!
python3 trading_bot.py --mode live
```

### Monitoring
```bash
# Real-time dashboard
python3 dashboard.py

# One-time snapshot
python3 dashboard.py --once

# View profit analysis
python3 crypto_profit_maximizer.py
```

---

## ⚙️ Configuration Options

Edit `.env` to customize:

| Setting | Default | Description |
|---------|---------|-------------|
| `TRADING_MODE` | paper | `paper` or `live` |
| `MAX_POSITION_SIZE` | 100 | Max USD per position |
| `MAX_DAILY_VOLUME` | 500 | Max USD traded per day |
| `MAX_DAILY_LOSS` | 200 | Max USD loss per day |
| `STOP_LOSS_PERCENTAGE` | 15 | Stop loss % |
| `ANALYSIS_INTERVAL` | 3600 | Seconds between analysis (1 hour) |

---

## 🛡️ Safety Checklist

Before going live:

- [ ] Tested in paper mode for 24+ hours
- [ ] Reviewed all trades in dashboard
- [ ] Verified stop-loss triggers work
- [ ] Set conservative risk limits
- [ ] Have monitoring plan
- [ ] Starting with small amount ($100-500)

---

## 🆘 Need Help?

**Configuration issues:**
```bash
python3 -c "from config import config; config.print_summary()"
```

**Test database:**
```bash
python3 -c "from database import Database; db = Database('test.db'); print('OK'); db.close()"
```

**Full documentation:**
- See [README.md](file:///home/vladd/portfolio/crypto/README.md)
- See [walkthrough.md](file:///home/vladd/.gemini/antigravity/brain/640a4fa5-223c-4e92-97f2-d171e215dee6/walkthrough.md)

---

## ⚠️ Important Reminders

> **ALWAYS START WITH PAPER TRADING**

> **ONLY INVEST WHAT YOU CAN AFFORD TO LOSE**

> **CRYPTOCURRENCY TRADING IS HIGHLY RISKY**

---

**Ready to maximize your crypto profits! 🚀🌙**
