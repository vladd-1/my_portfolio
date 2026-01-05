"""
Portfolio Tracker for Crypto Trading Bot
Tracks positions, calculates P&L, and monitors performance
"""

from datetime import datetime
from typing import Dict, List, Optional
from database import Database
from config import config


class PortfolioTracker:
    """Tracks portfolio state and performance."""
    
    def __init__(self, db: Database, initial_capital: float = 10000):
        """
        Initialize portfolio tracker.
        
        Args:
            db: Database instance
            initial_capital: Starting capital in USD
        """
        self.db = db
        self.initial_capital = initial_capital
        self.cash_balance = initial_capital
        self.positions: Dict[str, Dict] = {}  # symbol -> position info
        self.total_fees_paid = 0.0
        
    def update_cash_balance(self, amount: float):
        """
        Update cash balance.
        
        Args:
            amount: Amount to add (positive) or subtract (negative)
        """
        self.cash_balance += amount
    
    def record_buy(self, symbol: str, quantity: float, price: float, fee: float = 0.0):
        """
        Record a buy transaction.
        
        Args:
            symbol: Trading pair
            quantity: Quantity bought
            price: Purchase price
            fee: Trading fee
        """
        cost = (quantity * price) + fee
        
        # Update cash
        self.cash_balance -= cost
        self.total_fees_paid += fee
        
        # Update position
        if symbol in self.positions:
            pos = self.positions[symbol]
            total_qty = pos['quantity'] + quantity
            avg_price = ((pos['quantity'] * pos['avg_price']) + (quantity * price)) / total_qty
            pos['quantity'] = total_qty
            pos['avg_price'] = avg_price
        else:
            self.positions[symbol] = {
                'quantity': quantity,
                'avg_price': price,
                'entry_time': datetime.now()
            }
        
        # Save to database
        self.db.insert_trade(symbol, 'buy', quantity, price, quantity * price, fee)
        self.db.upsert_position(symbol, self.positions[symbol]['quantity'], 
                               self.positions[symbol]['avg_price'], price)
        
        print(f"✅ BUY: {quantity:.6f} {symbol} @ ${price:.2f} (Fee: ${fee:.2f})")
    
    def record_sell(self, symbol: str, quantity: float, price: float, fee: float = 0.0):
        """
        Record a sell transaction.
        
        Args:
            symbol: Trading pair
            quantity: Quantity sold
            price: Sale price
            fee: Trading fee
        """
        proceeds = (quantity * price) - fee
        
        # Update cash
        self.cash_balance += proceeds
        self.total_fees_paid += fee
        
        # Update position
        if symbol in self.positions:
            pos = self.positions[symbol]
            
            # Calculate realized P&L
            realized_pnl = (price - pos['avg_price']) * quantity - fee
            
            # Update quantity
            pos['quantity'] -= quantity
            
            # Remove position if fully closed
            if pos['quantity'] <= 0.0001:
                del self.positions[symbol]
                self.db.delete_position(symbol)
            else:
                self.db.upsert_position(symbol, pos['quantity'], pos['avg_price'], price)
        
        # Save to database
        self.db.insert_trade(symbol, 'sell', quantity, price, quantity * price, fee)
        
        print(f"✅ SELL: {quantity:.6f} {symbol} @ ${price:.2f} (Fee: ${fee:.2f})")
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position for a symbol."""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Dict]:
        """Get all positions."""
        return self.positions.copy()
    
    def calculate_position_value(self, symbol: str, current_price: float) -> float:
        """
        Calculate current value of a position.
        
        Args:
            symbol: Trading pair
            current_price: Current market price
            
        Returns:
            Position value in USD
        """
        if symbol not in self.positions:
            return 0.0
        
        return self.positions[symbol]['quantity'] * current_price
    
    def calculate_position_pnl(self, symbol: str, current_price: float) -> Dict:
        """
        Calculate P&L for a position.
        
        Args:
            symbol: Trading pair
            current_price: Current market price
            
        Returns:
            Dict with unrealized_pnl, unrealized_pnl_pct, current_value
        """
        if symbol not in self.positions:
            return {'unrealized_pnl': 0, 'unrealized_pnl_pct': 0, 'current_value': 0}
        
        pos = self.positions[symbol]
        current_value = pos['quantity'] * current_price
        cost_basis = pos['quantity'] * pos['avg_price']
        unrealized_pnl = current_value - cost_basis
        unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        return {
            'unrealized_pnl': unrealized_pnl,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'current_value': current_value,
            'cost_basis': cost_basis
        }
    
    def calculate_total_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value.
        
        Args:
            current_prices: Dict of symbol -> current price
            
        Returns:
            Total portfolio value in USD
        """
        crypto_value = sum(
            self.calculate_position_value(symbol, current_prices.get(symbol, 0))
            for symbol in self.positions
        )
        
        return self.cash_balance + crypto_value
    
    def calculate_total_pnl(self, current_prices: Dict[str, float]) -> Dict:
        """
        Calculate total portfolio P&L.
        
        Args:
            current_prices: Dict of symbol -> current price
            
        Returns:
            Dict with total_value, total_pnl, total_pnl_pct, crypto_value
        """
        crypto_value = 0.0
        unrealized_pnl = 0.0
        
        for symbol in self.positions:
            current_price = current_prices.get(symbol, 0)
            pnl_data = self.calculate_position_pnl(symbol, current_price)
            crypto_value += pnl_data['current_value']
            unrealized_pnl += pnl_data['unrealized_pnl']
        
        total_value = self.cash_balance + crypto_value
        total_pnl = total_value - self.initial_capital
        total_pnl_pct = (total_pnl / self.initial_capital * 100) if self.initial_capital > 0 else 0
        
        return {
            'total_value': total_value,
            'cash_balance': self.cash_balance,
            'crypto_value': crypto_value,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'total_fees_paid': self.total_fees_paid
        }
    
    def save_snapshot(self, current_prices: Dict[str, float]):
        """
        Save portfolio snapshot to database.
        
        Args:
            current_prices: Dict of symbol -> current price
        """
        pnl_data = self.calculate_total_pnl(current_prices)
        
        self.db.insert_balance_snapshot(
            total_value=pnl_data['total_value'],
            cash_balance=pnl_data['cash_balance'],
            crypto_value=pnl_data['crypto_value'],
            num_positions=len(self.positions)
        )
    
    def print_portfolio_summary(self, current_prices: Dict[str, float]):
        """
        Print portfolio summary.
        
        Args:
            current_prices: Dict of symbol -> current price
        """
        pnl_data = self.calculate_total_pnl(current_prices)
        
        print("\n" + "=" * 80)
        print("PORTFOLIO SUMMARY")
        print("=" * 80)
        
        print(f"\n💰 Account Value:")
        print(f"   Total Value:      ${pnl_data['total_value']:,.2f}")
        print(f"   Cash Balance:     ${pnl_data['cash_balance']:,.2f}")
        print(f"   Crypto Value:     ${pnl_data['crypto_value']:,.2f}")
        
        print(f"\n📊 Performance:")
        print(f"   Initial Capital:  ${self.initial_capital:,.2f}")
        pnl_sign = "+" if pnl_data['total_pnl'] >= 0 else ""
        print(f"   Total P&L:        {pnl_sign}${pnl_data['total_pnl']:,.2f} ({pnl_sign}{pnl_data['total_pnl_pct']:.2f}%)")
        print(f"   Unrealized P&L:   {pnl_sign}${pnl_data['unrealized_pnl']:,.2f}")
        print(f"   Total Fees:       ${pnl_data['total_fees_paid']:,.2f}")
        
        print(f"\n📈 Positions ({len(self.positions)}):")
        
        if self.positions:
            print(f"   {'Symbol':<12} {'Quantity':<15} {'Avg Price':<12} {'Current':<12} {'Value':<12} {'P&L':<12}")
            print("   " + "-" * 75)
            
            for symbol, pos in self.positions.items():
                current_price = current_prices.get(symbol, 0)
                pnl = self.calculate_position_pnl(symbol, current_price)
                pnl_sign = "+" if pnl['unrealized_pnl'] >= 0 else ""
                
                print(f"   {symbol:<12} {pos['quantity']:<15.6f} "
                      f"${pos['avg_price']:<11.2f} ${current_price:<11.2f} "
                      f"${pnl['current_value']:<11.2f} "
                      f"{pnl_sign}${pnl['unrealized_pnl']:.2f} ({pnl_sign}{pnl['unrealized_pnl_pct']:.1f}%)")
        else:
            print("   No open positions")
        
        print("=" * 80)
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics.
        
        Returns:
            Dict with various performance metrics
        """
        stats = self.db.get_trade_statistics()
        
        return {
            'total_trades': stats['total_trades'],
            'win_rate': stats['win_rate'],
            'total_fees': self.total_fees_paid,
            'num_positions': len(self.positions)
        }


if __name__ == "__main__":
    # Test portfolio tracker
    print("Portfolio Tracker Test")
    print("=" * 80)
    
    db = Database('test_trading_bot.db')
    portfolio = PortfolioTracker(db, initial_capital=10000)
    
    # Simulate some trades
    portfolio.record_buy('btcinr', 0.1, 45000, fee=5.0)
    portfolio.record_buy('ethinr', 1.0, 2500, fee=2.5)
    
    # Print summary
    current_prices = {'btcinr': 46000, 'ethinr': 2600}
    portfolio.print_portfolio_summary(current_prices)
    
    db.close()
