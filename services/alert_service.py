"""
Alert Service
Manages price alerts and evaluates thresholds
"""
import uuid
from datetime import datetime
from decimal import Decimal

class AlertService:
    def __init__(self):
        self.alerts = {}  # In-memory storage (replace with DynamoDB in production)
    
    def create_alert(self, user_id, crypto_id, threshold, alert_type):
        """Create a new price alert for a user"""
        try:
            alert_id = str(uuid.uuid4())
            
            alert = {
                'alert_id': alert_id,
                'user_id': user_id,
                'crypto_id': crypto_id,
                'threshold': Decimal(str(threshold)),
                'alert_type': alert_type,  # 'ABOVE_THRESHOLD' or 'BELOW_THRESHOLD'
                'state': 'ACTIVE',
                'created_at': datetime.utcnow().isoformat(),
                'last_triggered': None
            }
            
            # Store alert
            if user_id not in self.alerts:
                self.alerts[user_id] = {}
            
            self.alerts[user_id][alert_id] = alert
            
            return {'success': True, 'alert': alert, 'message': 'Alert created successfully'}
        
        except Exception as e:
            return {'success': False, 'error': 'ALERT_CREATION_FAILED', 'message': str(e)}
    
    def get_user_alerts(self, user_id):
        """Retrieve all active alerts for a user"""
        try:
            if user_id not in self.alerts:
                return {'success': True, 'alerts': []}
            
            alerts = list(self.alerts[user_id].values())
            return {'success': True, 'alerts': alerts}
        
        except Exception as e:
            return {'success': False, 'error': 'ALERT_FETCH_FAILED', 'message': str(e)}
    
    def delete_alert(self, alert_id, user_id):
        """Delete a specific alert"""
        try:
            if user_id not in self.alerts or alert_id not in self.alerts[user_id]:
                return {'success': False, 'error': 'ALERT_NOT_FOUND', 'message': 'Alert not found'}
            
            del self.alerts[user_id][alert_id]
            
            return {'success': True, 'message': 'Alert deleted successfully'}
        
        except Exception as e:
            return {'success': False, 'error': 'ALERT_DELETION_FAILED', 'message': str(e)}
    
    def evaluate_alerts(self, current_prices):
        """Evaluate all active alerts against current prices"""
        triggered_alerts = []
        
        try:
            for user_id, user_alerts in self.alerts.items():
                for alert_id, alert in user_alerts.items():
                    if alert['state'] != 'ACTIVE':
                        continue
                    
                    crypto_id = alert['crypto_id']
                    if crypto_id not in current_prices:
                        continue
                    
                    current_price = current_prices[crypto_id]['price_usd']
                    threshold = alert['threshold']
                    alert_type = alert['alert_type']
                    
                    # Check if alert should trigger
                    should_trigger = False
                    if alert_type == 'ABOVE_THRESHOLD' and current_price >= threshold:
                        should_trigger = True
                    elif alert_type == 'BELOW_THRESHOLD' and current_price <= threshold:
                        should_trigger = True
                    
                    if should_trigger:
                        # Update alert state
                        alert['state'] = 'TRIGGERED'
                        alert['last_triggered'] = datetime.utcnow().isoformat()
                        
                        triggered_alerts.append({
                            'alert': alert,
                            'current_price': current_price,
                            'user_id': user_id
                        })
            
            return triggered_alerts
        
        except Exception as e:
            print(f"Error evaluating alerts: {e}")
            return []
