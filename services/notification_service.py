"""
Notification Service - AWS SES Implementation
"""
import os
import time

class NotificationService:
    def __init__(self, ses_client):
        self.ses = ses_client
        self.sender_email = os.getenv('SES_SENDER_EMAIL', 'noreply@crypsync.com')
        self.max_retries = 3
    
    def send_alert_notification(self, user, alert, current_price):
        """Send email notification for triggered alert"""
        try:
            message = self.format_alert_message(alert, current_price)
            
            # Retry logic with exponential backoff
            for attempt in range(self.max_retries):
                try:
                    response = self.ses.send_email(
                        Source=self.sender_email,
                        Destination={'ToAddresses': [user['email']]},
                        Message={
                            'Subject': {
                                'Data': f'CrypSync Alert: {alert["crypto_id"].capitalize()} Price Alert',
                                'Charset': 'UTF-8'
                            },
                            'Body': {
                                'Text': {
                                    'Data': message,
                                    'Charset': 'UTF-8'
                                }
                            }
                        }
                    )
                    
                    return {'success': True, 'message_id': response['MessageId']}
                
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                        time.sleep(wait_time)
                    else:
                        raise e
        
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return {'success': False, 'error': 'NOTIFICATION_FAILED', 'message': str(e)}
    
    def format_alert_message(self, alert, current_price):
        """Format notification message"""
        crypto_name = alert['crypto_id'].capitalize()
        threshold = float(alert['threshold'])
        alert_type = 'above' if alert['alert_type'] == 'ABOVE_THRESHOLD' else 'below'
        
        message = f"""
CrypSync Price Alert

Cryptocurrency: {crypto_name}
Current Price: ${current_price:,.2f}
Alert Threshold: ${threshold:,.2f}
Alert Type: Price is {alert_type} threshold

This alert was triggered at {alert.get('last_triggered', 'now')}.

Thank you for using CrypSync!
        """
        
        return message.strip()

    def send_trade_notification(self, user_email, transaction):
        """Send trade confirmation notification via SNS/SES"""
        try:
            trade_type = transaction['type']
            crypto_id = transaction['crypto_id'].upper()
            amount = transaction['amount']
            price = transaction['price_usd']
            total = transaction['total_usd']
            
            subject = f"CrypSync: {trade_type} Order Executed - {crypto_id}"
            
            message = f"""
Trade Confirmation

Transaction Type: {trade_type}
Cryptocurrency: {crypto_id}
Amount: {amount} {crypto_id}
Price per Unit: ${price:,.2f}
Total Amount: ${total:,.2f}
Transaction ID: {transaction['transaction_id']}
Status: {transaction['status']}
Timestamp: {transaction['timestamp']}

Your {trade_type.lower()} order has been successfully executed.
Amount {'deducted' if trade_type == 'BUY' else 'credited'}: ${total:,.2f}

View your portfolio at CrypSync dashboard.

Best regards,
CrypSync Team
            """
            
            # Retry logic with exponential backoff
            for attempt in range(self.max_retries):
                try:
                    response = self.ses.send_email(
                        Source=self.sender_email,
                        Destination={'ToAddresses': [user_email]},
                        Message={
                            'Subject': {
                                'Data': subject,
                                'Charset': 'UTF-8'
                            },
                            'Body': {
                                'Text': {
                                    'Data': message.strip(),
                                    'Charset': 'UTF-8'
                                }
                            }
                        }
                    )
                    
                    return {'success': True, 'message_id': response['MessageId']}
                
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                    else:
                        raise e
        
        except Exception as e:
            print(f"Failed to send trade notification: {e}")
            return {'success': False, 'error': 'NOTIFICATION_FAILED', 'message': str(e)}
