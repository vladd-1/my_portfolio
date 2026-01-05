#!/usr/bin/env python3
"""
Cryptocurrency Golden Cross Trading Simulator
Simulates 60 days of crypto price data and implements a Golden Cross trading strategy
No external dependencies required - uses only Python standard library
"""

import random
import math
from datetime import datetime, timedelta
from collections import defaultdict

# Top 10 cryptocurrencies by market cap
CRYPTOCURRENCIES = [
    'Bitcoin', 'Ethereum', 'Binance Coin', 'Cardano', 'Solana',
    'XRP', 'Polkadot', 'Dogecoin', 'Avalanche', 'Polygon'
]

# Initial prices (approximate as of 2024)
INITIAL_PRICES = {
    'Bitcoin': 45000,
    'Ethereum': 2500,
    'Binance Coin': 320,
    'Cardano': 0.50,
    'Solana': 100,
    'XRP': 0.60,
    'Polkadot': 7.5,
    'Dogecoin': 0.08,
    'Avalanche': 38,
    'Polygon': 0.85
}

# Volatility parameters (daily volatility as percentage)
VOLATILITY = {
    'Bitcoin': 0.03,
    'Ethereum': 0.04,
    'Binance Coin': 0.045,
    'Cardano': 0.05,
    'Solana': 0.06,
    'XRP': 0.055,
    'Polkadot': 0.05,
    'Dogecoin': 0.07,
    'Avalanche': 0.055,
    'Polygon': 0.06
}

# Drift (expected daily return)
DRIFT = {
    'Bitcoin': 0.001,
    'Ethereum': 0.0015,
    'Binance Coin': 0.0012,
    'Cardano': 0.0008,
    'Solana': 0.002,
    'XRP': 0.0005,
    'Polkadot': 0.001,
    'Dogecoin': 0.0003,
    'Avalanche': 0.0015,
    'Polygon': 0.0018
}


def normal_random():
    """Generate a random number from standard normal distribution using Box-Muller transform."""
    u1 = random.random()
    u2 = random.random()
    return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


def moving_average(prices, window):
    """Calculate moving average for a list of prices."""
    if len(prices) < window:
        return sum(prices) / len(prices) if prices else 0
    return sum(prices[-window:]) / window


def generate_price_data(crypto, days=60):
    """
    Generate realistic cryptocurrency price data using Geometric Brownian Motion.
    
    Returns: List of dictionaries with Date and Price
    """
    random.seed(hash(crypto) % 2**32)  # Different seed for each crypto
    
    initial_price = INITIAL_PRICES[crypto]
    volatility = VOLATILITY[crypto]
    drift = DRIFT[crypto]
    
    data = []
    price = initial_price
    start_date = datetime.now() - timedelta(days=days-1)
    
    for i in range(days):
        date = start_date + timedelta(days=i)
        data.append({'Date': date, 'Price': price})
        
        # Generate next price using Geometric Brownian Motion
        if i < days - 1:
            random_shock = normal_random()
            daily_return = drift + volatility * random_shock
            price = price * (1 + daily_return)
    
    return data


def calculate_moving_averages(data):
    """Calculate 7-day and 30-day moving averages."""
    prices = [d['Price'] for d in data]
    
    for i, record in enumerate(data):
        # Calculate MA7
        if i < 7:
            record['MA7'] = sum(prices[:i+1]) / (i+1)
        else:
            record['MA7'] = sum(prices[i-6:i+1]) / 7
        
        # Calculate MA30
        if i < 30:
            record['MA30'] = sum(prices[:i+1]) / (i+1)
        else:
            record['MA30'] = sum(prices[i-29:i+1]) / 30
    
    return data


def golden_cross_strategy(data, initial_capital=10000):
    """
    Implement Golden Cross trading strategy.
    
    Golden Cross: Buy when MA7 crosses above MA30 (bullish signal)
    Death Cross: Sell when MA7 crosses below MA30 (bearish signal)
    """
    trades = []
    cash = initial_capital
    holdings = 0.0
    position = 0  # 0: No position, 1: Holding
    
    for i in range(len(data)):
        record = data[i]
        record['Signal'] = 'HOLD'
        record['Position'] = position
        
        if i > 0:
            prev = data[i-1]
            
            # Check for Golden Cross (MA7 crosses above MA30)
            if prev['MA7'] <= prev['MA30'] and record['MA7'] > record['MA30']:
                if position == 0:  # Not holding, so buy
                    record['Signal'] = 'BUY'
                    holdings = cash / record['Price']
                    trades.append({
                        'Date': record['Date'],
                        'Action': 'BUY',
                        'Price': record['Price'],
                        'Amount': holdings,
                        'Value': cash
                    })
                    cash = 0
                    position = 1
            
            # Check for Death Cross (MA7 crosses below MA30)
            elif prev['MA7'] >= prev['MA30'] and record['MA7'] < record['MA30']:
                if position == 1:  # Holding, so sell
                    record['Signal'] = 'SELL'
                    cash = holdings * record['Price']
                    trades.append({
                        'Date': record['Date'],
                        'Action': 'SELL',
                        'Price': record['Price'],
                        'Amount': holdings,
                        'Value': cash
                    })
                    holdings = 0
                    position = 0
        
        record['Cash'] = cash
        record['Holdings'] = holdings
        record['Portfolio_Value'] = cash + (holdings * record['Price'])
        record['Position'] = position
    
    return data, trades


