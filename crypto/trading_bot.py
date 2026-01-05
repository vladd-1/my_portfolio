#!/usr/bin/env python3
"""
Automated Crypto Trading Bot for WazirX
Integrates profit analysis with automated trading
"""

import time
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from wazirx_client import WazirXClient
from config import config
from risk_manager import RiskManager
from database import Database
from portfolio_tracker import PortfolioTracker
from crypto_profit_maximizer import get_top_recommendations
from market_data import MarketDataFetcher


class TradingBot:
    """Automated cryptocurrency trading bot."""
    
    def __init__(self, paper_mode: bool = None):
        """
        Initialize trading bot.
        
        Args:
            paper_mode: Override config paper mode setting
        """
        # Set trading mode
        if paper_mode is not None:
            self.paper_mode = paper_mode
        else:
            self.paper_mode = config.is_paper_mode()
        
        print("\n" + "=" * 80)
        print("WAZIRX AUTOMATED TRADING BOT")
        print("=" * 80)
        print(f"\n🤖 Mode: {'PAPER TRADING (Simulation)' if self.paper_mode else '🔴 LIVE TRADING'}")
        
        # Initialize components
        self.db = Database()
        self.risk_manager = RiskManager()
        
        # Initialize WazirX client (only for live mode)
        self.client = None
        if not self.paper_mode:
            if not config.WAZIRX_API_KEY or not config.WAZIRX_API_SECRET:
                print("\n❌ ERROR: API credentials required for live trading")
                print("   Please set WAZIRX_API_KEY and WAZIRX_API_SECRET in .env file")
                sys.exit(1)
            
            self.client = WazirXClient(config.WAZIRX_API_KEY, config.WAZIRX_API_SECRET)
            
            # Test connectivity
            print("\n🔌 Testing API connection...")
            if not self.client.test_connectivity():
                print("❌ Failed to connect to WazirX API")
                sys.exit(1)
            
            if not self.client.test_authentication():
                print("❌ Failed to authenticate with WazirX API")
                sys.exit(1)
            
            print("✅ Connected to WazirX API")
        
        # Initialize market data fetcher
        # Use live data even in paper mode for realistic prices
        self.market_data = MarketDataFetcher(use_live_data=True)
        
        # Get initial capital
        initial_capital = self._get_initial_capital()
        self.portfolio = PortfolioTracker(self.db, initial_capital)
        self.risk_manager.set_initial_portfolio_value(initial_capital)
        
        # State
        self.running = False
        self.last_analysis_time = None
        self.current_recommendations = []
        
        print(f"\n💰 Initial Capital: ${initial_capital:,.2f}")
        print("✅ Bot initialized successfully")
    
    def _get_initial_capital(self) -> float:
        """Get initial capital from account or config."""
        if self.paper_mode:
            # Use default for paper trading
            return 10000.0
        else:
            # Get INR balance from WazirX
            try:
                inr_balance = self.client.get_available_balance('INR')
                if inr_balance > 0:
                    return inr_balance
                else:
                    print("\n⚠️  WARNING: No INR balance found in account")
                    return 10000.0
            except Exception as e:
                print(f"\n⚠️  WARNING: Could not fetch balance: {e}")
                return 10000.0
    
    def _get_current_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol.
        
        Args:
            symbol: WazirX trading pair (e.g., 'btcinr')
            
        Returns:
            Current price
        """
        # Get fallback price from base data
        from crypto_profit_maximizer import CRYPTOCURRENCIES
        fallback_price = 0
        for crypto_name, params in CRYPTOCURRENCIES.items():
            if config.get_trading_pair(crypto_name) == symbol:
                fallback_price = params['price']
                break
        
        # Use market data fetcher (works for both paper and live modes)
        if self.paper_mode:
            # In paper mode, try to get real price but use simulated if unavailable
            price = self.market_data.get_current_price(symbol, fallback_price)
            return price
        else:
            # In live mode, must use real prices
            try:
                return self.client.get_current_price(symbol)
            except Exception as e:
                print(f"⚠️  Error fetching price for {symbol}: {e}")
                # Use market data fetcher as backup
                return self.market_data.get_current_price(symbol, fallback_price)
    
    def _execute_buy(self, symbol: str, usd_amount: float) -> bool:
        """
        Execute a buy order.
        
        Args:
            symbol: Trading pair
            usd_amount: Amount in USD to buy
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current price
            price = self._get_current_price(symbol)
            if price <= 0:
                print(f"❌ Invalid price for {symbol}")
                return False
            
            # Calculate quantity
            quantity = usd_amount / price
            
            # Check risk approval
            approved, reason = self.risk_manager.approve_trade(symbol, 'buy', quantity, price)
            if not approved:
                print(f"❌ Trade rejected: {reason}")
                return False
            
            # Execute order
            if self.paper_mode:
                # Simulate order
                print(f"📝 [PAPER] BUY {quantity:.6f} {symbol} @ ${price:.2f}")
                fee = usd_amount * 0.002  # 0.2% fee
            else:
                # Real order
                print(f"🔄 Executing BUY order: {quantity:.6f} {symbol}")
                order = self.client.create_market_buy(symbol, quantity)
                print(f"✅ Order executed: {order.get('orderId')}")
                fee = float(order.get('fee', usd_amount * 0.002))
            
            # Record trade
            self.portfolio.record_buy(symbol, quantity, price, fee)
            self.risk_manager.record_trade(symbol, 'buy', quantity, price, fee)
            
            return True
            
        except Exception as e:
            print(f"❌ Error executing buy: {e}")
            return False
    
    def _execute_sell(self, symbol: str, quantity: float) -> bool:
        """
        Execute a sell order.
        
        Args:
            symbol: Trading pair
            quantity: Quantity to sell
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current price
            price = self._get_current_price(symbol)
            if price <= 0:
                print(f"❌ Invalid price for {symbol}")
                return False
            
            # Check risk approval
            approved, reason = self.risk_manager.approve_trade(symbol, 'sell', quantity, price)
            if not approved:
                print(f"❌ Trade rejected: {reason}")
                return False
            
            # Execute order
            if self.paper_mode:
                # Simulate order
                print(f"📝 [PAPER] SELL {quantity:.6f} {symbol} @ ${price:.2f}")
                fee = (quantity * price) * 0.002  # 0.2% fee
            else:
                # Real order
                print(f"🔄 Executing SELL order: {quantity:.6f} {symbol}")
                order = self.client.create_market_sell(symbol, quantity)
                print(f"✅ Order executed: {order.get('orderId')}")
                fee = float(order.get('fee', (quantity * price) * 0.002))
            
            # Record trade
            self.portfolio.record_sell(symbol, quantity, price, fee)
            self.risk_manager.record_trade(symbol, 'sell', quantity, price, fee)
            
            return True
            
        except Exception as e:
            print(f"❌ Error executing sell: {e}")
            return False
    
    def run_analysis(self):
        """Run profit maximizer analysis and get recommendations."""
        print("\n" + "=" * 80)
        print("🔍 RUNNING PROFIT ANALYSIS")
        print("=" * 80)
        
        # Get top recommendations
        recommendations = get_top_recommendations(top_n=10, silent=True)
        
        # Filter for supported pairs on WazirX
        supported_recommendations = []
        for rec in recommendations:
            crypto_name = rec['crypto']
            if config.is_supported(crypto_name):
                rec['symbol'] = config.get_trading_pair(crypto_name)
                supported_recommendations.append(rec)
            else:
                print(f"⚠️  {crypto_name} not available on WazirX, skipping")
        
        self.current_recommendations = supported_recommendations
        self.last_analysis_time = datetime.now()
        
        print(f"\n✅ Analysis complete: {len(supported_recommendations)} tradeable recommendations")
        
        # Display recommendations
        print(f"\n{'Rank':<6} {'Crypto':<20} {'Symbol':<12} {'Allocation':<12} {'Expected Return':<15}")
        print("-" * 80)
        for i, rec in enumerate(supported_recommendations, 1):
            print(f"{i:<6} {rec['crypto']:<20} {rec['symbol']:<12} "
                  f"{rec['allocation_pct']:>6.2f}%      {rec['avg_return']:>8.2f}%")
    
    def execute_portfolio_rebalance(self):
        """Execute portfolio rebalancing based on current recommendations."""
        if not self.current_recommendations:
            print("\n⚠️  No recommendations available, run analysis first")
            return
        
        print("\n" + "=" * 80)
        print("⚖️  REBALANCING PORTFOLIO")
        print("=" * 80)
        
        # Check if trading is allowed
        can_trade, reason = self.risk_manager.can_trade()
        if not can_trade:
            print(f"\n❌ Trading not allowed: {reason}")
            return
        
        # Get current prices
        current_prices = {}
        for rec in self.current_recommendations:
            symbol = rec['symbol']
            current_prices[symbol] = self._get_current_price(symbol)
        
        # Calculate current portfolio value
        portfolio_value = self.portfolio.calculate_total_portfolio_value(current_prices)
        available_cash = self.portfolio.cash_balance
        
        print(f"\n💰 Portfolio Value: ${portfolio_value:,.2f}")
        print(f"💵 Available Cash: ${available_cash:,.2f}")
        
        # Execute buys for recommended positions
        print(f"\n📈 Executing buy orders...")
        
        for rec in self.current_recommendations:
            symbol = rec['symbol']
            crypto_name = rec['crypto']
            allocation_pct = rec['allocation_pct']
            
            # Calculate target position size
            target_value = portfolio_value * (allocation_pct / 100)
            
            # Get current position
            current_position = self.portfolio.get_position(symbol)
            current_value = 0
            if current_position:
                current_price = current_prices[symbol]
                current_value = current_position['quantity'] * current_price
            
            # Calculate how much to buy
            buy_amount = target_value - current_value
            
            # Apply position sizing limits
            if buy_amount > 0:
                buy_amount = self.risk_manager.calculate_position_size(
                    symbol, current_prices[symbol], allocation_pct, available_cash
                )
                
                if buy_amount >= config.MIN_TRADE_SIZE:
                    print(f"\n🎯 {crypto_name} ({symbol})")
                    print(f"   Target: ${target_value:.2f} ({allocation_pct:.2f}%)")
                    print(f"   Current: ${current_value:.2f}")
                    print(f"   Buy: ${buy_amount:.2f}")
                    
                    if self._execute_buy(symbol, buy_amount):
                        available_cash -= buy_amount
                        time.sleep(1)  # Rate limiting
                else:
                    print(f"⏭️  Skipping {crypto_name}: buy amount ${buy_amount:.2f} below minimum")
        
        print("\n✅ Rebalancing complete")
    
    def check_stop_losses(self):
        """Check and execute stop losses for all positions."""
        positions = self.portfolio.get_all_positions()
        
        if not positions:
            return
        
        print("\n🛡️  Checking stop losses...")
        
        for symbol, pos in positions.items():
            current_price = self._get_current_price(symbol)
            
            if self.risk_manager.check_stop_loss(symbol, current_price):
                # Execute stop loss
                print(f"🚨 Executing stop loss for {symbol}")
                self._execute_sell(symbol, pos['quantity'])
                time.sleep(1)
    
    def run_once(self):
        """Run one iteration of the trading bot."""
        print("\n" + "=" * 80)
        print(f"🤖 BOT ITERATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Check if we need to run analysis
        should_analyze = (
            self.last_analysis_time is None or
            datetime.now() - self.last_analysis_time > timedelta(seconds=config.ANALYSIS_INTERVAL)
        )
        
        if should_analyze:
            self.run_analysis()
            self.execute_portfolio_rebalance()
        
        # Check stop losses
        self.check_stop_losses()
        
        # Get current prices for portfolio
        current_prices = {}
        for symbol in self.portfolio.get_all_positions().keys():
            current_prices[symbol] = self._get_current_price(symbol)
        
        # Print portfolio summary
        self.portfolio.print_portfolio_summary(current_prices)
        
        # Print risk summary
        self.risk_manager.print_risk_summary()
        
        # Save snapshot
        self.portfolio.save_snapshot(current_prices)
        
        # Check circuit breaker
        portfolio_value = self.portfolio.calculate_total_portfolio_value(current_prices)
        self.risk_manager.check_circuit_breaker(portfolio_value)
    
    def run(self, iterations: int = None):
        """
        Run the trading bot.
        
        Args:
            iterations: Number of iterations to run (None = infinite)
        """
        self.running = True
        iteration = 0
        
        print("\n🚀 Starting trading bot...")
        print(f"⏱️  Analysis interval: {config.ANALYSIS_INTERVAL}s ({config.ANALYSIS_INTERVAL/3600:.1f}h)")
        
        try:
            while self.running:
                iteration += 1
                
                if iterations and iteration > iterations:
                    print(f"\n✅ Completed {iterations} iterations")
                    break
                
                self.run_once()
                
                # Wait before next iteration
                if iterations is None or iteration < iterations:
                    wait_time = 60  # Check every minute
                    print(f"\n⏸️  Waiting {wait_time}s until next check...")
                    time.sleep(wait_time)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Bot stopped by user")
        except Exception as e:
            print(f"\n\n❌ Bot error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.stop()
    
    def stop(self):
        """Stop the trading bot."""
        self.running = False
        print("\n🛑 Bot stopped")
        self.db.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='WazirX Automated Trading Bot')
    parser.add_argument('--mode', choices=['paper', 'live'], 
                       help='Trading mode (overrides config)')
    parser.add_argument('--iterations', type=int, 
                       help='Number of iterations to run (default: infinite)')
    parser.add_argument('--analyze-only', action='store_true',
                       help='Only run analysis without trading')
    
    args = parser.parse_args()
    
    # Determine paper mode
    paper_mode = None
    if args.mode:
        paper_mode = (args.mode == 'paper')
    
    # Create and run bot
    bot = TradingBot(paper_mode=paper_mode)
    
    if args.analyze_only:
        bot.run_analysis()
    else:
        bot.run(iterations=args.iterations)


if __name__ == "__main__":
    main()
