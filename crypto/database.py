"""
Database Layer for Crypto Trading Bot
Handles persistent storage of trades, positions, and performance metrics
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from config import config


class Database:
    """SQLite database manager for trading bot."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or config.DB_PATH
        self.conn = None
        self.cursor = None
        self.connect()
        self.initialize_tables()
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def initialize_tables(self):
        """Create database tables if they don't exist."""
        
        # Trades table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                value REAL NOT NULL,
                fee REAL DEFAULT 0,
                order_id TEXT,
                status TEXT DEFAULT 'completed',
                notes TEXT
            )
        ''')
        
        # Positions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                quantity REAL NOT NULL,
                avg_entry_price REAL NOT NULL,
                current_price REAL,
                unrealized_pnl REAL,
                entry_time TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # Balance history table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_value REAL NOT NULL,
                cash_balance REAL NOT NULL,
                crypto_value REAL NOT NULL,
                num_positions INTEGER DEFAULT 0
            )
        ''')
        
        # Performance metrics table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_return_pct REAL,
                daily_return_pct REAL,
                sharpe_ratio REAL,
                max_drawdown_pct REAL,
                win_rate REAL,
                total_trades INTEGER,
                profitable_trades INTEGER
            )
        ''')
        
        # Bot status table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bot_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                error TEXT
            )
        ''')
        
        self.conn.commit()
        print(f"✅ Database initialized: {self.db_path}")
    
    # ============= Trade Operations =============
    
    def insert_trade(self, symbol: str, side: str, quantity: float, 
                    price: float, value: float, fee: float = 0.0,
                    order_id: str = None, notes: str = None) -> int:
        """
        Insert a new trade record.
        
        Returns:
            Trade ID
        """
        timestamp = datetime.now().isoformat()
        
        self.cursor.execute('''
            INSERT INTO trades (timestamp, symbol, side, quantity, price, value, fee, order_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, symbol, side, quantity, price, value, fee, order_id, notes))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_trades(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """
        Get trade history.
        
        Args:
            symbol: Optional symbol filter
            limit: Maximum number of trades to return
        """
        if symbol:
            self.cursor.execute('''
                SELECT * FROM trades 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (symbol, limit))
        else:
            self.cursor.execute('''
                SELECT * FROM trades 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_all_trades(self) -> List[Dict]:
        """Get all trades."""
        self.cursor.execute('SELECT * FROM trades ORDER BY timestamp DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ============= Position Operations =============
    
    def upsert_position(self, symbol: str, quantity: float, 
                       avg_entry_price: float, current_price: float = None):
        """
        Insert or update a position.
        
        Args:
            symbol: Trading pair
            quantity: Position quantity
            avg_entry_price: Average entry price
            current_price: Current market price
        """
        timestamp = datetime.now().isoformat()
        unrealized_pnl = None
        
        if current_price:
            unrealized_pnl = (current_price - avg_entry_price) * quantity
        
        # Check if position exists
        self.cursor.execute('SELECT id FROM positions WHERE symbol = ?', (symbol,))
        existing = self.cursor.fetchone()
        
        if existing:
            # Update existing position
            self.cursor.execute('''
                UPDATE positions 
                SET quantity = ?, avg_entry_price = ?, current_price = ?, 
                    unrealized_pnl = ?, last_updated = ?
                WHERE symbol = ?
            ''', (quantity, avg_entry_price, current_price, unrealized_pnl, timestamp, symbol))
        else:
            # Insert new position
            self.cursor.execute('''
                INSERT INTO positions 
                (symbol, quantity, avg_entry_price, current_price, unrealized_pnl, entry_time, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (symbol, quantity, avg_entry_price, current_price, unrealized_pnl, timestamp, timestamp))
        
        self.conn.commit()
    
    def delete_position(self, symbol: str):
        """Delete a position (when fully closed)."""
        self.cursor.execute('DELETE FROM positions WHERE symbol = ?', (symbol,))
        self.conn.commit()
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions."""
        self.cursor.execute('SELECT * FROM positions ORDER BY entry_time DESC')
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get a specific position."""
        self.cursor.execute('SELECT * FROM positions WHERE symbol = ?', (symbol,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # ============= Balance History =============
    
    def insert_balance_snapshot(self, total_value: float, cash_balance: float, 
                                crypto_value: float, num_positions: int):
        """Record a balance snapshot."""
        timestamp = datetime.now().isoformat()
        
        self.cursor.execute('''
            INSERT INTO balance_history (timestamp, total_value, cash_balance, crypto_value, num_positions)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, total_value, cash_balance, crypto_value, num_positions))
        
        self.conn.commit()
    
    def get_balance_history(self, limit: int = 100) -> List[Dict]:
        """Get balance history."""
        self.cursor.execute('''
            SELECT * FROM balance_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ============= Performance Metrics =============
    
    def insert_performance_metrics(self, total_return_pct: float, daily_return_pct: float,
                                   sharpe_ratio: float = None, max_drawdown_pct: float = None,
                                   win_rate: float = None, total_trades: int = 0,
                                   profitable_trades: int = 0):
        """Record performance metrics."""
        timestamp = datetime.now().isoformat()
        
        self.cursor.execute('''
            INSERT INTO performance_metrics 
            (timestamp, total_return_pct, daily_return_pct, sharpe_ratio, max_drawdown_pct,
             win_rate, total_trades, profitable_trades)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, total_return_pct, daily_return_pct, sharpe_ratio, max_drawdown_pct,
              win_rate, total_trades, profitable_trades))
        
        self.conn.commit()
    
    def get_latest_performance(self) -> Optional[Dict]:
        """Get latest performance metrics."""
        self.cursor.execute('''
            SELECT * FROM performance_metrics 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''')
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    # ============= Bot Status =============
    
    def log_status(self, status: str, message: str = None, error: str = None):
        """Log bot status."""
        timestamp = datetime.now().isoformat()
        
        self.cursor.execute('''
            INSERT INTO bot_status (timestamp, status, message, error)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, status, message, error))
        
        self.conn.commit()
    
    def get_status_log(self, limit: int = 50) -> List[Dict]:
        """Get status log."""
        self.cursor.execute('''
            SELECT * FROM bot_status 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ============= Analytics =============
    
    def get_trade_statistics(self) -> Dict:
        """Calculate trade statistics."""
        # Total trades
        self.cursor.execute('SELECT COUNT(*) as count FROM trades')
        total_trades = self.cursor.fetchone()['count']
        
        # Profitable trades (approximate - based on buy/sell pairs)
        self.cursor.execute('''
            SELECT COUNT(*) as count FROM trades 
            WHERE side = 'sell' AND (price > 
                (SELECT AVG(price) FROM trades t2 
                 WHERE t2.symbol = trades.symbol AND t2.side = 'buy'))
        ''')
        profitable = self.cursor.fetchone()['count']
        
        # Total volume
        self.cursor.execute('SELECT SUM(value) as total FROM trades')
        total_volume = self.cursor.fetchone()['total'] or 0
        
        # Total fees
        self.cursor.execute('SELECT SUM(fee) as total FROM trades')
        total_fees = self.cursor.fetchone()['total'] or 0
        
        win_rate = (profitable / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'profitable_trades': profitable,
            'win_rate': win_rate,
            'total_volume': total_volume,
            'total_fees': total_fees
        }
    
    def clear_all_data(self):
        """Clear all data (use with caution!)."""
        tables = ['trades', 'positions', 'balance_history', 'performance_metrics', 'bot_status']
        for table in tables:
            self.cursor.execute(f'DELETE FROM {table}')
        self.conn.commit()
        print("⚠️  All data cleared from database")


if __name__ == "__main__":
    # Test database
    print("Database Test")
    print("=" * 70)
    
    db = Database('test_trading_bot.db')
    
    # Insert test trade
    trade_id = db.insert_trade('btcinr', 'buy', 0.001, 45000, 45, fee=0.5)
    print(f"✅ Inserted trade ID: {trade_id}")
    
    # Get trades
    trades = db.get_trades(limit=5)
    print(f"✅ Retrieved {len(trades)} trades")
    
    # Insert position
    db.upsert_position('btcinr', 0.001, 45000, 46000)
    print("✅ Inserted position")
    
    # Get statistics
    stats = db.get_trade_statistics()
    print(f"✅ Trade statistics: {stats}")
    
    db.close()
    print("\n✅ Database test completed")
