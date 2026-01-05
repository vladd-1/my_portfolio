#!/usr/bin/env python3
"""
Comprehensive Cryptocurrency Profit Maximizer
Analyzes 50+ cryptocurrencies and recommends the top 10 for maximum profit
"""

import random
import math
from datetime import datetime, timedelta

# Comprehensive list of top 50+ cryptocurrencies
CRYPTOCURRENCIES = {
    # Top 10 by market cap
    'Bitcoin': {'price': 45000, 'volatility': 0.03, 'drift': 0.0012},
    'Ethereum': {'price': 2500, 'volatility': 0.04, 'drift': 0.0018},
    'Binance Coin': {'price': 320, 'volatility': 0.045, 'drift': 0.0015},
    'Solana': {'price': 100, 'volatility': 0.06, 'drift': 0.0025},
    'XRP': {'price': 0.60, 'volatility': 0.055, 'drift': 0.0008},
    'Cardano': {'price': 0.50, 'volatility': 0.05, 'drift': 0.0010},
    'Avalanche': {'price': 38, 'volatility': 0.055, 'drift': 0.0020},
    'Dogecoin': {'price': 0.08, 'volatility': 0.07, 'drift': 0.0005},
    'Polkadot': {'price': 7.5, 'volatility': 0.05, 'drift': 0.0012},
    'Polygon': {'price': 0.85, 'volatility': 0.06, 'drift': 0.0022},
    
    # 11-20
    'Chainlink': {'price': 15, 'volatility': 0.055, 'drift': 0.0018},
    'Litecoin': {'price': 75, 'volatility': 0.045, 'drift': 0.0010},
    'Uniswap': {'price': 6.5, 'volatility': 0.06, 'drift': 0.0020},
    'Stellar': {'price': 0.12, 'volatility': 0.05, 'drift': 0.0008},
    'VeChain': {'price': 0.025, 'volatility': 0.065, 'drift': 0.0015},
    'Cosmos': {'price': 10, 'volatility': 0.055, 'drift': 0.0016},
    'Algorand': {'price': 0.18, 'volatility': 0.06, 'drift': 0.0018},
    'Tron': {'price': 0.10, 'volatility': 0.05, 'drift': 0.0010},
    'Monero': {'price': 160, 'volatility': 0.045, 'drift': 0.0012},
    'EOS': {'price': 0.70, 'volatility': 0.055, 'drift': 0.0008},
    
    # 21-30
    'Filecoin': {'price': 5.5, 'volatility': 0.07, 'drift': 0.0022},
    'Hedera': {'price': 0.08, 'volatility': 0.06, 'drift': 0.0015},
    'Aptos': {'price': 8, 'volatility': 0.08, 'drift': 0.0030},
    'Near Protocol': {'price': 3.5, 'volatility': 0.065, 'drift': 0.0020},
    'Arbitrum': {'price': 1.2, 'volatility': 0.07, 'drift': 0.0025},
    'Optimism': {'price': 2.5, 'volatility': 0.07, 'drift': 0.0024},
    'Sui': {'price': 1.5, 'volatility': 0.09, 'drift': 0.0035},
    'Injective': {'price': 25, 'volatility': 0.08, 'drift': 0.0028},
    'Render': {'price': 7, 'volatility': 0.075, 'drift': 0.0026},
    'The Graph': {'price': 0.15, 'volatility': 0.065, 'drift': 0.0018},
    
    # 31-40
    'Kaspa': {'price': 0.12, 'volatility': 0.10, 'drift': 0.0040},
    'Immutable': {'price': 2, 'volatility': 0.08, 'drift': 0.0027},
    'Stacks': {'price': 1.5, 'volatility': 0.075, 'drift': 0.0023},
    'Sei': {'price': 0.50, 'volatility': 0.09, 'drift': 0.0032},
    'Celestia': {'price': 8, 'volatility': 0.085, 'drift': 0.0030},
    'Fantom': {'price': 0.45, 'volatility': 0.07, 'drift': 0.0020},
    'Theta': {'price': 1.2, 'volatility': 0.065, 'drift': 0.0016},
    'Axie Infinity': {'price': 7, 'volatility': 0.08, 'drift': 0.0022},
    'Flow': {'price': 0.80, 'volatility': 0.07, 'drift': 0.0018},
    'Sandbox': {'price': 0.50, 'volatility': 0.075, 'drift': 0.0021},
    
    # 41-50
    'Mina': {'price': 0.70, 'volatility': 0.07, 'drift': 0.0019},
    'Aave': {'price': 95, 'volatility': 0.06, 'drift': 0.0020},
    'Maker': {'price': 1500, 'volatility': 0.055, 'drift': 0.0016},
    'Quant': {'price': 110, 'volatility': 0.065, 'drift': 0.0021},
    'Lido DAO': {'price': 2.2, 'volatility': 0.07, 'drift': 0.0023},
    'Pepe': {'price': 0.000001, 'volatility': 0.12, 'drift': 0.0045},
    'Bonk': {'price': 0.00001, 'volatility': 0.11, 'drift': 0.0042},
    'Floki': {'price': 0.00005, 'volatility': 0.10, 'drift': 0.0038},
    'Shiba Inu': {'price': 0.00001, 'volatility': 0.09, 'drift': 0.0035},
    'Worldcoin': {'price': 3.5, 'volatility': 0.085, 'drift': 0.0029},
}


