"""
Alert Service - AWS DynamoDB Implementation
"""
import uuid
from datetime import datetime
from decimal import Decimal
import os

class AlertServiceAWS:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table_name = os.getenv('DYNAMODB_ALERTS_TABLE', 'crypsync-alerts-production')
        self.table = dynamodb.Table(self.table_name)
    
    def create_alert(self, user_id, crypto_id, threshold, alert_type):
        """Create a new price alert"""
        try:
            alert_id = str(uuid.uuid4())
            
            self.table.put_item(
                Item={
                    'user_id': user_id,
                    'alert_id': alert_id,
                    'crypto_id': crypto_id,
                    'threshold': Decimal(str(threshold)),
                    'alert_type': alert_type,
                    'state': 'ACTIVE',
                    'created_at': datetime.utcnow().isoformat(),
                    'last_triggered': None
                }
            )
            
            return {
                'success': True,
                'alert': {
                    'alert_id': alert_id,
                    'user_id': user_id,
                    'crypto_id': crypto_id,
                    'threshold': threshold,
                    'alert_type': alert_type,
                    'state': 'ACTIVE'
                },
                'message': 'Alert created successfully'
            }
        
        except Exception as e:
            return {'success': False, 'error': 'ALERT_CREATION_FAILED', 'message': str(e)}
    
    def get_user_alerts(self, user_id):
        """Get all alerts for a user"""
        try:
            response = self.table.query(
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            
            # Convert Decimal to float for JSON serialization
            alerts = []
            for item in response['Items']:
                alert = dict(item)
                if 'threshold' in alert:
                    alert['threshold'] = float(alert['threshold'])
                alerts.append(alert)
            
            return {'success': True, 'alerts': alerts}
        
        except Exception as e:
            return {'success': False, 'error': 'ALERT_FETCH_FAILED', 'message': str(e)}
    
    def delete_alert(self, alert_id, user_id):
        """Delete an alert"""
        try:
            self.table.delete_item(
                Key={
                    'user_id': user_id,
                    'alert_id': alert_id
                }
            )
            
            return {'success': True, 'message': 'Alert deleted successfully'}
        
        except Exception as e:
            return {'success': False, 'error': 'ALERT_DELETION_FAILED', 'message': str(e)}
    
    def evaluate_alerts(self, current_prices):
        """Evaluate all active alerts"""
        triggered_alerts = []
        
        try:
            # Query all active alerts
            response = self.table.query(
                IndexName='state-index',
                KeyConditionExpression='#state = :active',
                ExpressionAttributeNames={'#state': 'state'},
                ExpressionAttributeValues={':active': 'ACTIVE'}
            )
            
            for alert in response['Items']:
                crypto_id = alert['crypto_id']
                if crypto_id not in current_prices:
                    continue
                
                current_price = Decimal(str(current_prices[crypto_id]['price_usd']))
                threshold = alert['threshold']
                alert_type = alert['alert_type']
                
                should_trigger = False
                if alert_type == 'ABOVE_THRESHOLD' and current_price >= threshold:
                    should_trigger = True
                elif alert_type == 'BELOW_THRESHOLD' and current_price <= threshold:
                    should_trigger = True
                
                if should_trigger:
                    # Update alert state
                    self.table.update_item(
                        Key={
                            'user_id': alert['user_id'],
                            'alert_id': alert['alert_id']
                        },
                        UpdateExpression='SET #state = :triggered, last_triggered = :time',
                        ExpressionAttributeNames={'#state': 'state'},
                        ExpressionAttributeValues={
                            ':triggered': 'TRIGGERED',
                            ':time': datetime.utcnow().isoformat()
                        }
                    )
                    
                    triggered_alerts.append({
                        'alert': alert,
                        'current_price': float(current_price),
                        'user_id': alert['user_id']
                    })
            
            return triggered_alerts
        
        except Exception as e:
            print(f"Error evaluating alerts: {e}")
            return []
