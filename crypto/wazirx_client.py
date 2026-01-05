#!/usr/bin/env python3
"""
WazirX API Client
Handles all interactions with WazirX exchange API
"""

import hashlib
import hmac
import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode


class WazirXClient:
    """Client for interacting with WazirX API."""
    
    BASE_URL = "https://api.wazirx.com"
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize WazirX client.
        
        Args:
            api_key: WazirX API key
            api_secret: WazirX API secret
            testnet: Use testnet (if available)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.session = requests.Session()
        self.session.headers.update({
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        })
        
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature for authenticated requests."""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, signed: bool = False, 
                 params: Optional[Dict] = None) -> Dict:
        """
        Make HTTP request to WazirX API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            signed: Whether request requires signature
            params: Request parameters
            
        Returns:
            API response as dictionary
        """
        if params is None:
            params = {}
            
        url = f"{self.BASE_URL}{endpoint}"
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['recvWindow'] = 10000
            params['signature'] = self._generate_signature(params)
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, json=params, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            raise
    
    # ============= Public API Methods =============
    
    def get_server_time(self) -> Dict:
        """Get server time."""
        return self._request('GET', '/sapi/v1/time')
    
    def get_system_status(self) -> Dict:
        """Get system status."""
        return self._request('GET', '/sapi/v1/systemStatus')
    
    def get_tickers(self) -> List[Dict]:
        """Get 24hr ticker price change statistics for all symbols."""
        return self._request('GET', '/sapi/v1/tickers/24hr')
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Get 24hr ticker for a specific symbol.
        
        Args:
            symbol: Trading pair (e.g., 'btcinr', 'ethinr')
        """
        params = {'symbol': symbol.lower()}
        return self._request('GET', '/sapi/v1/ticker/24hr', params=params)
    
    def get_depth(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get order book depth.
        
        Args:
            symbol: Trading pair
            limit: Number of orders to return (default 20, max 1000)
        """
        params = {'symbol': symbol.lower(), 'limit': limit}
        return self._request('GET', '/sapi/v1/depth', params=params)
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> List[Dict]:
        """
        Get recent trades.
        
        Args:
            symbol: Trading pair
            limit: Number of trades (default 100, max 1000)
        """
        params = {'symbol': symbol.lower(), 'limit': limit}
        return self._request('GET', '/sapi/v1/trades', params=params)
    
    def get_exchange_info(self) -> Dict:
        """Get exchange trading rules and symbol information."""
        return self._request('GET', '/sapi/v1/exchangeInfo')
    
    # ============= Private API Methods (Require Authentication) =============
    
    def get_account_info(self) -> Dict:
        """Get current account information including balances."""
        return self._request('GET', '/sapi/v1/account', signed=True)
    
    def get_balances(self) -> List[Dict]:
        """
        Get account balances.
        
        Returns:
            List of assets with free and locked balances
        """
        account_info = self.get_account_info()
        return account_info.get('balances', [])
    
    def get_balance(self, asset: str) -> Optional[Dict]:
        """
        Get balance for a specific asset.
        
        Args:
            asset: Asset symbol (e.g., 'BTC', 'INR', 'USDT')
            
        Returns:
            Balance info or None if not found
        """
        balances = self.get_balances()
        for balance in balances:
            if balance['asset'].upper() == asset.upper():
                return balance
        return None
    
    def create_order(self, symbol: str, side: str, order_type: str, 
                     quantity: float, price: Optional[float] = None) -> Dict:
        """
        Create a new order.
        
        Args:
            symbol: Trading pair (e.g., 'btcinr')
            side: 'buy' or 'sell'
            order_type: 'limit' or 'market'
            quantity: Order quantity
            price: Order price (required for limit orders)
            
        Returns:
            Order creation response
        """
        params = {
            'symbol': symbol.lower(),
            'side': side.lower(),
            'type': order_type.lower(),
            'quantity': quantity
        }
        
        if order_type.lower() == 'limit':
            if price is None:
                raise ValueError("Price is required for limit orders")
            params['price'] = price
            params['timeInForce'] = 'GTC'  # Good Till Cancelled
        
        return self._request('POST', '/sapi/v1/order', signed=True, params=params)
    
    def create_market_buy(self, symbol: str, quantity: float) -> Dict:
        """
        Create market buy order.
        
        Args:
            symbol: Trading pair
            quantity: Quantity to buy
        """
        return self.create_order(symbol, 'buy', 'market', quantity)
    
    def create_market_sell(self, symbol: str, quantity: float) -> Dict:
        """
        Create market sell order.
        
        Args:
            symbol: Trading pair
            quantity: Quantity to sell
        """
        return self.create_order(symbol, 'sell', 'market', quantity)
    
    def create_limit_buy(self, symbol: str, quantity: float, price: float) -> Dict:
        """
        Create limit buy order.
        
        Args:
            symbol: Trading pair
            quantity: Quantity to buy
            price: Limit price
        """
        return self.create_order(symbol, 'buy', 'limit', quantity, price)
    
    def create_limit_sell(self, symbol: str, quantity: float, price: float) -> Dict:
        """
        Create limit sell order.
        
        Args:
            symbol: Trading pair
            quantity: Quantity to sell
            price: Limit price
        """
        return self.create_order(symbol, 'sell', 'limit', quantity, price)
    
    def get_order(self, symbol: str, order_id: int) -> Dict:
        """
        Get order status.
        
        Args:
            symbol: Trading pair
            order_id: Order ID
        """
        params = {
            'symbol': symbol.lower(),
            'orderId': order_id
        }
        return self._request('GET', '/sapi/v1/order', signed=True, params=params)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict:
        """
        Cancel an active order.
        
        Args:
            symbol: Trading pair
            order_id: Order ID to cancel
        """
        params = {
            'symbol': symbol.lower(),
            'orderId': order_id
        }
        return self._request('DELETE', '/sapi/v1/order', signed=True, params=params)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get all open orders.
        
        Args:
            symbol: Optional trading pair filter
        """
        params = {}
        if symbol:
            params['symbol'] = symbol.lower()
        return self._request('GET', '/sapi/v1/openOrders', signed=True, params=params)
    
    def get_all_orders(self, symbol: str, limit: int = 500) -> List[Dict]:
        """
        Get all orders (active, canceled, filled).
        
        Args:
            symbol: Trading pair
            limit: Number of orders to return (max 1000)
        """
        params = {
            'symbol': symbol.lower(),
            'limit': limit
        }
        return self._request('GET', '/sapi/v1/allOrders', signed=True, params=params)
    
    def get_my_trades(self, symbol: str, limit: int = 500) -> List[Dict]:
        """
        Get account trade history.
        
        Args:
            symbol: Trading pair
            limit: Number of trades (max 1000)
        """
        params = {
            'symbol': symbol.lower(),
            'limit': limit
        }
        return self._request('GET', '/sapi/v1/myTrades', signed=True, params=params)
    
    # ============= Helper Methods =============
    
    def get_current_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Current price as float
        """
        ticker = self.get_ticker(symbol)
        return float(ticker.get('lastPrice', 0))
    
    def get_available_balance(self, asset: str) -> float:
        """
        Get available (free) balance for an asset.
        
        Args:
            asset: Asset symbol
            
        Returns:
            Available balance as float
        """
        balance = self.get_balance(asset)
        if balance:
            return float(balance.get('free', 0))
        return 0.0
    
    def test_connectivity(self) -> bool:
        """
        Test API connectivity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.get_server_time()
            return True
        except Exception as e:
            print(f"Connectivity test failed: {e}")
            return False
    
    def test_authentication(self) -> bool:
        """
        Test API authentication.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            self.get_account_info()
            return True
        except Exception as e:
            print(f"Authentication test failed: {e}")
            return False


if __name__ == "__main__":
    # Example usage (requires valid API credentials)
    print("WazirX API Client")
    print("=" * 50)
    print("\nThis module provides a client for WazirX API.")
    print("Import and use with your API credentials:")
    print("\n  from wazirx_client import WazirXClient")
    print("  client = WazirXClient(api_key, api_secret)")
    print("  balances = client.get_balances()")