def normal_random():
    """Generate standard normal random number."""
    u1 = random.random()
    u2 = random.random()
    return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)


def simulate_30_day_returns(crypto, params, simulations=2000):
    """Run Monte Carlo simulation for 30-day returns."""
    random.seed(hash(crypto) % 2**32)
    
    initial_price = params['price']
    volatility = params['volatility']
    drift = params['drift']
    
    final_returns = []
    
    for _ in range(simulations):
        price = initial_price
        
        for day in range(30):
            random_shock = normal_random()
            daily_return = drift + volatility * random_shock
            price = price * (1 + daily_return)
        
        return_pct = ((price - initial_price) / initial_price) * 100
        final_returns.append(return_pct)
    
    # Calculate statistics
    avg_return = sum(final_returns) / len(final_returns)
    sorted_returns = sorted(final_returns)
    
    # Percentiles
    p10 = sorted_returns[int(len(sorted_returns) * 0.10)]
    p25 = sorted_returns[int(len(sorted_returns) * 0.25)]
    p50 = sorted_returns[int(len(sorted_returns) * 0.50)]
    p75 = sorted_returns[int(len(sorted_returns) * 0.75)]
    p90 = sorted_returns[int(len(sorted_returns) * 0.90)]
    
    # Risk metrics
    losses = [r for r in final_returns if r < 0]
    prob_loss = len(losses) / len(final_returns) * 100
    
    # Standard deviation
    variance = sum((r - avg_return)**2 for r in final_returns) / len(final_returns)
    std_dev = math.sqrt(variance)
    
    # Sharpe ratio (assuming 0% risk-free rate)
    sharpe = avg_return / std_dev if std_dev > 0 else 0
    
    # Sortino ratio (downside deviation)
    downside_returns = [r for r in final_returns if r < 0]
    if downside_returns:
        downside_variance = sum(r**2 for r in downside_returns) / len(downside_returns)
        downside_dev = math.sqrt(downside_variance)
        sortino = avg_return / downside_dev if downside_dev > 0 else 0
    else:
        sortino = float('inf') if avg_return > 0 else 0
    
    # Maximum drawdown potential
    max_loss = min(final_returns)
    
    return {
        'avg_return': avg_return,
        'median_return': p50,
        'p10': p10,
        'p25': p25,
        'p75': p75,
        'p90': p90,
        'volatility': std_dev,
        'prob_loss': prob_loss,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_loss': max_loss,
        'upside_potential': p90,
        'downside_risk': p10
    }


def calculate_profit_score(crypto, params, stats):
    """
    Calculate comprehensive profit maximization score.
    
    Factors:
    - Expected Return (35%)
    - Upside Potential (25%)
    - Risk-Adjusted Return/Sortino (20%)
    - Low Downside Risk (15%)
    - Sharpe Ratio (5%)
    """
    # Normalize scores
    return_score = min(max(stats['avg_return'] * 3, 0), 100)
    upside_score = min(max(stats['p90'] * 2, 0), 100)
    sortino_score = min(max(stats['sortino_ratio'] * 15, 0), 100)
    downside_score = max(100 + stats['p10'], 0)  # Less negative is better
    sharpe_score = min(max(stats['sharpe_ratio'] * 25, 0), 100)
    
    # Weighted composite score
    profit_score = (
        return_score * 0.35 +
        upside_score * 0.25 +
        sortino_score * 0.20 +
        downside_score * 0.15 +
        sharpe_score * 0.05
    )
    
    return profit_score


