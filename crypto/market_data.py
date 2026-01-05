"""
Real-time Market Data Fetcher for WazirX
Fetches live prices and updates crypto analysis with current market data
"""

import time
from typing import Dict, Optional
from wazirx_client import WazirXClient
from config import config


class MarketDataFetcher:
    """Fetches real-time market data from WazirX."""
    
    def __init__(self, use_live_data: bool = True):
        """
        Initialize market data fetcher.
        
        Args:
            use_live_data: If True, fetch from WazirX API. If False, use simulated data.
        """
        self.use_live_data = use_live_data
        self.client = None
        self.price_cache = {}
        self.cache_timestamp = 0
        self.cache_ttl = 60  # Cache for 60 seconds
        
        if use_live_data:
            # Initialize client without auth for public data
            self.client = WazirXClient('', '')
            print("✅ Real-time market data enabled")
        else:
            print("📝 Using simulated market data")
    
    def get_live_price(self, symbol: str) -> Optional[float]:
        """
        Get live price from WazirX.
        
        Args:
            symbol: Trading pair (e.g., 'btcinr')
            
        Returns:
            Current price or None if unavailable
        """
        if not self.use_live_data or not self.client:
            return None
        
        try:
            ticker = self.client.get_ticker(symbol)
            price = float(ticker.get('lastPrice', 0))
            return price if price > 0 else None
        except Exception as e:
            print(f"⚠️  Error fetching price for {symbol}: {e}")
            return None
    
    def get_all_tickers(self) -> Dict[str, float]:
        """
        Get all ticker prices from WazirX.
        
        Returns:
            Dict of symbol -> price
        """
        if not self.use_live_data or not self.client:
            return {}
        
        # Check cache
        current_time = time.time()
        if self.price_cache and (current_time - self.cache_timestamp) < self.cache_ttl:
            return self.price_cache
        
        try:
            tickers = self.client.get_tickers()
            prices = {}
            
            for ticker in tickers:
                symbol = ticker.get('symbol', '').lower()
                price = float(ticker.get('lastPrice', 0))
                if price > 0:
                    prices[symbol] = price
            
            # Update cache
            self.price_cache = prices
            self.cache_timestamp = current_time
            
            print(f"✅ Fetched {len(prices)} live prices from WazirX")
            return prices
            
        except Exception as e:
            print(f"⚠️  Error fetching tickers: {e}")
            return {}
    
    def get_current_price(self, symbol: str, fallback_price: float = 0) -> float:
        """
        Get current price with fallback.
        
        Args:
            symbol: Trading pair
            fallback_price: Price to use if live data unavailable
            
        Returns:
            Current price
        """
        if self.use_live_data:
            # Try cache first
            if symbol in self.price_cache:
                cache_age = time.time() - self.cache_timestamp
                if cache_age < self.cache_ttl:
                    return self.price_cache[symbol]
            
            # Fetch live price
            live_price = self.get_live_price(symbol)
            if live_price:
                self.price_cache[symbol] = live_price
                self.cache_timestamp = time.time()
                return live_price
        
        # Use fallback (simulated price)
        if fallback_price > 0:
            # Add small random variation for realism
            import random
            variation = random.uniform(-0.02, 0.02)
            return fallback_price * (1 + variation)
        
        return fallback_price
    
    def update_crypto_prices(self) -> Dict[str, float]:
        """
        Update prices for all supported cryptocurrencies.
        
        Returns:
            Dict of crypto_name -> current_price
        """
        from crypto_profit_maximizer import CRYPTOCURRENCIES
        
        updated_prices = {}
        
        if self.use_live_data:
            # Fetch all tickers at once (more efficient)
            all_prices = self.get_all_tickers()
            
            for crypto_name, params in CRYPTOCURRENCIES.items():
                symbol = config.get_trading_pair(crypto_name)
                
                if symbol and symbol in all_prices:
                    updated_prices[crypto_name] = all_prices[symbol]
                    print(f"✅ {crypto_name}: ${all_prices[symbol]:,.6f}")
                else:
                    # Use base price as fallback
                    updated_prices[crypto_name] = params['price']
                    if symbol:
                        print(f"⚠️  {crypto_name}: Using base price (live data unavailable)")
        else:
            # Use simulated prices
            for crypto_name, params in CRYPTOCURRENCIES.items():
                import random
                variation = random.uniform(-0.02, 0.02)
                updated_prices[crypto_name] = params['price'] * (1 + variation)
        
        return updated_prices
    
    def get_market_summary(self) -> Dict:
        """
        Get market summary statistics.
        
        Returns:
            Dict with market statistics
        """
        if not self.use_live_data:
            return {'status': 'simulated', 'available_pairs': 0}
        
        try:
            all_prices = self.get_all_tickers()
            
            # Calculate some basic stats
            prices_list = list(all_prices.values())
            
            return {
                'status': 'live',
                'available_pairs': len(all_prices),
                'avg_price': sum(prices_list) / len(prices_list) if prices_list else 0,
                'min_price': min(prices_list) if prices_list else 0,
                'max_price': max(prices_list) if prices_list else 0,
                'cache_age': time.time() - self.cache_timestamp
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}


# Global instance
market_data = MarketDataFetcher(use_live_data=True)


if __name__ == "__main__":
    # Test market data fetcher
    print("=" * 70)
    print("MARKET DATA FETCHER TEST")
    print("=" * 70)
    
    fetcher = MarketDataFetcher(use_live_data=True)
    
    # Test single price
    print("\n📊 Testing single price fetch:")
    btc_price = fetcher.get_live_price('btcinr')
    if btc_price:
        print(f"BTC/INR: ₹{btc_price:,.2f}")
    
    # Test all tickers
    print("\n📊 Testing all tickers fetch:")
    all_prices = fetcher.get_all_tickers()
    print(f"Fetched {len(all_prices)} prices")
    
    # Show sample
    print("\nSample prices:")
    for symbol, price in list(all_prices.items())[:5]:
        print(f"  {symbol}: ₹{price:,.6f}")
    
    # Market summary
    print("\n📊 Market Summary:")
    summary = fetcher.get_market_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
