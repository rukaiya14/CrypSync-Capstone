"""
Portfolio Service with SQLite Database
Handles cryptocurrency portfolio management and trading with persistent storage
"""
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json
from database import get_db_connection

class PortfolioService:
    def __init__(self):
        pass  # No in-memory storage needed
    
    def get_user_portfolio(self, user_id):
        """Get user's complete portfolio from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT crypto_id, amount, avg_price, total_invested, first_purchase_date
                FROM holdings
                WHERE user_id = ?
            ''', (user_id,))
            
            holdings = cursor.fetchall()
            conn.close()
            
            portfolio = {}
            for holding in holdings:
                portfolio[holding['crypto_id']] = {
                    'amount': holding['amount'],
                    'avg_price': holding['avg_price'],
                    'total_invested': holding['total_invested'],
                    'first_purchase_date': holding['first_purchase_date']
                }
            
            return {
                'success': True,
                'portfolio': portfolio,
                'message': 'Portfolio retrieved successfully'
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def buy_crypto(self, user_id, crypto_id, amount, price_usd):
        """Buy cryptocurrency with database persistence"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            amount_decimal = Decimal(str(amount))
            price_decimal = Decimal(str(price_usd))
            total_cost = amount_decimal * price_decimal
            purchase_date = datetime.utcnow()
            
            # Get existing holding
            cursor.execute('''
                SELECT * FROM holdings WHERE user_id = ? AND crypto_id = ?
            ''', (user_id, crypto_id))
            
            holding = cursor.fetchone()
            
            if holding:
                # Update existing holding
                old_amount = Decimal(str(holding['amount']))
                old_avg_price = Decimal(str(holding['avg_price']))
                old_total = old_amount * old_avg_price
                
                new_total = old_total + total_cost
                new_amount = old_amount + amount_decimal
                new_avg_price = new_total / new_amount
                new_invested = Decimal(str(holding['total_invested'])) + total_cost
                
                cursor.execute('''
                    UPDATE holdings
                    SET amount = ?, avg_price = ?, total_invested = ?, updated_at = ?
                    WHERE user_id = ? AND crypto_id = ?
                ''', (float(new_amount), float(new_avg_price), float(new_invested),
                      purchase_date.isoformat(), user_id, crypto_id))
            else:
                # Create new holding
                cursor.execute('''
                    INSERT INTO holdings (user_id, crypto_id, amount, avg_price, total_invested, 
                                        first_purchase_date, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, crypto_id, float(amount_decimal), float(price_decimal),
                      float(total_cost), purchase_date.isoformat(), purchase_date.isoformat()))
                
                new_amount = amount_decimal
                new_avg_price = price_decimal
            
            # Create transaction record
            transaction_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO transactions (transaction_id, user_id, crypto_id, type, amount,
                                        price_usd, total_usd, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (transaction_id, user_id, crypto_id, 'BUY', float(amount_decimal),
                  float(price_decimal), float(total_cost), purchase_date.isoformat(), 'COMPLETED'))
            
            conn.commit()
            
            # Create portfolio snapshot
            self._create_portfolio_snapshot(user_id, cursor)
            conn.commit()
            conn.close()
            
            transaction = {
                'transaction_id': transaction_id,
                'user_id': user_id,
                'crypto_id': crypto_id,
                'type': 'BUY',
                'amount': float(amount_decimal),
                'price_usd': float(price_decimal),
                'total_usd': float(total_cost),
                'timestamp': purchase_date.isoformat(),
                'purchase_date': purchase_date.isoformat(),
                'status': 'COMPLETED'
            }
            
            return {
                'success': True,
                'transaction': transaction,
                'new_balance': float(new_amount),
                'avg_price': float(new_avg_price),
                'message': f'Successfully bought {amount} {crypto_id.upper()}'
            }
        
        except Exception as e:
            return {'success': False, 'error': 'BUY_FAILED', 'message': str(e)}
    
    def sell_crypto(self, user_id, crypto_id, amount, price_usd):
        """Sell cryptocurrency with database persistence"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get holding
            cursor.execute('''
                SELECT * FROM holdings WHERE user_id = ? AND crypto_id = ?
            ''', (user_id, crypto_id))
            
            holding = cursor.fetchone()
            
            if not holding:
                conn.close()
                return {'success': False, 'error': 'NO_HOLDING', 'message': f'No {crypto_id} holdings found'}
            
            amount_decimal = Decimal(str(amount))
            price_decimal = Decimal(str(price_usd))
            current_amount = Decimal(str(holding['amount']))
            
            # Check sufficient balance
            if current_amount < amount_decimal:
                conn.close()
                return {
                    'success': False,
                    'error': 'INSUFFICIENT_BALANCE',
                    'message': f'Insufficient balance. You have {current_amount} {crypto_id.upper()}'
                }
            
            total_received = amount_decimal * price_decimal
            sale_date = datetime.utcnow()
            new_amount = current_amount - amount_decimal
            
            # Update or delete holding
            if new_amount == 0:
                cursor.execute('DELETE FROM holdings WHERE user_id = ? AND crypto_id = ?',
                             (user_id, crypto_id))
            else:
                cursor.execute('''
                    UPDATE holdings SET amount = ?, updated_at = ?
                    WHERE user_id = ? AND crypto_id = ?
                ''', (float(new_amount), sale_date.isoformat(), user_id, crypto_id))
            
            # Create transaction record
            transaction_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO transactions (transaction_id, user_id, crypto_id, type, amount,
                                        price_usd, total_usd, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (transaction_id, user_id, crypto_id, 'SELL', float(amount_decimal),
                  float(price_decimal), float(total_received), sale_date.isoformat(), 'COMPLETED'))
            
            conn.commit()
            
            # Create portfolio snapshot
            self._create_portfolio_snapshot(user_id, cursor)
            conn.commit()
            conn.close()
            
            transaction = {
                'transaction_id': transaction_id,
                'user_id': user_id,
                'crypto_id': crypto_id,
                'type': 'SELL',
                'amount': float(amount_decimal),
                'price_usd': float(price_decimal),
                'total_usd': float(total_received),
                'timestamp': sale_date.isoformat(),
                'sale_date': sale_date.isoformat(),
                'status': 'COMPLETED'
            }
            
            return {
                'success': True,
                'transaction': transaction,
                'new_balance': float(new_amount),
                'total_received': float(total_received),
                'message': f'Successfully sold {amount} {crypto_id.upper()}'
            }
        
        except Exception as e:
            return {'success': False, 'error': 'SELL_FAILED', 'message': str(e)}
    
    def get_transaction_history(self, user_id, limit=50):
        """Get user's transaction history from database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM transactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))
            
            transactions = cursor.fetchall()
            conn.close()
            
            transaction_list = [dict(tx) for tx in transactions]
            
            return {
                'success': True,
                'transactions': transaction_list,
                'total_count': len(transaction_list)
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def get_portfolio_value(self, user_id, current_prices):
        """Calculate total portfolio value with current prices"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM holdings WHERE user_id = ?
            ''', (user_id,))
            
            holdings = cursor.fetchall()
            conn.close()
            
            if not holdings:
                return {'success': True, 'total_value': 0, 'holdings': []}
            
            total_value = Decimal('0')
            holdings_list = []
            
            for holding in holdings:
                crypto_id = holding['crypto_id']
                amount = Decimal(str(holding['amount']))
                avg_price = Decimal(str(holding['avg_price']))
                total_invested = Decimal(str(holding['total_invested']))
                
                current_price = Decimal(str(current_prices.get(crypto_id, 0)))
                value = amount * current_price
                total_value += value
                
                profit_loss = value - total_invested
                profit_loss_pct = (profit_loss / total_invested * 100) if total_invested > 0 else Decimal('0')
                
                holdings_list.append({
                    'crypto_id': crypto_id,
                    'amount': float(amount),
                    'avg_price': float(avg_price),
                    'current_price': float(current_price),
                    'current_value': float(value),
                    'total_invested': float(total_invested),
                    'profit_loss': float(profit_loss),
                    'profit_loss_pct': float(profit_loss_pct),
                    'first_purchase_date': holding['first_purchase_date']
                })
            
            return {
                'success': True,
                'total_value': float(total_value),
                'holdings': holdings_list
            }
        except Exception as e:
            return {'success': False, 'error': 'CALCULATION_FAILED', 'message': str(e)}
    
    def _create_portfolio_snapshot(self, user_id, cursor=None):
        """Create a snapshot of portfolio for historical tracking"""
        try:
            should_close = False
            if cursor is None:
                conn = get_db_connection()
                cursor = conn.cursor()
                should_close = True
            
            # Get current holdings
            cursor.execute('SELECT * FROM holdings WHERE user_id = ?', (user_id,))
            holdings = cursor.fetchall()
            
            holdings_dict = {}
            total_value = 0
            
            for holding in holdings:
                holdings_dict[holding['crypto_id']] = {
                    'amount': holding['amount'],
                    'avg_price': holding['avg_price'],
                    'total_invested': holding['total_invested']
                }
                total_value += holding['amount'] * holding['avg_price']
            
            snapshot_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            cursor.execute('''
                INSERT INTO portfolio_snapshots (snapshot_id, user_id, timestamp, total_value, holdings_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (snapshot_id, user_id, timestamp, total_value, json.dumps(holdings_dict)))
            
            # Clean up old snapshots (keep last 90 days)
            cutoff_date = (datetime.utcnow() - timedelta(days=90)).isoformat()
            cursor.execute('''
                DELETE FROM portfolio_snapshots
                WHERE user_id = ? AND timestamp < ?
            ''', (user_id, cutoff_date))
            
            if should_close:
                conn.commit()
                conn.close()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': 'SNAPSHOT_FAILED', 'message': str(e)}
    
    def get_portfolio_performance_history(self, user_id, days=30, current_prices=None):
        """Get portfolio performance over time"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT * FROM portfolio_snapshots
                WHERE user_id = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            ''', (user_id, start_date))
            
            snapshots = cursor.fetchall()
            conn.close()
            
            if not snapshots:
                return {'success': True, 'performance': [], 'message': 'No historical data available'}
            
            performance = []
            for snapshot in snapshots:
                holdings = json.loads(snapshot['holdings_json'])
                performance.append({
                    'timestamp': snapshot['timestamp'],
                    'total_value': snapshot['total_value'],
                    'holdings_count': len(holdings)
                })
            
            return {
                'success': True,
                'performance': performance,
                'days': days
            }
        except Exception as e:
            return {'success': False, 'error': 'PERFORMANCE_FETCH_FAILED', 'message': str(e)}
    
    # Portfolio Alert Methods
    def create_portfolio_alert(self, user_id, alert_type, threshold_value):
        """Create portfolio-level alert"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            alert_id = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()
            
            cursor.execute('''
                INSERT INTO portfolio_alerts (alert_id, user_id, alert_type, threshold_value,
                                            status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (alert_id, user_id, alert_type, threshold_value, 'ACTIVE', created_at))
            
            conn.commit()
            conn.close()
            
            alert = {
                'alert_id': alert_id,
                'user_id': user_id,
                'alert_type': alert_type,
                'threshold_value': threshold_value,
                'created_at': created_at,
                'status': 'ACTIVE',
                'last_triggered': None
            }
            
            return {
                'success': True,
                'alert': alert,
                'message': 'Portfolio alert created successfully'
            }
        except Exception as e:
            return {'success': False, 'error': 'ALERT_CREATE_FAILED', 'message': str(e)}
    
    def get_portfolio_alerts(self, user_id):
        """Get all portfolio alerts for a user"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM portfolio_alerts WHERE user_id = ?
            ''', (user_id,))
            
            alerts = cursor.fetchall()
            conn.close()
            
            alert_list = [dict(alert) for alert in alerts]
            
            return {
                'success': True,
                'alerts': alert_list
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def delete_portfolio_alert(self, alert_id, user_id):
        """Delete a portfolio alert"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM portfolio_alerts
                WHERE alert_id = ? AND user_id = ?
            ''', (alert_id, user_id))
            
            if cursor.rowcount == 0:
                conn.close()
                return {'success': False, 'error': 'ALERT_NOT_FOUND', 'message': 'Alert not found'}
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'Alert deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': 'DELETE_FAILED', 'message': str(e)}
