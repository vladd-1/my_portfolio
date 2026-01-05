"""
Configuration Management for Crypto Trading Bot
Handles API credentials, trading parameters, and risk management settings
"""

import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration manager for trading bot."""
    
    def __init__(self, env_file: str = '.env'):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file
        """
        # Load environment variables
        env_path = Path(__file__).parent / env_file
        load_dotenv(env_path)
        
        # API Credentials
        self.WAZIRX_API_KEY = os.getenv('WAZIRX_API_KEY', '')
        self.WAZIRX_API_SECRET = os.getenv('WAZIRX_API_SECRET', '')
        
        # Trading Mode
        self.TRADING_MODE = os.getenv('TRADING_MODE', 'paper').lower()  # 'paper' or 'live'
        
        # Risk Management Settings
        self.MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '100'))  # USD
        self.MAX_DAILY_VOLUME = float(os.getenv('MAX_DAILY_VOLUME', '500'))  # USD
        self.MAX_DAILY_LOSS = float(os.getenv('MAX_DAILY_LOSS', '200'))  # USD
        self.STOP_LOSS_PERCENTAGE = float(os.getenv('STOP_LOSS_PERCENTAGE', '15'))  # %
        self.MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '10'))
        
        # Trading Parameters
        self.MIN_TRADE_SIZE = float(os.getenv('MIN_TRADE_SIZE', '10'))  # USD
        self.REBALANCE_THRESHOLD = float(os.getenv('REBALANCE_THRESHOLD', '10'))  # %
        self.ANALYSIS_INTERVAL = int(os.getenv('ANALYSIS_INTERVAL', '3600'))  # seconds
        
        # WazirX Trading Pairs Mapping
        # Maps crypto names to WazirX trading pairs
        self.TRADING_PAIRS = {
            'Bitcoin': 'btcinr',
            'Ethereum': 'ethinr',
            'Binance Coin': 'bnbinr',
            'Solana': 'solinr',
            'XRP': 'xrpinr',
            'Cardano': 'adainr',
            'Avalanche': 'avaxinr',
            'Dogecoin': 'dogeinr',
            'Polkadot': 'dotinr',
            'Polygon': 'maticinr',
            'Chainlink': 'linkinr',
            'Litecoin': 'ltcinr',
            'Uniswap': 'uniinr',
            'Stellar': 'xlminr',
            'VeChain': 'vetinr',
            'Cosmos': 'atominr',
            'Algorand': 'algoinr',
            'Tron': 'trxinr',
            'Monero': 'xmrinr',
            'EOS': 'eosinr',
            'Filecoin': 'filinr',
            'Hedera': 'hbarinr',
            'Aptos': 'aptinr',
            'Near Protocol': 'nearinr',
            'Arbitrum': 'arbinr',
            'Optimism': 'opinr',
            'Sui': 'suiinr',
            'Injective': 'injinr',
            'Render': 'rndrinr',
            'The Graph': 'grtinr',
            'Kaspa': 'kasinr',
            'Immutable': 'imxinr',
            'Stacks': 'stxinr',
            'Sei': 'seiinr',
            'Celestia': 'tiainr',
            'Fantom': 'ftminr',
            'Theta': 'thetainr',
            'Axie Infinity': 'axsinr',
            'Flow': 'flowinr',
            'Sandbox': 'sandinr',
            'Mina': 'minainr',
            'Aave': 'aaveinr',
            'Maker': 'mkrinr',
            'Quant': 'qntinr',
            'Lido DAO': 'ldoinr',
            'Pepe': 'pepeinr',
            'Bonk': 'bonkinr',
            'Floki': 'flokiinr',
            'Shiba Inu': 'shivinr',
            'Worldcoin': 'wldinr',
        }
        
        # Database Settings
        self.DB_PATH = os.getenv('DB_PATH', 'trading_bot.db')
        
        # Logging Settings
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_DIR = os.getenv('LOG_DIR', 'logs')
        
        # Emergency Settings
        self.EMERGENCY_STOP = False
        self.CIRCUIT_BREAKER_THRESHOLD = float(os.getenv('CIRCUIT_BREAKER_THRESHOLD', '25'))  # %
        
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        errors = []
        
        # Check API credentials for live trading
        if self.TRADING_MODE == 'live':
            if not self.WAZIRX_API_KEY:
                errors.append("WAZIRX_API_KEY is required for live trading")
            if not self.WAZIRX_API_SECRET:
                errors.append("WAZIRX_API_SECRET is required for live trading")
        
        # Validate numeric parameters
        if self.MAX_POSITION_SIZE <= 0:
            errors.append("MAX_POSITION_SIZE must be positive")
        if self.MAX_DAILY_VOLUME <= 0:
            errors.append("MAX_DAILY_VOLUME must be positive")
        if self.MAX_DAILY_LOSS <= 0:
            errors.append("MAX_DAILY_LOSS must be positive")
        if not (0 < self.STOP_LOSS_PERCENTAGE < 100):
            errors.append("STOP_LOSS_PERCENTAGE must be between 0 and 100")
        if self.MAX_POSITIONS <= 0:
            errors.append("MAX_POSITIONS must be positive")
        
        # Validate trading mode
        if self.TRADING_MODE not in ['paper', 'live']:
            errors.append("TRADING_MODE must be 'paper' or 'live'")
        
        if errors:
            print("Configuration validation errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def get_trading_pair(self, crypto_name: str) -> str:
        """
        Get WazirX trading pair for a cryptocurrency.
        
        Args:
            crypto_name: Name of cryptocurrency
            
        Returns:
            Trading pair symbol (e.g., 'btcinr')
        """
        return self.TRADING_PAIRS.get(crypto_name, '')
    
    def is_supported(self, crypto_name: str) -> bool:
        """
        Check if cryptocurrency is supported on WazirX.
        
        Args:
            crypto_name: Name of cryptocurrency
            
        Returns:
            True if supported, False otherwise
        """
        return crypto_name in self.TRADING_PAIRS
    
    def is_live_mode(self) -> bool:
        """Check if bot is in live trading mode."""
        return self.TRADING_MODE == 'live'
    
    def is_paper_mode(self) -> bool:
        """Check if bot is in paper trading mode."""
        return self.TRADING_MODE == 'paper'
    
    def print_summary(self):
        """Print configuration summary."""
        print("=" * 70)
        print("TRADING BOT CONFIGURATION")
        print("=" * 70)
        print(f"\n🔧 Trading Mode: {self.TRADING_MODE.upper()}")
        print(f"\n💰 Risk Management:")
        print(f"   Max Position Size:    ${self.MAX_POSITION_SIZE:,.2f}")
        print(f"   Max Daily Volume:     ${self.MAX_DAILY_VOLUME:,.2f}")
        print(f"   Max Daily Loss:       ${self.MAX_DAILY_LOSS:,.2f}")
        print(f"   Stop Loss:            {self.STOP_LOSS_PERCENTAGE}%")
        print(f"   Max Positions:        {self.MAX_POSITIONS}")
        print(f"\n📊 Trading Parameters:")
        print(f"   Min Trade Size:       ${self.MIN_TRADE_SIZE:,.2f}")
        print(f"   Rebalance Threshold:  {self.REBALANCE_THRESHOLD}%")
        print(f"   Analysis Interval:    {self.ANALYSIS_INTERVAL}s ({self.ANALYSIS_INTERVAL/3600:.1f}h)")
        print(f"\n🔐 API Configuration:")
        print(f"   API Key Set:          {'Yes' if self.WAZIRX_API_KEY else 'No'}")
        print(f"   API Secret Set:       {'Yes' if self.WAZIRX_API_SECRET else 'No'}")
        print(f"\n📁 Storage:")
        print(f"   Database:             {self.DB_PATH}")
        print(f"   Logs Directory:       {self.LOG_DIR}")
        print(f"\n⚡ Supported Pairs:     {len(self.TRADING_PAIRS)}")
        print("=" * 70)


# Global configuration instance
config = Config()


if __name__ == "__main__":
    # Test configuration
    config.print_summary()
    print(f"\n✅ Configuration valid: {config.validate()}")