def print_daily_ledger(crypto, data, trades):
    """Print daily trading ledger for a cryptocurrency."""
    print(f"\n{'='*80}")
    print(f"DAILY LEDGER FOR {crypto.upper()}")
    print(f"{'='*80}")
    print(f"{'Date':<12} {'Price':<12} {'MA7':<12} {'MA30':<12} {'Signal':<8} {'Portfolio':<12}")
    print(f"{'-'*80}")
    
    for record in data:
        print(f"{record['Date'].strftime('%Y-%m-%d'):<12} "
              f"${record['Price']:>10.2f} "
              f"${record['MA7']:>10.2f} "
              f"${record['MA30']:>10.2f} "
              f"{record['Signal']:<8} "
              f"${record['Portfolio_Value']:>10.2f}")
    
    print(f"\n{'TRADES EXECUTED':^80}")
    print(f"{'-'*80}")
    if trades:
        for trade in trades:
            print(f"{trade['Date'].strftime('%Y-%m-%d')}: {trade['Action']:<4} "
                  f"{trade['Amount']:.4f} units @ ${trade['Price']:.2f} "
                  f"= ${trade['Value']:.2f}")
    else:
        print("No trades executed (no Golden Cross signals detected)")


def main():
    """Main function to run the crypto trading simulation."""
    print("="*80)
    print("CRYPTOCURRENCY GOLDEN CROSS TRADING SIMULATOR")
    print("="*80)
    print(f"\nSimulating 60 days of price data for top 10 cryptocurrencies...")
    print(f"Initial Capital per Crypto: $10,000")
    print(f"Strategy: Golden Cross (MA7 crosses above MA30 = BUY, MA7 crosses below MA30 = SELL)")
    
    results = {}
    
    for crypto in CRYPTOCURRENCIES:
        print(f"\n\nProcessing {crypto}...")
        
        # Generate price data
        data = generate_price_data(crypto, days=60)
        
        # Calculate moving averages
        data = calculate_moving_averages(data)
        
        # Apply Golden Cross strategy
        data, trades = golden_cross_strategy(data, initial_capital=10000)
        
        # Print daily ledger
        print_daily_ledger(crypto, data, trades)
        
        # Store results
        initial_value = 10000
        final_value = data[-1]['Portfolio_Value']
        profit = final_value - initial_value
        profit_pct = (profit / initial_value) * 100
        
        results[crypto] = {
            'Initial': initial_value,
            'Final': final_value,
            'Profit': profit,
            'Profit_Pct': profit_pct,
            'Trades': len(trades)
        }
    
    # Print final summary
    print("\n\n" + "="*80)
    print("FINAL PORTFOLIO PERFORMANCE SUMMARY")
    print("="*80)
    print(f"{'Cryptocurrency':<20} {'Initial':<12} {'Final':<12} {'Profit':<12} {'Return %':<10} {'Trades':<8}")
    print("-"*80)
    
    # Sort by profit percentage
    sorted_results = sorted(results.items(), key=lambda x: x[1]['Profit_Pct'], reverse=True)
    
    total_initial = 0
    total_final = 0
    
    for crypto, stats in sorted_results:
        print(f"{crypto:<20} "
              f"${stats['Initial']:>10.2f} "
              f"${stats['Final']:>10.2f} "
              f"${stats['Profit']:>10.2f} "
              f"{stats['Profit_Pct']:>8.2f}% "
              f"{stats['Trades']:>6}")
        total_initial += stats['Initial']
        total_final += stats['Final']
    
    print("-"*80)
    total_profit = total_final - total_initial
    total_return = (total_profit / total_initial) * 100
    
    print(f"{'TOTAL PORTFOLIO':<20} "
          f"${total_initial:>10.2f} "
          f"${total_final:>10.2f} "
          f"${total_profit:>10.2f} "
          f"{total_return:>8.2f}%")
    
    print("\n" + "="*80)
    print("SIMULATION COMPLETE")
    print("="*80)
    
    # Additional insights
    print("\nKEY INSIGHTS:")
    print(f"- Best Performer: {sorted_results[0][0]} with {sorted_results[0][1]['Profit_Pct']:.2f}% return")
    print(f"- Worst Performer: {sorted_results[-1][0]} with {sorted_results[-1][1]['Profit_Pct']:.2f}% return")
    print(f"- Average Return: {sum(r[1]['Profit_Pct'] for r in sorted_results) / len(sorted_results):.2f}%")
    print(f"- Total Trades Executed: {sum(r[1]['Trades'] for r in sorted_results)}")
    
    print("\nNOTE: This simulation uses Geometric Brownian Motion to model realistic price movements.")
    print("Past performance does not guarantee future results. This is for educational purposes only.")


if __name__ == "__main__":
    main()
