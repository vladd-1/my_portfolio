#!/usr/bin/env python3
"""
Setup Script for Crypto Trading Bot
Guides user through initial configuration
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def create_env_file():
    """Create .env file from template."""
    print_header("STEP 1: API CREDENTIALS")
    
    env_file = Path('.env')
    
    if env_file.exists():
        response = input("\n.env file already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Keeping existing .env file")
            return
    
    print("\n📝 Creating .env file...")
    print("\nYou'll need to get your API credentials from WazirX:")
    print("   1. Log in to https://wazirx.com")
    print("   2. Go to Settings > API Keys")
    print("   3. Create a new API key with trading permissions")
    print("   4. Copy the API Key and Secret")
    
    print("\n⚠️  IMPORTANT: Keep your API keys secure and never share them!")
    
    # Get API credentials
    print("\n" + "-" * 70)
    api_key = input("Enter your WazirX API Key (or press Enter to skip): ").strip()
    api_secret = input("Enter your WazirX API Secret (or press Enter to skip): ").strip()
    
    # Get trading mode
    print("\n" + "-" * 70)
    print("\nTrading Mode:")
    print("  paper - Simulate trading without real money (RECOMMENDED for testing)")
    print("  live  - Execute real trades with real money")
    
    mode = input("\nSelect mode (paper/live) [paper]: ").strip().lower() or 'paper'
    
    # Get risk parameters
    print("\n" + "-" * 70)
    print("\nRisk Management Settings:")
    print("(Press Enter to use default values)")
    
    max_position = input(f"Max position size in USD [100]: ").strip() or '100'
    max_daily_volume = input(f"Max daily trading volume in USD [500]: ").strip() or '500'
    max_daily_loss = input(f"Max daily loss in USD [200]: ").strip() or '200'
    stop_loss = input(f"Stop loss percentage [15]: ").strip() or '15'
    
    # Create .env file
    env_content = f"""# WazirX API Credentials
WAZIRX_API_KEY={api_key}
WAZIRX_API_SECRET={api_secret}

# Trading Mode
TRADING_MODE={mode}

# Risk Management Settings
MAX_POSITION_SIZE={max_position}
MAX_DAILY_VOLUME={max_daily_volume}
MAX_DAILY_LOSS={max_daily_loss}
STOP_LOSS_PERCENTAGE={stop_loss}
MAX_POSITIONS=10

# Trading Parameters
MIN_TRADE_SIZE=10
REBALANCE_THRESHOLD=10
ANALYSIS_INTERVAL=3600

# Circuit Breaker
CIRCUIT_BREAKER_THRESHOLD=25

# Database
DB_PATH=trading_bot.db

# Logging
LOG_LEVEL=INFO
LOG_DIR=logs
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully")


def create_directories():
    """Create necessary directories."""
    print_header("STEP 2: CREATING DIRECTORIES")
    
    dirs = ['logs']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"✅ Created directory: {dir_name}")
        else:
            print(f"📁 Directory already exists: {dir_name}")


def install_dependencies():
    """Install Python dependencies."""
    print_header("STEP 3: INSTALLING DEPENDENCIES")
    
    print("\n📦 Installing required Python packages...")
    print("   This may take a minute...\n")
    
    import subprocess
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("\n✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error installing dependencies: {e}")
        print("   You may need to install them manually:")
        print("   pip install -r requirements.txt")


def test_configuration():
    """Test the configuration."""
    print_header("STEP 4: TESTING CONFIGURATION")
    
    try:
        from config import config
        
        print("\n📋 Configuration Summary:")
        config.print_summary()
        
        print("\n🔍 Validating configuration...")
        if config.validate():
            print("✅ Configuration is valid")
        else:
            print("❌ Configuration has errors (see above)")
            return False
        
        # Test database
        print("\n🗄️  Testing database...")
        from database import Database
        db = Database('test_setup.db')
        db.close()
        os.remove('test_setup.db')
        print("✅ Database test passed")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup function."""
    print("\n" + "=" * 70)
    print("CRYPTO TRADING BOT - SETUP WIZARD")
    print("=" * 70)
    
    print("\n👋 Welcome! This wizard will help you set up the trading bot.")
    print("\nWhat we'll do:")
    print("  1. Configure API credentials and trading parameters")
    print("  2. Create necessary directories")
    print("  3. Install Python dependencies")
    print("  4. Test the configuration")
    
    input("\nPress Enter to continue...")
    
    # Run setup steps
    create_env_file()
    create_directories()
    install_dependencies()
    
    if test_configuration():
        print_header("✅ SETUP COMPLETE!")
        
        print("\n🎉 Your trading bot is ready!")
        print("\nNext steps:")
        print("  1. Review your .env file and adjust settings if needed")
        print("  2. Test in paper trading mode first:")
        print("     python trading_bot.py --mode paper --iterations 1")
        print("  3. When ready for live trading:")
        print("     python trading_bot.py --mode live")
        
        print("\n⚠️  IMPORTANT REMINDERS:")
        print("  - Start with paper trading to test the system")
        print("  - Only invest what you can afford to lose")
        print("  - Monitor the bot regularly")
        print("  - Keep your API keys secure")
        
        print("\n📚 For help, run: python trading_bot.py --help")
    else:
        print_header("⚠️  SETUP INCOMPLETE")
        print("\nPlease fix the errors above and run setup again.")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
