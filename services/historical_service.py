"""
Historical Service
Stores and retrieves historical price data
"""
from datetime import datetime, timedelta
from decimal import Decimal

class HistoricalService:
    def __init__(self):
        self.prices = {}  # In-memory storage (replace with DynamoDB in production)
        self.cache = {}
    
    def store_price_snapshot(self, crypto_id, price, timestamp=None):
        """Store a price snapshot"""
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()
            
            snapshot = {
                'crypto_id': crypto_id,
                'price_usd': Decimal(str(price)),
                'timestamp': timestamp,
                'recorded_at': timestamp.isoformat(),
                'source': 'coingecko'
            }
            
            # Store snapshot
            if crypto_id not in self.prices:
                self.prices[crypto_id] = []
            
            self.prices[crypto_id].append(snapshot)
            
            # Keep only last 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            self.prices[crypto_id] = [
                s for s in self.prices[crypto_id]
                if s['timestamp'] >= cutoff_date
            ]
            
            return {'success': True, 'message': 'Price snapshot stored'}
        
        except Exception as e:
            return {'success': False, 'error': 'STORAGE_FAILED', 'message': str(e)}
    
    def get_historical_data(self, crypto_id, days=7):
        """Retrieve historical prices for date range"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            if crypto_id not in self.prices:
                return {'success': True, 'data': []}
            
            # Filter by date range
            filtered_data = [
                s for s in self.prices[crypto_id]
                if s['timestamp'] >= start_date
            ]
            
            # Sort by timestamp
            filtered_data.sort(key=lambda x: x['timestamp'])
            
            return {'success': True, 'data': filtered_data}
        
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def get_cached_historical_data(self, cache_key):
        """Check cache for frequently accessed historical data"""
        return self.cache.get(cache_key)
