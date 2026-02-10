"""
Portfolio Service - AWS DynamoDB Implementation
"""
import uuid
from datetime import datetime
from decimal import Decimal
import os

class PortfolioServiceAWS:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table_name = os.getenv('DYNAMODB_PORTFOLIO_TABLE', 'UserPortfolios')
        self.table = dynamodb.Table(self.table_name)
    
    def get_user_portfolio(self, user_id):
        """Get all holdings for a user - user_id is email"""
        try:
            response = self.table.query(
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': user_id}
            )
            
            # Aggregate holdings by crypto_id
            holdings = {}
            transactions = []
            
            for item in response['Items']:
                crypto_id = item.get('crypto_id')
                transaction_type = item.get('transaction_type')
                amount = float(item.get('amount', 0))
                price = float(item.get('price', 0))
                
                # Track transactions
                transactions.append({
                    'transaction_id': item.get('TransactionID'),
                    'crypto_id': crypto_id,
                    'transaction_type': transaction_type,
                    'amount': amount,
                    'price': price,
                    'total': amount * price,
                    'timestamp': item.get('timestamp')
                })
                
                # Aggregate holdings
                if crypto_id not in holdings:
                    holdings[crypto_id] = {
                        'crypto_id': crypto_id,
                        'total_amount': 0,
                        'total_invested': 0,
                        'avg_buy_price': 0
                    }
                
                if transaction_type == 'BUY':
                    holdings[crypto_id]['total_amount'] += amount
                    holdings[crypto_id]['total_invested'] += (amount * price)
                elif transaction_type == 'SELL':
                    holdings[crypto_id]['total_amount'] -= amount
                    holdings[crypto_id]['total_invested'] -= (amount * price)
            
            # Calculate average buy price
            for crypto_id, holding in holdings.items():
                if holding['total_amount'] > 0:
                    holding['avg_buy_price'] = holding['total_invested'] / holding['total_amount']
            
            # Filter out zero holdings
            holdings = {k: v for k, v in holdings.items() if v['total_amount'] > 0}
            
            return {
                'success': True,
                'holdings': list(holdings.values()),
                'transactions': transactions
            }
        
        except Exception as e:
            return {'success': False, 'error': 'PORTFOLIO_FETCH_FAILED', 'message': str(e)}
    
    def add_transaction(self, user_id, crypto_id, transaction_type, amount, price):
        """Add a buy or sell transaction - user_id is email"""
        try:
            transaction_id = str(uuid.uuid4())
            
            self.table.put_item(
                Item={
                    'email': user_id,  # Partition key (email)
                    'TransactionID': transaction_id,  # Sort key
                    'crypto_id': crypto_id,
                    'transaction_type': transaction_type,
                    'amount': Decimal(str(amount)),
                    'price': Decimal(str(price)),
                    'total': Decimal(str(amount * price)),
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            return {
                'success': True,
                'transaction': {
                    'transaction_id': transaction_id,
                    'user_id': user_id,
                    'crypto_id': crypto_id,
                    'transaction_type': transaction_type,
                    'amount': amount,
                    'price': price,
                    'total': amount * price
                },
                'message': f'{transaction_type} transaction added successfully'
            }
        
        except Exception as e:
            return {'success': False, 'error': 'TRANSACTION_FAILED', 'message': str(e)}
    
    def delete_transaction(self, user_id, transaction_id):
        """Delete a transaction - user_id is email"""
        try:
            self.table.delete_item(
                Key={
                    'email': user_id,
                    'TransactionID': transaction_id
                }
            )
            
            return {'success': True, 'message': 'Transaction deleted successfully'}
        
        except Exception as e:
            return {'success': False, 'error': 'DELETE_FAILED', 'message': str(e)}