def get_top_recommendations(top_n: int = 10, silent: bool = False):
    """
    Get top N cryptocurrency recommendations for automated trading.
    
    Args:
        top_n: Number of top recommendations to return
        silent: If True, suppress console output
        
    Returns:
        List of dicts with crypto recommendations and allocations
    """
    if not silent:
        print("="*100)
        print("COMPREHENSIVE CRYPTOCURRENCY PROFIT MAXIMIZER")
        print("="*100)
        print(f"\n🔍 Analyzing {len(CRYPTOCURRENCIES)} cryptocurrencies...")
        print("📊 Running 2,000 Monte Carlo simulations per coin...")
        print("🎯 Optimizing for maximum 30-day profit potential...\n")
    
    results = []
    
    for i, (crypto, params) in enumerate(CRYPTOCURRENCIES.items(), 1):
        if not silent:
            print(f"[{i:2d}/{len(CRYPTOCURRENCIES)}] Analyzing {crypto:<20}", end=" ")
        
        # Run simulation
        stats = simulate_30_day_returns(crypto, params, simulations=2000)
        
        # Calculate profit score
        score = calculate_profit_score(crypto, params, stats)
        
        results.append({
            'crypto': crypto,
            'score': score,
            'price': params['price'],
            'volatility_param': params['volatility'],
            'drift_param': params['drift'],
            **stats
        })
        
        if not silent:
            print("✓")
    
    # Sort by profit score
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Get top N
    top_results = results[:top_n]
    
    # Calculate allocations based on scores
    total_score = sum(r['score'] for r in top_results)
    
    for r in top_results:
        r['allocation_pct'] = (r['score'] / total_score) * 100
    
    return top_results


