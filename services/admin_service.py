"""
Admin Service
Handles admin-specific operations like user management and coin tracking
"""
from database import get_db_connection
from datetime import datetime
import uuid

class AdminService:
    def __init__(self):
        pass
    
    def is_admin(self, user_id):
        """Check if user is admin"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            return user and user['role'] == 'admin'
        except Exception as e:
            return False
    
    def get_all_users(self):
        """Get all registered users"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT user_id, email, role, created_at, last_login
                FROM users
                ORDER BY created_at DESC
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            return {
                'success': True,
                'users': [dict(user) for user in users],
                'total_count': len(users)
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def get_user_statistics(self):
        """Get user statistics"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) as count FROM users')
            total_users = cursor.fetchone()['count']
            
            # Admin users
            cursor.execute('SELECT COUNT(*) as count FROM users WHERE role = "admin"')
            admin_users = cursor.fetchone()['count']
            
            # Regular users
            regular_users = total_users - admin_users
            
            # Total transactions
            cursor.execute('SELECT COUNT(*) as count FROM transactions')
            total_transactions = cursor.fetchone()['count']
            
            # Total portfolio value (sum of all holdings)
            cursor.execute('SELECT SUM(amount * avg_price) as total FROM holdings')
            result = cursor.fetchone()
            total_portfolio_value = result['total'] if result['total'] else 0
            
            # Active alerts
            cursor.execute('SELECT COUNT(*) as count FROM portfolio_alerts WHERE status = "ACTIVE"')
            active_alerts = cursor.fetchone()['count']
            
            conn.close()
            
            return {
                'success': True,
                'statistics': {
                    'total_users': total_users,
                    'admin_users': admin_users,
                    'regular_users': regular_users,
                    'total_transactions': total_transactions,
                    'total_portfolio_value': float(total_portfolio_value),
                    'active_alerts': active_alerts
                }
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def get_tracked_coins(self):
        """Get all tracked coins"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM tracked_coins
                WHERE status = 'active'
                ORDER BY added_at DESC
            ''')
            
            coins = cursor.fetchall()
            conn.close()
            
            return {
                'success': True,
                'coins': [dict(coin) for coin in coins],
                'total_count': len(coins)
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def add_tracked_coin(self, coin_id, name, symbol, added_by):
        """Add a new coin to tracking"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if coin already exists
            cursor.execute('SELECT coin_id FROM tracked_coins WHERE coin_id = ?', (coin_id,))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'error': 'COIN_EXISTS', 'message': 'Coin already tracked'}
            
            # Add coin
            cursor.execute('''
                INSERT INTO tracked_coins (coin_id, name, symbol, added_by, added_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (coin_id, name, symbol, added_by, datetime.utcnow().isoformat(), 'active'))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Successfully added {name} ({symbol}) to tracking'
            }
        except Exception as e:
            return {'success': False, 'error': 'ADD_FAILED', 'message': str(e)}
    
    def remove_tracked_coin(self, coin_id):
        """Remove a coin from tracking"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Update status instead of deleting
            cursor.execute('''
                UPDATE tracked_coins
                SET status = 'inactive'
                WHERE coin_id = ?
            ''', (coin_id,))
            
            if cursor.rowcount == 0:
                conn.close()
                return {'success': False, 'error': 'COIN_NOT_FOUND', 'message': 'Coin not found'}
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': f'Successfully removed {coin_id} from tracking'
            }
        except Exception as e:
            return {'success': False, 'error': 'REMOVE_FAILED', 'message': str(e)}
    
    def get_recent_transactions(self, limit=50):
        """Get recent transactions across all users"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.*, u.email
                FROM transactions t
                JOIN users u ON t.user_id = u.user_id
                ORDER BY t.timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            transactions = cursor.fetchall()
            conn.close()
            
            return {
                'success': True,
                'transactions': [dict(tx) for tx in transactions]
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def delete_user(self, user_id):
        """Delete a user and all their data"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if user exists and is not admin
            cursor.execute('SELECT role FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {'success': False, 'error': 'USER_NOT_FOUND', 'message': 'User not found'}
            
            if user['role'] == 'admin':
                conn.close()
                return {'success': False, 'error': 'CANNOT_DELETE_ADMIN', 'message': 'Cannot delete admin user'}
            
            # Delete user data
            cursor.execute('DELETE FROM holdings WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM portfolio_snapshots WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM portfolio_alerts WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM price_alerts WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
            cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'User deleted successfully'
            }
        except Exception as e:
            return {'success': False, 'error': 'DELETE_FAILED', 'message': str(e)}
