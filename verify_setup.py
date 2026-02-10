#!/usr/bin/env python3
"""
CrypSync Setup Verification
Verifies that the admin panel is properly configured
"""
from database import get_db_connection
import os

def verify_setup():
    print("=" * 60)
    print("CrypSync Admin Panel - Setup Verification")
    print("=" * 60)
    print()
    
    # Check database exists
    if not os.path.exists('crypsync.db'):
        print("❌ Database not found!")
        print("   Run: python migrate_database.py")
        return False
    
    print("✅ Database found: crypsync.db")
    
    # Check database tables
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check users table has role column
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'role' not in columns:
            print("❌ Users table missing 'role' column")
            print("   Run: python migrate_database.py")
            return False
        print("✅ Users table configured correctly")
        
        # Check tracked_coins table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracked_coins'")
        if not cursor.fetchone():
            print("❌ Tracked coins table not found")
            print("   Run: python migrate_database.py")
            return False
        print("✅ Tracked coins table exists")
        
        # Count admin users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='admin'")
        admin_count = cursor.fetchone()['count']
        
        if admin_count == 0:
            print("❌ No admin users found")
            print("   Run: python -c \"from database import create_admin_user; create_admin_user()\"")
            return False
        print(f"✅ Admin users: {admin_count}")
        
        # Count total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        print(f"✅ Total users: {user_count}")
        
        # Count tracked coins
        cursor.execute("SELECT COUNT(*) as count FROM tracked_coins WHERE status='active'")
        coin_count = cursor.fetchone()['count']
        print(f"✅ Tracked coins: {coin_count}")
        
        # Get admin email
        cursor.execute("SELECT email FROM users WHERE role='admin' LIMIT 1")
        admin_email = cursor.fetchone()['email']
        
        print()
        print("=" * 60)
        print("✅ ALL CHECKS PASSED - SYSTEM READY")
        print("=" * 60)
        print()
        print("🚀 To start the application:")
        print("   python app.py")
        print()
        print("🔐 Admin Login:")
        print(f"   URL: http://localhost:5000/login")
        print(f"   Email: {admin_email}")
        print(f"   Password: admin123")
        print()
        print("📊 Admin Panel:")
        print("   After login, click the orange 'Admin' link in the navbar")
        print("   Or go to: http://localhost:5000/admin")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    success = verify_setup()
    exit(0 if success else 1)