def main():
    """Main analysis function."""
    results = get_top_recommendations(top_n=10, silent=False)
    
    # Display top 10
    print("\n" + "="*100)
    print("🏆 TOP 10 CRYPTOCURRENCIES FOR MAXIMUM PROFIT (30-DAY HOLD)")
    print("="*100)
    print(f"\n{'Rank':<6} {'Crypto':<20} {'Score':<8} {'Expected':<11} {'Upside':<11} {'Downside':<11} {'Risk':<8}")
    print(f"{'':6} {'':20} {'':8} {'Return':<11} {'(90th %)':<11} {'(10th %)':<11} {'Loss %':<8}")
    print("-"*100)
    
    for i, r in enumerate(results[:10], 1):
        emoji = "🚀" if r['avg_return'] > 5 else "📈" if r['avg_return'] > 2 else "📊"
        print(f"{i:<6} {emoji} {r['crypto']:<18} {r['score']:>6.1f}  "
              f"{r['avg_return']:>9.2f}%  "
              f"{r['p90']:>9.2f}%  "
              f"{r['p10']:>9.2f}%  "
              f"{r['prob_loss']:>6.1f}%")
    
    # Detailed analysis
    print("\n" + "="*100)
    print("📋 DETAILED ANALYSIS - TOP 10 PROFIT MAXIMIZERS")
    print("="*100)
    
    for i, r in enumerate(results[:10], 1):
        print(f"\n{i}. {r['crypto'].upper()}")
        print(f"   {'─'*95}")
        print(f"   Current Price:        ${r['price']:,.6f}")
        print(f"   Profit Score:         {r['score']:.1f}/100")
        print(f"   Expected Return:      {r['avg_return']:+.2f}% (30 days)")
        print(f"   Median Return:        {r['median_return']:+.2f}%")
        print(f"   Upside (90th %ile):   {r['p90']:+.2f}%")
        print(f"   Downside (10th %ile): {r['p10']:+.2f}%")
        print(f"   Best Case Scenario:   {r['upside_potential']:+.2f}%")
        print(f"   Worst Case Scenario:  {r['max_loss']:+.2f}%")
        print(f"   Volatility:           {r['volatility']:.2f}%")
        print(f"   Probability of Loss:  {r['prob_loss']:.1f}%")
        print(f"   Sharpe Ratio:         {r['sharpe_ratio']:.3f}")
        print(f"   Sortino Ratio:        {r['sortino_ratio']:.3f}")
        
        # Recommendation
        if r['avg_return'] > 8:
            rec = "🚀 VERY STRONG BUY - Exceptional profit potential"
        elif r['avg_return'] > 5:
            rec = "🚀 STRONG BUY - High profit potential"
        elif r['avg_return'] > 3:
            rec = "📈 BUY - Good profit potential"
        elif r['avg_return'] > 1:
            rec = "📊 MODERATE BUY - Decent profit potential"
        else:
            rec = "⚠️  HOLD - Limited profit potential"
        
        print(f"   Recommendation:       {rec}")
    
    # Portfolio allocation
    print("\n" + "="*100)
    print("💰 OPTIMIZED PORTFOLIO ALLOCATION (for $10,000 investment)")
    print("="*100)
    
    # Weighted allocation based on scores
    top_10 = results[:10]
    total_score = sum(r['score'] for r in top_10)
    
    print(f"\n{'Rank':<6} {'Cryptocurrency':<25} {'Allocation':<12} {'Amount':<12} {'Expected':<15}")
    print(f"{'':6} {'':25} {'':12} {'':12} {'Value (30d)':<15}")
    print("-"*100)
    
    total_investment = 10000
    total_expected = 0
    
    for i, r in enumerate(top_10, 1):
        # Allocation proportional to score
        allocation_pct = (r['score'] / total_score) * 100
        amount = total_investment * (allocation_pct / 100)
        expected_value = amount * (1 + r['avg_return'] / 100)
        total_expected += expected_value
        
        print(f"{i:<6} {r['crypto']:<25} {allocation_pct:>5.1f}%        "
              f"${amount:>9.2f}  ${expected_value:>12.2f}")
    
    total_profit = total_expected - total_investment
    total_return = (total_profit / total_investment) * 100
    
    print("-"*100)
    print(f"{'TOTAL PORTFOLIO':<31} {'100.0%':<12} ${total_investment:>9.2f}  ${total_expected:>12.2f}")
    print(f"\n💵 Expected Profit:  ${total_profit:,.2f}")
    print(f"📊 Expected Return:  {total_return:+.2f}%")
    print(f"⏱️  Time Horizon:    30 days")
    
    # Risk analysis
    print("\n" + "="*100)
    print("⚠️  PORTFOLIO RISK ANALYSIS")
    print("="*100)
    
    avg_prob_loss = sum(r['prob_loss'] for r in top_10) / len(top_10)
    avg_sharpe = sum(r['sharpe_ratio'] for r in top_10) / len(top_10)
    avg_volatility = sum(r['volatility'] for r in top_10) / len(top_10)
    
    print(f"\n   Average Probability of Loss:  {avg_prob_loss:.1f}%")
    print(f"   Average Sharpe Ratio:         {avg_sharpe:.3f}")
    print(f"   Average Volatility:           {avg_volatility:.2f}%")
    print(f"   Diversification:              10 cryptocurrencies")
    
    if avg_prob_loss < 45:
        risk_level = "🟢 LOW-MODERATE RISK"
    elif avg_prob_loss < 50:
        risk_level = "🟡 MODERATE RISK"
    else:
        risk_level = "🔴 MODERATE-HIGH RISK"
    
    print(f"   Overall Risk Level:           {risk_level}")
    
    # Comparison with excluded coins
    print("\n" + "="*100)
    print("📉 COINS NOT IN TOP 10 (For Reference)")
    print("="*100)
    print(f"\n{'Rank':<6} {'Crypto':<25} {'Score':<8} {'Expected Return':<15}")
    print("-"*100)
    
    for i, r in enumerate(results[10:20], 11):
        print(f"{i:<6} {r['crypto']:<25} {r['score']:>6.1f}  {r['avg_return']:>13.2f}%")
    
    # Key insights
    print("\n" + "="*100)
    print("🎯 KEY INSIGHTS & RECOMMENDATIONS")
    print("="*100)
    
    best = results[0]
    print(f"""
✅ BEST PERFORMER:
   {best['crypto']} with {best['avg_return']:.2f}% expected return
   Upside potential: {best['p90']:.2f}% | Downside risk: {best['p10']:.2f}%

💡 STRATEGY:
   1. Diversify across all top 10 cryptocurrencies
   2. Use the suggested allocation percentages
   3. Set stop-loss orders at -15% to -20% to manage risk
   4. Consider taking partial profits at +20%, +40%, +60%
   5. Monitor portfolio weekly and rebalance if needed

⏰ TIMING:
   - Entry: Dollar-cost average over 3-5 days
   - Hold Period: 30 days
   - Exit: Gradually sell over 2-3 days or at target profits

⚠️  RISK MANAGEMENT:
   - Only invest capital you can afford to lose
   - Cryptocurrency markets are highly volatile
   - This analysis is based on statistical modeling
   - Past performance does not guarantee future results
   - Consider your personal risk tolerance

📚 DISCLAIMER:
   This is for educational purposes only and not financial advice.
   Always do your own research (DYOR) and consult with a financial advisor.
    """)
    
    print("="*100)
    print("🚀 ANALYSIS COMPLETE - May your portfolio moon! 🌙")
    print("="*100)


if __name__ == "__main__":
    main()
