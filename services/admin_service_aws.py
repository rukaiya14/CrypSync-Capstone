"""
Admin Service - AWS DynamoDB Implementation
"""
import os
from decimal import Decimal

class AdminServiceAWS:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.users_table = dynamodb.Table(os.getenv('DYNAMODB_USERS_TABLE', 'Users_New'))
        self.portfolio_table = dynamodb.Table(os.getenv('DYNAMODB_PORTFOLIO_TABLE', 'UserPortfolios'))
        self.alerts_table = dynamodb.Table(os.getenv('DYNAMODB_ALERTS_TABLE', 'PriceAlerts'))
    
    def get_dashboard_stats(self):
        """Get admin dashboard statistics"""
        try:
            # Get total users
            users_response = self.users_table.scan(Select='COUNT')
            total_users = users_response.get('Count', 0)
            
            # Get total transactions
            portfolio_response = self.portfolio_table.scan(Select='COUNT')
            total_transactions = portfolio_response.get('Count', 0)
            
            # Get active alerts
            alerts_response = self.alerts_table.scan(
                FilterExpression='#state = :active',
                ExpressionAttributeNames={'#state': 'state'},
                ExpressionAttributeValues={':active': 'ACTIVE'},
                Select='COUNT'
            )
            active_alerts = alerts_response.get('Count', 0)
            
            # Calculate portfolio value (scan all transactions)
            portfolio_full = self.portfolio_table.scan()
            total_portfolio_value = 0
            
            for item in portfolio_full.get('Items', []):
                if item.get('transaction_type') == 'BUY':
                    total_portfolio_value += float(item.get('total', 0))
            
            return {
                'success': True,
                'stats': {
                    'total_users': total_users,
                    'total_transactions': total_transactions,
                    'portfolio_value': total_portfolio_value,
                    'active_alerts': active_alerts
                }
            }
        
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_all_users(self):
        """Get all registered users"""
        try:
            response = self.users_table.scan()
            
            users = []
            for item in response.get('Items', []):
                users.append({
                    'email': item.get('email'),
                    'username': item.get('username'),
                    'created_at': item.get('created_at'),
                    'last_login': item.get('last_login')
                })
            
            return {'success': True, 'users': users}
        
        except Exception as e:
            print(f"Error fetching users: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_all_transactions(self):
        """Get all portfolio transactions"""
        try:
            response = self.portfolio_table.scan()
            
            transactions = []
            for item in response.get('Items', []):
                transactions.append({
                    'email': item.get('email'),
                    'transaction_id': item.get('TransactionID'),
                    'crypto_id': item.get('crypto_id'),
                    'transaction_type': item.get('transaction_type'),
                    'amount': float(item.get('amount', 0)),
                    'price': float(item.get('price', 0)),
                    'total': float(item.get('total', 0)),
                    'timestamp': item.get('timestamp')
                })
            
            # Sort by timestamp descending
            transactions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return {'success': True, 'transactions': transactions}
        
        except Exception as e:
            print(f"Error fetching transactions: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_all_alerts(self):
        """Get all price alerts"""
        try:
            response = self.alerts_table.scan()
            
            alerts = []
            for item in response.get('Items', []):
                alerts.append({
                    'alert_id': item.get('AlertID'),
                    'user_id': item.get('UserID'),
                    'crypto_id': item.get('crypto_id'),
                    'threshold': float(item.get('threshold', 0)),
                    'alert_type': item.get('alert_type'),
                    'state': item.get('state'),
                    'created_at': item.get('created_at')
                })
            
            return {'success': True, 'alerts': alerts}
        
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return {'success': False, 'error': str(e)}
