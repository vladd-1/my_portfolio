"""
Risk Manager for Crypto Trading Bot
Implements safety controls and position sizing
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from config import config


class RiskManager:
    """Manages trading risk and enforces safety limits."""
    
    def __init__(self):
        """Initialize risk manager."""
        self.daily_volume = 0.0
        self.daily_loss = 0.0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.positions: Dict[str, Dict] = {}  # symbol -> position info
        self.trade_history: List[Dict] = []
        self.circuit_breaker_active = False
        self.initial_portfolio_value = 0.0
        
    def reset_daily_limits(self):
        """Reset daily counters if new day."""
        now = datetime.now()
        if now >= self.daily_reset_time + timedelta(days=1):
            self.daily_volume = 0.0
            self.daily_loss = 0.0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            print(f"✅ Daily limits reset at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def set_initial_portfolio_value(self, value: float):
        """
        Set initial portfolio value for circuit breaker calculation.
        
        Args:
            value: Initial portfolio value in USD
        """
        self.initial_portfolio_value = value
        print(f"📊 Initial portfolio value set: ${value:,.2f}")
    
    def check_circuit_breaker(self, current_portfolio_value: float) -> bool:
        """
        Check if circuit breaker should activate.
        
        Args:
            current_portfolio_value: Current total portfolio value
            
        Returns:
            True if circuit breaker activated, False otherwise
        """
        if self.initial_portfolio_value == 0:
            return False
        
        loss_pct = ((current_portfolio_value - self.initial_portfolio_value) 
                    / self.initial_portfolio_value * 100)
        
        if loss_pct <= -config.CIRCUIT_BREAKER_THRESHOLD:
            if not self.circuit_breaker_active:
                self.circuit_breaker_active = True
                print(f"\n🚨 CIRCUIT BREAKER ACTIVATED!")
                print(f"   Portfolio loss: {loss_pct:.2f}%")
                print(f"   Threshold: -{config.CIRCUIT_BREAKER_THRESHOLD}%")
                print(f"   All trading halted!")
            return True
        
        return False
    
    def can_trade(self, reason: str = "") -> Tuple[bool, str]:
        """
        Check if trading is allowed.
        
        Args:
            reason: Optional reason for logging
            
        Returns:
            (can_trade, reason_if_not)
        """
        self.reset_daily_limits()
        
        # Check emergency stop
        if config.EMERGENCY_STOP:
            return False, "Emergency stop activated"
        
        # Check circuit breaker
        if self.circuit_breaker_active:
            return False, "Circuit breaker active - portfolio loss exceeded threshold"
        
        # Check daily loss limit
        if abs(self.daily_loss) >= config.MAX_DAILY_LOSS:
            return False, f"Daily loss limit reached: ${abs(self.daily_loss):.2f} >= ${config.MAX_DAILY_LOSS:.2f}"
        
        # Check daily volume limit
        if self.daily_volume >= config.MAX_DAILY_VOLUME:
            return False, f"Daily volume limit reached: ${self.daily_volume:.2f} >= ${config.MAX_DAILY_VOLUME:.2f}"
        
        return True, "OK"
    
    def calculate_position_size(self, symbol: str, price: float, 
                                allocation_pct: float, total_capital: float) -> float:
        """
        Calculate position size based on allocation and risk limits.
        
        Args:
            symbol: Trading pair symbol
            price: Current price
            allocation_pct: Target allocation percentage (0-100)
            total_capital: Total available capital
            
        Returns:
            Position size in USD
        """
        # Calculate base position size from allocation
        base_size = total_capital * (allocation_pct / 100)
        
        # Apply maximum position size limit
        position_size = min(base_size, config.MAX_POSITION_SIZE)
        
        # Check remaining daily volume
        remaining_volume = config.MAX_DAILY_VOLUME - self.daily_volume
        position_size = min(position_size, remaining_volume)
        
        # Ensure minimum trade size
        if position_size < config.MIN_TRADE_SIZE:
            return 0.0
        
        return position_size
    
    def approve_trade(self, symbol: str, side: str, quantity: float, 
                     price: float) -> Tuple[bool, str]:
        """
        Approve or reject a trade based on risk parameters.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            quantity: Trade quantity
            price: Trade price
            
        Returns:
            (approved, reason_if_rejected)
        """
        # Check if trading is allowed
        can_trade, reason = self.can_trade()
        if not can_trade:
            return False, reason
        
        trade_value = quantity * price
        
        # Check minimum trade size
        if trade_value < config.MIN_TRADE_SIZE:
            return False, f"Trade size ${trade_value:.2f} below minimum ${config.MIN_TRADE_SIZE:.2f}"
        
        # Check maximum position size
        if side == 'buy' and trade_value > config.MAX_POSITION_SIZE:
            return False, f"Trade size ${trade_value:.2f} exceeds max position ${config.MAX_POSITION_SIZE:.2f}"
        
        # Check daily volume limit
        if self.daily_volume + trade_value > config.MAX_DAILY_VOLUME:
            return False, f"Trade would exceed daily volume limit"
        
        # Check max positions for new buys
        if side == 'buy' and len(self.positions) >= config.MAX_POSITIONS:
            if symbol not in self.positions:
                return False, f"Maximum positions ({config.MAX_POSITIONS}) reached"
        
        return True, "Trade approved"
    
    def record_trade(self, symbol: str, side: str, quantity: float, 
                    price: float, fee: float = 0.0):
        """
        Record a trade and update risk metrics.
        
        Args:
            symbol: Trading pair
            side: 'buy' or 'sell'
            quantity: Trade quantity
            price: Trade price
            fee: Trading fee
        """
        trade_value = quantity * price
        
        # Update daily volume
        self.daily_volume += trade_value
        
        # Record trade
        trade = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'value': trade_value,
            'fee': fee
        }
        self.trade_history.append(trade)
        
        # Update positions
        if side == 'buy':
            if symbol in self.positions:
                # Average up
                pos = self.positions[symbol]
                total_qty = pos['quantity'] + quantity
                avg_price = ((pos['quantity'] * pos['avg_price']) + (quantity * price)) / total_qty
                pos['quantity'] = total_qty
                pos['avg_price'] = avg_price
            else:
                # New position
                self.positions[symbol] = {
                    'quantity': quantity,
                    'avg_price': price,
                    'entry_time': datetime.now()
                }
        
        elif side == 'sell':
            if symbol in self.positions:
                pos = self.positions[symbol]
                pos['quantity'] -= quantity
                
                # Calculate realized P&L
                pnl = (price - pos['avg_price']) * quantity - fee
                self.daily_loss += pnl if pnl < 0 else 0
                
                # Remove position if fully closed
                if pos['quantity'] <= 0.0001:  # Small threshold for rounding
                    del self.positions[symbol]
        
        print(f"📝 Trade recorded: {side.upper()} {quantity:.6f} {symbol} @ ${price:.2f}")
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """
        Check if stop loss should trigger for a position.
        
        Args:
            symbol: Trading pair
            current_price: Current market price
            
        Returns:
            True if stop loss triggered, False otherwise
        """
        if symbol not in self.positions:
            return False
        
        pos = self.positions[symbol]
        entry_price = pos['avg_price']
        
        # Calculate loss percentage
        loss_pct = ((current_price - entry_price) / entry_price) * 100
        
        if loss_pct <= -config.STOP_LOSS_PERCENTAGE:
            print(f"\n⚠️  STOP LOSS TRIGGERED for {symbol}")
            print(f"   Entry: ${entry_price:.2f}")
            print(f"   Current: ${current_price:.2f}")
            print(f"   Loss: {loss_pct:.2f}%")
            return True
        
        return False
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Get position information.
        
        Args:
            symbol: Trading pair
            
        Returns:
            Position dict or None
        """
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Dict]:
        """Get all current positions."""
        return self.positions.copy()
    
    def calculate_position_pnl(self, symbol: str, current_price: float) -> float:
        """
        Calculate unrealized P&L for a position.
        
        Args:
            symbol: Trading pair
            current_price: Current market price
            
        Returns:
            Unrealized P&L in USD
        """
        if symbol not in self.positions:
            return 0.0
        
        pos = self.positions[symbol]
        pnl = (current_price - pos['avg_price']) * pos['quantity']
        return pnl
    
    def get_risk_metrics(self) -> Dict:
        """
        Get current risk metrics.
        
        Returns:
            Dictionary of risk metrics
        """
        self.reset_daily_limits()
        
        return {
            'daily_volume': self.daily_volume,
            'daily_volume_limit': config.MAX_DAILY_VOLUME,
            'daily_volume_used_pct': (self.daily_volume / config.MAX_DAILY_VOLUME * 100),
            'daily_loss': self.daily_loss,
            'daily_loss_limit': config.MAX_DAILY_LOSS,
            'daily_loss_used_pct': (abs(self.daily_loss) / config.MAX_DAILY_LOSS * 100),
            'open_positions': len(self.positions),
            'max_positions': config.MAX_POSITIONS,
            'circuit_breaker_active': self.circuit_breaker_active,
            'can_trade': self.can_trade()[0]
        }
    
    def print_risk_summary(self):
        """Print risk metrics summary."""
        metrics = self.get_risk_metrics()
        
        print("\n" + "=" * 70)
        print("RISK MANAGEMENT SUMMARY")
        print("=" * 70)
        print(f"\n📊 Daily Limits:")
        print(f"   Volume:  ${metrics['daily_volume']:,.2f} / ${metrics['daily_volume_limit']:,.2f} "
              f"({metrics['daily_volume_used_pct']:.1f}%)")
        print(f"   Loss:    ${abs(metrics['daily_loss']):,.2f} / ${metrics['daily_loss_limit']:,.2f} "
              f"({metrics['daily_loss_used_pct']:.1f}%)")
        print(f"\n📈 Positions:")
        print(f"   Open:    {metrics['open_positions']} / {metrics['max_positions']}")
        print(f"\n⚡ Status:")
        print(f"   Circuit Breaker: {'🔴 ACTIVE' if metrics['circuit_breaker_active'] else '🟢 OK'}")
        print(f"   Can Trade:       {'✅ YES' if metrics['can_trade'] else '❌ NO'}")
        print("=" * 70)


if __name__ == "__main__":
    # Test risk manager
    print("Risk Manager Test")
    print("=" * 70)
    
    rm = RiskManager()
    rm.set_initial_portfolio_value(10000)
    
    # Test trade approval
    approved, reason = rm.approve_trade('btcinr', 'buy', 0.001, 45000)
    print(f"\nTrade approval: {approved}")
    print(f"Reason: {reason}")
    
    # Record a trade
    if approved:
        rm.record_trade('btcinr', 'buy', 0.001, 45000, fee=0.5)
    
    # Print summary
    rm.print_risk_summary()
