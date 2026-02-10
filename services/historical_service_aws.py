"""
Historical Service - AWS DynamoDB Implementation
"""
from datetime import datetime, timedelta
from decimal import Decimal
import os
import time

class HistoricalServiceAWS:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table_name = os.getenv('DYNAMODB_PRICES_TABLE', 'CryptoPrices')
        self.table = dynamodb.Table(self.table_name)
        self.cache = {}
    
    def store_price_snapshot(self, crypto_id, price, timestamp=None):
        """Store a price snapshot to DynamoDB"""
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()
            
            # Calculate TTL (90 days from now)
            ttl = int((datetime.utcnow() + timedelta(days=90)).timestamp())
            
            self.table.put_item(
                Item={
                    'CryptoTicker': crypto_id,  # Partition key
                    'Timestamp': Decimal(str(int(timestamp.timestamp()))),  # Sort key (Number)
                    'price_usd': Decimal(str(price)),
                    'recorded_at': timestamp.isoformat(),
                    'source': 'coingecko',
                    'expires_at': ttl
                }
            )
            
            return {'success': True, 'message': 'Price snapshot stored'}
        
        except Exception as e:
            print(f"Error storing price snapshot: {e}")
            return {'success': False, 'error': 'STORAGE_FAILED', 'message': str(e)}
    
    def get_historical_data(self, crypto_id, days=7):
        """Retrieve historical prices for date range"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            start_timestamp = int(start_date.timestamp())
            
            response = self.table.query(
                KeyConditionExpression='CryptoTicker = :cid AND #ts >= :start',
                ExpressionAttributeNames={'#ts': 'Timestamp'},
                ExpressionAttributeValues={
                    ':cid': crypto_id,
                    ':start': start_timestamp
                }
            )
            
            # Convert data for JSON serialization
            data = []
            for item in response['Items']:
                data.append({
                    'crypto_id': item['CryptoTicker'],
                    'price_usd': float(item['price_usd']),
                    'timestamp': datetime.fromtimestamp(int(item['Timestamp'])),
                    'recorded_at': item['recorded_at'],
                    'source': item.get('source', 'coingecko')
                })
            
            # Sort by timestamp
            data.sort(key=lambda x: x['timestamp'])
            
            return {'success': True, 'data': data}
        
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def get_cached_historical_data(self, cache_key):
        """Check cache for frequently accessed data"""
        return self.cache.get(cache_key)
