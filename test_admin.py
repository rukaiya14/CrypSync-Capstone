#!/usr/bin/env python3
"""
Test Admin Functionality
Quick test to verify admin panel works correctly
"""
from database import get_db_connection, init_database, create_admin_user
from services.admin_service import AdminService

def test_admin():
    print("=== Testing Admin Functionality ===\n")
    
    # Initialize database
    print("1. Initializing database...")
    init_database()
    create_admin_user()
    print("✓ Database initialized\n")
    
    # Test admin service
    admin_service = AdminService()
    
    # Get admin user ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE email = 'admin@crypsync.com'")
    admin_user = cursor.fetchone()
    conn.close()
    
    if not admin_user:
        print("✗ Admin user not found!")
        return
    
    admin_id = admin_user['user_id']
    print(f"2. Admin user ID: {admin_id}")
    
    # Test is_admin
    print(f"3. Testing is_admin()...")
    is_admin = admin_service.is_admin(admin_id)
    print(f"   Result: {is_admin}")
    if is_admin:
        print("   ✓ Admin check passed\n")
    else:
        print("   ✗ Admin check failed\n")
        return
    
    # Test get_all_users
    print("4. Testing get_all_users()...")
    result = admin_service.get_all_users()
    if result['success']:
        print(f"   ✓ Found {result['total_count']} users")
        for user in result['users']:
            print(f"     - {user['email']} ({user['role']})")
    else:
        print(f"   ✗ Failed: {result['message']}")
    print()
    
    # Test get_user_statistics
    print("5. Testing get_user_statistics()...")
    result = admin_service.get_user_statistics()
    if result['success']:
        stats = result['statistics']
        print(f"   ✓ Statistics retrieved:")
        print(f"     - Total Users: {stats['total_users']}")
        print(f"     - Admin Users: {stats['admin_users']}")
        print(f"     - Regular Users: {stats['regular_users']}")
        print(f"     - Total Transactions: {stats['total_transactions']}")
        print(f"     - Total Portfolio Value: ${stats['total_portfolio_value']:.2f}")
        print(f"     - Active Alerts: {stats['active_alerts']}")
    else:
        print(f"   ✗ Failed: {result['message']}")
    print()
    
    # Test get_tracked_coins
    print("6. Testing get_tracked_coins()...")
    result = admin_service.get_tracked_coins()
    if result['success']:
        print(f"   ✓ Found {result['total_count']} tracked coins:")
        for coin in result['coins']:
            print(f"     - {coin['name']} ({coin['symbol']}) - {coin['coin_id']}")
    else:
        print(f"   ✗ Failed: {result['message']}")
    print()
    
    print("=== All Tests Completed ===")

if __name__ == '__main__':
    test_admin()
