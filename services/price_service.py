"""
Price Service
Fetches and caches real-time cryptocurrency prices from CoinGecko API
"""
import requests
from datetime import datetime, timedelta
from decimal import Decimal
import time

class PriceService:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache = {}
        self.cache_duration = 60  # seconds
        self.rate_limit_tokens = 50
        self.rate_limit_window = 60  # seconds
        self.last_request_time = None
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_open = False
        self.circuit_breaker_reset_time = None
    
    def get_current_prices(self, crypto_ids):
        """Get current prices for specified cryptocurrencies"""
        try:
            # Check cache first
            if self._is_cache_valid():
                cached_prices = self._get_from_cache(crypto_ids)
                if cached_prices:
                    return {'success': True, 'data': cached_prices, 'cached': True}
            
            # Fetch from API
            result = self.fetch_from_api(crypto_ids)
            return result
        
        except Exception as e:
            return {'success': False, 'error': 'PRICE_FETCH_FAILED', 'message': str(e)}
    
    def fetch_from_api(self, crypto_ids):
        """Fetch prices directly from CoinGecko API"""
        try:
            # Check circuit breaker
            if self.circuit_breaker_open:
                if datetime.utcnow() < self.circuit_breaker_reset_time:
                    # Return cached data if available
                    cached = self._get_from_cache(crypto_ids)
                    if cached:
                        return {'success': True, 'data': cached, 'cached': True, 'warning': 'API temporarily unavailable'}
                    return {'success': False, 'error': 'API_UNAVAILABLE', 'message': 'CoinGecko API is temporarily unavailable'}
                else:
                    # Reset circuit breaker
                    self.circuit_breaker_open = False
                    self.circuit_breaker_failures = 0
            
            # Rate limiting
            self._apply_rate_limit()
            
            # Make API request
            ids_param = ','.join(crypto_ids)
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ids_param,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Transform data
            prices = {}
            for crypto_id in crypto_ids:
                if crypto_id in data:
                    prices[crypto_id] = {
                        'crypto_id': crypto_id,
                        'price_usd': Decimal(str(data[crypto_id]['usd'])),
                        'change_24h': Decimal(str(data[crypto_id].get('usd_24h_change', 0))),
                        'fetched_at': datetime.utcnow().isoformat()
                    }
            
            # Update cache
            self._update_cache(prices)
            
            # Reset circuit breaker on success
            self.circuit_breaker_failures = 0
            
            return {'success': True, 'data': prices, 'cached': False}
        
        except requests.exceptions.RequestException as e:
            # Increment circuit breaker failures
            self.circuit_breaker_failures += 1
            
            if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
                self.circuit_breaker_open = True
                self.circuit_breaker_reset_time = datetime.utcnow() + timedelta(seconds=60)
            
            # Try to return cached data
            cached = self._get_from_cache(crypto_ids)
            if cached:
                return {'success': True, 'data': cached, 'cached': True, 'warning': 'Using cached data due to API error'}
            
            return {'success': False, 'error': 'API_UNAVAILABLE', 'message': f'CoinGecko API error: {str(e)}'}
    
    def _is_cache_valid(self):
        """Check if cache is still valid"""
        if not self.cache:
            return False
        
        cache_age = self.get_cache_age()
        return cache_age < self.cache_duration
    
    def _get_from_cache(self, crypto_ids):
        """Get prices from cache"""
        if not self.cache:
            return None
        
        result = {}
        for crypto_id in crypto_ids:
            if crypto_id in self.cache:
                result[crypto_id] = self.cache[crypto_id]
        
        return result if result else None
    
    def _update_cache(self, prices):
        """Update cache with new prices"""
        self.cache.update(prices)
        self.cache['_timestamp'] = datetime.utcnow()
    
    def get_cache_age(self):
        """Returns age of cached data in seconds"""
        if '_timestamp' not in self.cache:
            return float('inf')
        
        cache_time = self.cache['_timestamp']
        age = (datetime.utcnow() - cache_time).total_seconds()
        return age
    
    def _apply_rate_limit(self):
        """Apply rate limiting using token bucket algorithm"""
        current_time = time.time()
        
        if self.last_request_time:
            time_since_last = current_time - self.last_request_time
            if time_since_last < (self.rate_limit_window / self.rate_limit_tokens):
                sleep_time = (self.rate_limit_window / self.rate_limit_tokens) - time_since_last
                time.sleep(sleep_time)
        
        self.last_request_time = time.time()
