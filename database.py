"""
Database initialization and management using SQLite
"""
import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'crypsync.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_database():
    """Initialize database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    ''')
    
    # Tracked coins table (for admin management)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_coins (
            coin_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            symbol TEXT NOT NULL,
            added_by TEXT,
            added_at TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (added_by) REFERENCES users(user_id)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Portfolio holdings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS holdings (
            holding_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            crypto_id TEXT NOT NULL,
            amount REAL NOT NULL,
            avg_price REAL NOT NULL,
            total_invested REAL NOT NULL,
            first_purchase_date TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            UNIQUE(user_id, crypto_id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            crypto_id TEXT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            price_usd REAL NOT NULL,
            total_usd REAL NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Portfolio snapshots table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_snapshots (
            snapshot_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            total_value REAL NOT NULL,
            holdings_json TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Portfolio alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_alerts (
            alert_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            threshold_value REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_triggered TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Price alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_alerts (
            alert_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            crypto_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            threshold REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_triggered TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Historical prices table (for caching)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crypto_id TEXT NOT NULL,
            price_usd REAL NOT NULL,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_holdings_user ON holdings(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_user ON portfolio_snapshots(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON portfolio_snapshots(timestamp DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_user ON portfolio_alerts(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_alerts_user ON price_alerts(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracked_coins_status ON tracked_coins(status)')
    
    # Insert default tracked coins
    default_coins = [
        ('bitcoin', 'Bitcoin', 'BTC'),
        ('ethereum', 'Ethereum', 'ETH'),
        ('cardano', 'Cardano', 'ADA'),
        ('solana', 'Solana', 'SOL'),
        ('ripple', 'Ripple', 'XRP')
    ]
    
    for coin_id, name, symbol in default_coins:
        cursor.execute('''
            INSERT OR IGNORE INTO tracked_coins (coin_id, name, symbol, added_at, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (coin_id, name, symbol, datetime.now().isoformat(), 'active'))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized successfully at {DATABASE_PATH}")

def create_admin_user(email='admin@crypsync.com', password='admin123'):
    """Create default admin user"""
    import bcrypt
    import uuid
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if admin exists
    cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        print(f"⚠️  Admin user already exists: {email}")
        return
    
    # Create admin user
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
    created_at = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO users (user_id, email, password_hash, role, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, email, password_hash, 'admin', created_at))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Admin user created: {email} / {password}")

def reset_database():
    """Reset database (delete and recreate)"""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        print(f"🗑️  Deleted existing database")
    init_database()

if __name__ == '__main__':
    # Initialize database when run directly
    init_database()
    create_admin_user()  # Create default admin user
