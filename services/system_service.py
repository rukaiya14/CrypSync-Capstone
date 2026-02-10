"""
System Service
Monitors system health, API status, and active users
"""
from database import get_db_connection
from datetime import datetime, timedelta
import time

class SystemService:
    def __init__(self):
        self.start_time = time.time()
        self.api_status = 'connected'
        self.last_api_check = datetime.now()
    
    def get_system_status(self):
        """Get overall system status"""
        try:
            # Check database connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            db_status = 'connected'
            conn.close()
        except:
            db_status = 'disconnected'
        
        # Calculate uptime
        uptime_seconds = int(time.time() - self.start_time)
        uptime_hours = uptime_seconds // 3600
        uptime_minutes = (uptime_seconds % 3600) // 60
        
        # Get active users (sessions created in last 30 minutes)
        active_users = self.get_active_users_count()
        
        # Mock system load (in production, use psutil)
        system_load = 12  # percentage
        
        # API rate limit (mock - in production, track actual API calls)
        api_rate_limit = {
            'used': 45,
            'limit': 50,
            'percentage': 90
        }
        
        return {
            'success': True,
            'status': {
                'api_status': self.api_status,
                'db_status': db_status,
                'uptime': f"{uptime_hours}h {uptime_minutes}m",
                'uptime_seconds': uptime_seconds,
                'active_users': active_users,
                'system_load': system_load,
                'api_rate_limit': api_rate_limit,
                'overall_health': 88  # percentage
            }
        }
    
    def get_active_users_count(self):
        """Get count of active users (sessions in last 30 minutes)"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get sessions created in last 30 minutes
            thirty_min_ago = (datetime.now() - timedelta(minutes=30)).isoformat()
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) as count
                FROM sessions
                WHERE created_at > ?
            ''', (thirty_min_ago,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result['count'] if result else 0
        except:
            return 0
    
    def get_api_status(self):
        """Get detailed API status"""
        return {
            'success': True,
            'api': {
                'coingecko': {
                    'status': 'operational',
                    'last_check': self.last_api_check.isoformat(),
                    'response_time': '120ms',
                    'rate_limit': {
                        'used': 45,
                        'limit': 50,
                        'reset_in': '45s'
                    }
                }
            }
        }
    
    def update_api_status(self, status):
        """Update API status after API call"""
        self.api_status = status
        self.last_api_check = datetime.now()
