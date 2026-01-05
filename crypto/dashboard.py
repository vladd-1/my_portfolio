#!/usr/bin/env python3
"""
Simple CLI Dashboard for Monitoring Trading Bot
Displays real-time portfolio status and performance
"""

import time
import os
from datetime import datetime
from database import Database
from config import config


class Dashboard:
    """CLI dashboard for monitoring bot."""
    
    def __init__(self):
        """Initialize dashboard."""
        self.db = Database()
    
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def display_header(self):
        """Display dashboard header."""
        print("=" * 90)
        print("CRYPTO TRADING BOT - LIVE DASHBOARD".center(90))
        print("=" * 90)
        print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(90))
        print(f"Mode: {config.TRADING_MODE.upper()}".center(90))
        print("=" * 90)
    
    def display_portfolio(self):
        """Display portfolio summary."""
        positions = self.db.get_positions()
        balance_history = self.db.get_balance_history(limit=1)
        
        print("\n📊 PORTFOLIO OVERVIEW")
        print("-" * 90)
        
        if balance_history:
            latest = balance_history[0]
            print(f"Total Value:      ${latest['total_value']:>12,.2f}")
            print(f"Cash Balance:     ${latest['cash_balance']:>12,.2f}")
            print(f"Crypto Value:     ${latest['crypto_value']:>12,.2f}")
            print(f"Open Positions:   {latest['num_positions']:>12}")
        else:
            print("No balance data available")
        
        print("\n📈 OPEN POSITIONS")
        print("-" * 90)
        
        if positions:
            print(f"{'Symbol':<12} {'Quantity':<15} {'Avg Entry':<12} {'Current':<12} {'P&L':<15}")
            print("-" * 90)
            
            for pos in positions:
                pnl = pos['unrealized_pnl'] if pos['unrealized_pnl'] else 0
                pnl_sign = '+' if pnl >= 0 else ''
                
                print(f"{pos['symbol']:<12} {pos['quantity']:<15.6f} "
                      f"${pos['avg_entry_price']:<11.2f} "
                      f"${pos['current_price'] if pos['current_price'] else 0:<11.2f} "
                      f"{pnl_sign}${pnl:>10.2f}")
        else:
            print("No open positions")
    
    def display_recent_trades(self, limit=5):
        """Display recent trades."""
        trades = self.db.get_trades(limit=limit)
        
        print(f"\n💼 RECENT TRADES (Last {limit})")
        print("-" * 90)
        
        if trades:
            print(f"{'Time':<20} {'Symbol':<12} {'Side':<6} {'Quantity':<15} {'Price':<12} {'Value':<12}")
            print("-" * 90)
            
            for trade in trades:
                timestamp = datetime.fromisoformat(trade['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                side_emoji = '🟢' if trade['side'] == 'buy' else '🔴'
                
                print(f"{timestamp:<20} {trade['symbol']:<12} {side_emoji} {trade['side']:<4} "
                      f"{trade['quantity']:<15.6f} ${trade['price']:<11.2f} ${trade['value']:<11.2f}")
        else:
            print("No trades yet")
    
    def display_performance(self):
        """Display performance metrics."""
        stats = self.db.get_trade_statistics()
        
        print("\n📈 PERFORMANCE METRICS")
        print("-" * 90)
        print(f"Total Trades:        {stats['total_trades']:>10}")
        print(f"Profitable Trades:   {stats['profitable_trades']:>10}")
        print(f"Win Rate:            {stats['win_rate']:>9.1f}%")
        print(f"Total Volume:        ${stats['total_volume']:>10,.2f}")
        print(f"Total Fees:          ${stats['total_fees']:>10,.2f}")
    
    def display_risk_status(self):
        """Display risk management status."""
        print("\n🛡️  RISK MANAGEMENT")
        print("-" * 90)
        print(f"Max Position Size:   ${config.MAX_POSITION_SIZE:>10,.2f}")
        print(f"Max Daily Volume:    ${config.MAX_DAILY_VOLUME:>10,.2f}")
        print(f"Max Daily Loss:      ${config.MAX_DAILY_LOSS:>10,.2f}")
        print(f"Stop Loss:           {config.STOP_LOSS_PERCENTAGE:>9.1f}%")
        print(f"Max Positions:       {config.MAX_POSITIONS:>10}")
    
    def display_status_log(self, limit=3):
        """Display recent status messages."""
        status_log = self.db.get_status_log(limit=limit)
        
        if status_log:
            print(f"\n📋 STATUS LOG (Last {limit})")
            print("-" * 90)
            
            for entry in status_log:
                timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                status = entry['status']
                message = entry['message'] or ''
                
                print(f"[{timestamp}] {status}: {message}")
    
    def display_controls(self):
        """Display control instructions."""
        print("\n" + "=" * 90)
        print("CONTROLS: Press Ctrl+C to exit | Dashboard refreshes every 10 seconds")
        print("=" * 90)
    
    def refresh(self):
        """Refresh dashboard display."""
        self.clear_screen()
        self.display_header()
        self.display_portfolio()
        self.display_recent_trades(limit=5)
        self.display_performance()
        self.display_risk_status()
        self.display_status_log(limit=3)
        self.display_controls()
    
    def run(self, refresh_interval=10):
        """
        Run dashboard with auto-refresh.
        
        Args:
            refresh_interval: Seconds between refreshes
        """
        print("Starting dashboard...")
        
        try:
            while True:
                self.refresh()
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\n\nDashboard stopped")
        finally:
            self.db.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Bot Dashboard')
    parser.add_argument('--refresh', type=int, default=10,
                       help='Refresh interval in seconds (default: 10)')
    parser.add_argument('--once', action='store_true',
                       help='Display once and exit (no auto-refresh)')
    
    args = parser.parse_args()
    
    dashboard = Dashboard()
    
    if args.once:
        dashboard.refresh()
    else:
        dashboard.run(refresh_interval=args.refresh)


if __name__ == "__main__":
    main()
