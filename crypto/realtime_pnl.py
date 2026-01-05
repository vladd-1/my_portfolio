#!/usr/bin/env python3
"""
Real-time Portfolio P&L Calculator
Fetches current prices and calculates actual profit/loss
"""

from database import Database
from market_data import MarketDataFetcher
from datetime import datetime


def calculate_realtime_pnl():
    """Calculate real-time P&L with current market prices."""
    
    print("=" * 80)
    print("REAL-TIME PORTFOLIO P&L CALCULATOR")
    print("=" * 80)
    print(f"\nUpdated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize
    db = Database()
    market_data = MarketDataFetcher(use_live_data=True)
    
    # Get all positions from database
    positions = db.get_positions()
    
    if not positions:
        print("❌ No positions found in database")
        return
    
    print(f"📊 Fetching real-time prices for {len(positions)} positions...\n")
    
    # Fetch all current prices at once
    all_prices = market_data.get_all_tickers()
    
    total_cost_basis = 0
    total_current_value = 0
    position_details = []
    
    for pos in positions:
        symbol = pos['symbol']
        quantity = pos['quantity']
        avg_entry = pos['avg_entry_price']
        
        # Get current price
        current_price = all_prices.get(symbol, avg_entry)
        
        # Calculate values
        cost_basis = quantity * avg_entry
        current_value = quantity * current_price
        pnl = current_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        total_cost_basis += cost_basis
        total_current_value += current_value
        
        position_details.append({
            'symbol': symbol,
            'quantity': quantity,
            'avg_entry': avg_entry,
            'current_price': current_price,
            'cost_basis': cost_basis,
            'current_value': current_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct
        })
    
    # Get balance history for initial capital
    balance_history = db.get_balance_history(limit=1)
    initial_capital = 10000  # Default
    cash_balance = 9499  # From last known state
    
    if balance_history:
        cash_balance = balance_history[0]['cash_balance']
    
    # Calculate totals
    total_portfolio_value = cash_balance + total_current_value
    total_pnl = total_current_value - total_cost_basis
    total_pnl_pct = (total_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0
    overall_return = ((total_portfolio_value - initial_capital) / initial_capital * 100)
    
    # Display results
    print("=" * 80)
    print("💰 PORTFOLIO SUMMARY (REAL-TIME PRICES)")
    print("=" * 80)
    
    print(f"\n📊 Account Overview:")
    print(f"   Initial Capital:      ${initial_capital:,.2f}")
    print(f"   Cash Balance:         ${cash_balance:,.2f}")
    print(f"   Crypto Value:         ${total_current_value:,.2f}")
    print(f"   Total Portfolio:      ${total_portfolio_value:,.2f}")
    
    pnl_sign = "+" if total_pnl >= 0 else ""
    pnl_emoji = "🟢" if total_pnl >= 0 else "🔴"
    
    print(f"\n{pnl_emoji} Performance:")
    print(f"   Cost Basis:           ${total_cost_basis:,.2f}")
    print(f"   Current Value:        ${total_current_value:,.2f}")
    print(f"   Unrealized P&L:       {pnl_sign}${total_pnl:,.2f} ({pnl_sign}{total_pnl_pct:.2f}%)")
    print(f"   Overall Return:       {pnl_sign}{overall_return:.2f}%")
    
    # Position details
    print(f"\n📈 POSITIONS ({len(position_details)}) - SORTED BY P&L")
    print("=" * 80)
    print(f"{'Symbol':<12} {'Quantity':<15} {'Entry':<12} {'Current':<12} {'P&L':<15} {'%':<10}")
    print("-" * 80)
    
    # Sort by P&L
    position_details.sort(key=lambda x: x['pnl'], reverse=True)
    
    for pos in position_details:
        pnl_sign = "+" if pos['pnl'] >= 0 else ""
        pnl_color = "🟢" if pos['pnl'] >= 0 else "🔴"
        
        print(f"{pos['symbol']:<12} {pos['quantity']:<15.6f} "
              f"${pos['avg_entry']:<11.2f} ${pos['current_price']:<11.2f} "
              f"{pnl_color} {pnl_sign}${pos['pnl']:<10.2f} {pnl_sign}{pos['pnl_pct']:.2f}%")
    
    # Winners and losers
    winners = [p for p in position_details if p['pnl'] > 0]
    losers = [p for p in position_details if p['pnl'] < 0]
    
    print("\n" + "=" * 80)
    print("📊 STATISTICS")
    print("=" * 80)
    print(f"   Winning Positions:    {len(winners)}")
    print(f"   Losing Positions:     {len(losers)}")
    print(f"   Break-even:           {len(position_details) - len(winners) - len(losers)}")
    
    if winners:
        best = max(winners, key=lambda x: x['pnl_pct'])
        print(f"   Best Performer:       {best['symbol']} (+{best['pnl_pct']:.2f}%)")
    
    if losers:
        worst = min(losers, key=lambda x: x['pnl_pct'])
        print(f"   Worst Performer:      {worst['symbol']} ({worst['pnl_pct']:.2f}%)")
    
    print("\n" + "=" * 80)
    
    db.close()


if __name__ == "__main__":
    try:
        calculate_realtime_pnl()
    except KeyboardInterrupt:
        print("\n\nCalculation stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
