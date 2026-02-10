#!/usr/bin/env python3
"""
Database Migration Script
Adds role column and tracked_coins table to existing database
"""
import sqlite3
import os
from datetime import datetime

DATABASE_PATH = 'crypsync.db'

def migrate_database():
    """Migrate existing database to add new features"""
    print("=== Database Migration ===\n")
    
    if not os.path.exists(DATABASE_PATH):
        print("✗ Database not found. Run init_database() first.")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if role column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' not in columns:
            print("1. Adding 'role' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            print("   ✓ Role column added\n")
        else:
            print("1. Role column already exists\n")
        
        # Check if tracked_coins table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracked_coins'")
        if not cursor.fetchone():
            print("2. Creating tracked_coins table...")
            cursor.execute('''
                CREATE TABLE tracked_coins (
                    coin_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    added_by TEXT,
                    added_at TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (added_by) REFERENCES users(user_id)
                )
            ''')
            
            # Insert default coins
            default_coins = [
                ('bitcoin', 'Bitcoin', 'BTC'),
                ('ethereum', 'Ethereum', 'ETH'),
                ('cardano', 'Cardano', 'ADA'),
                ('solana', 'Solana', 'SOL'),
                ('ripple', 'Ripple', 'XRP')
            ]
            
            for coin_id, name, symbol in default_coins:
                cursor.execute('''
                    INSERT INTO tracked_coins (coin_id, name, symbol, added_at, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (coin_id, name, symbol, datetime.now().isoformat(), 'active'))
            
            print("   ✓ Tracked coins table created with default coins\n")
        else:
            print("2. Tracked coins table already exists\n")
        
        # Create indexes if they don't exist
        print("3. Creating indexes...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracked_coins_status ON tracked_coins(status)')
        print("   ✓ Indexes created\n")
        
        # Update admin user if exists
        print("4. Checking for admin user...")
        cursor.execute("SELECT user_id FROM users WHERE email = 'admin@crypsync.com'")
        admin = cursor.fetchone()
        
        if admin:
            cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'admin@crypsync.com'")
            print("   ✓ Admin user role updated\n")
        else:
            print("   ⚠ Admin user not found. Run create_admin_user() to create one.\n")
        
        conn.commit()
        print("=== Migration Completed Successfully ===")
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
