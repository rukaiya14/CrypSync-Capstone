"""
Portfolio Service
Handles cryptocurrency portfolio management and trading with historical tracking
"""
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

class PortfolioService:
    def __init__(self):
        # In-memory storage (replace with DynamoDB in production)
        self.portfolios = {}  # user_id -> {crypto_id: {amount, avg_price, transactions}}
        self.transactions = {}  # transaction_id -> transaction details
        self.portfolio_snapshots = {}  # user_id -> [snapshots] for historical tracking
        self.portfolio_alerts = {}  # alert_id -> portfolio alert details
    
    def get_user_portfolio(self, user_id):
        """Get user's complete portfolio"""
        try:
            if user_id not in self.portfolios:
                return {'success': True, 'portfolio': {}, 'total_value': 0}
            
            portfolio = self.portfolios[user_id]
            return {
                'success': True,
                'portfolio': portfolio,
                'message': 'Portfolio retrieved successfully'
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def buy_crypto(self, user_id, crypto_id, amount, price_usd):
        """Buy cryptocurrency with timestamp tracking"""
        try:
            # Initialize user portfolio if doesn't exist
            if user_id not in self.portfolios:
                self.portfolios[user_id] = {}
            
            # Initialize crypto holding if doesn't exist
            if crypto_id not in self.portfolios[user_id]:
                self.portfolios[user_id][crypto_id] = {
                    'amount': Decimal('0'),
                    'avg_price': Decimal('0'),
                    'total_invested': Decimal('0'),
                    'transactions': [],
                    'first_purchase_date': None
                }
            
            holding = self.portfolios[user_id][crypto_id]
            amount_decimal = Decimal(str(amount))
            price_decimal = Decimal(str(price_usd))
            total_cost = amount_decimal * price_decimal
            purchase_date = datetime.utcnow()
            
            # Set first purchase date if this is the first buy
            if holding['first_purchase_date'] is None:
                holding['first_purchase_date'] = purchase_date.isoformat()
            
            # Calculate new average price
            old_total = holding['amount'] * holding['avg_price']
            new_total = old_total + total_cost
            new_amount = holding['amount'] + amount_decimal
            new_avg_price = new_total / new_amount if new_amount > 0 else Decimal('0')
            
            # Update holding
            holding['amount'] = new_amount
            holding['avg_price'] = new_avg_price
            holding['total_invested'] += total_cost
            
            # Create transaction record with purchase date
            transaction_id = str(uuid.uuid4())
            transaction = {
                'transaction_id': transaction_id,
                'user_id': user_id,
                'crypto_id': crypto_id,
                'type': 'BUY',
                'amount': float(amount_decimal),
                'price_usd': float(price_decimal),
                'total_usd': float(total_cost),
                'timestamp': purchase_date.isoformat(),
                'purchase_date': purchase_date.isoformat(),  # For historical tracking
                'status': 'COMPLETED'
            }
            
            self.transactions[transaction_id] = transaction
            holding['transactions'].append(transaction_id)
            
            # Create portfolio snapshot for historical tracking
            self._create_portfolio_snapshot(user_id)
            
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
        """Sell cryptocurrency with timestamp tracking"""
        try:
            # Check if user has portfolio
            if user_id not in self.portfolios:
                return {'success': False, 'error': 'NO_PORTFOLIO', 'message': 'No portfolio found'}
            
            # Check if user has this crypto
            if crypto_id not in self.portfolios[user_id]:
                return {'success': False, 'error': 'NO_HOLDING', 'message': f'No {crypto_id} holdings found'}
            
            holding = self.portfolios[user_id][crypto_id]
            amount_decimal = Decimal(str(amount))
            price_decimal = Decimal(str(price_usd))
            
            # Check if user has enough
            if holding['amount'] < amount_decimal:
                return {
                    'success': False,
                    'error': 'INSUFFICIENT_BALANCE',
                    'message': f'Insufficient balance. You have {holding["amount"]} {crypto_id.upper()}'
                }
            
            total_received = amount_decimal * price_decimal
            sale_date = datetime.utcnow()
            
            # Update holding
            holding['amount'] -= amount_decimal
            
            # Create transaction record
            transaction_id = str(uuid.uuid4())
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
            
            self.transactions[transaction_id] = transaction
            holding['transactions'].append(transaction_id)
            
            # Remove holding if balance is zero
            if holding['amount'] == 0:
                del self.portfolios[user_id][crypto_id]
            
            # Create portfolio snapshot for historical tracking
            self._create_portfolio_snapshot(user_id)
            
            return {
                'success': True,
                'transaction': transaction,
                'new_balance': float(holding['amount']) if crypto_id in self.portfolios[user_id] else 0,
                'total_received': float(total_received),
                'message': f'Successfully sold {amount} {crypto_id.upper()}'
            }
        
        except Exception as e:
            return {'success': False, 'error': 'SELL_FAILED', 'message': str(e)}
    
    def get_transaction_history(self, user_id, limit=50):
        """Get user's transaction history"""
        try:
            user_transactions = [
                tx for tx in self.transactions.values()
                if tx['user_id'] == user_id
            ]
            
            # Sort by timestamp descending
            user_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return {
                'success': True,
                'transactions': user_transactions[:limit],
                'total_count': len(user_transactions)
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def get_portfolio_value(self, user_id, current_prices):
        """Calculate total portfolio value with current prices"""
        try:
            if user_id not in self.portfolios:
                return {'success': True, 'total_value': 0, 'holdings': []}
            
            portfolio = self.portfolios[user_id]
            total_value = Decimal('0')
            holdings = []
            
            for crypto_id, holding in portfolio.items():
                current_price = Decimal(str(current_prices.get(crypto_id, 0)))
                value = holding['amount'] * current_price
                total_value += value
                
                profit_loss = value - holding['total_invested']
                profit_loss_pct = (profit_loss / holding['total_invested'] * 100) if holding['total_invested'] > 0 else Decimal('0')
                
                holdings.append({
                    'crypto_id': crypto_id,
                    'amount': float(holding['amount']),
                    'avg_price': float(holding['avg_price']),
                    'current_price': float(current_price),
                    'current_value': float(value),
                    'total_invested': float(holding['total_invested']),
                    'profit_loss': float(profit_loss),
                    'profit_loss_pct': float(profit_loss_pct),
                    'first_purchase_date': holding.get('first_purchase_date')
                })
            
            return {
                'success': True,
                'total_value': float(total_value),
                'holdings': holdings
            }
        except Exception as e:
            return {'success': False, 'error': 'CALCULATION_FAILED', 'message': str(e)}
    
    def _create_portfolio_snapshot(self, user_id):
        """Create a snapshot of portfolio for historical tracking (Scenario 2)"""
        try:
            if user_id not in self.portfolio_snapshots:
                self.portfolio_snapshots[user_id] = []
            
            snapshot = {
                'snapshot_id': str(uuid.uuid4()),
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat(),
                'holdings': {}
            }
            
            # Copy current holdings
            if user_id in self.portfolios:
                for crypto_id, holding in self.portfolios[user_id].items():
                    snapshot['holdings'][crypto_id] = {
                        'amount': float(holding['amount']),
                        'avg_price': float(holding['avg_price']),
                        'total_invested': float(holding['total_invested'])
                    }
            
            self.portfolio_snapshots[user_id].append(snapshot)
            
            # Keep only last 90 days of snapshots (for scalability)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            self.portfolio_snapshots[user_id] = [
                s for s in self.portfolio_snapshots[user_id]
                if datetime.fromisoformat(s['timestamp']) >= cutoff_date
            ]
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': 'SNAPSHOT_FAILED', 'message': str(e)}
    
    def get_portfolio_performance_history(self, user_id, days=30, current_prices=None):
        """Get portfolio performance over time (Scenario 2)"""
        try:
            if user_id not in self.portfolio_snapshots:
                return {'success': True, 'performance': [], 'message': 'No historical data available'}
            
            start_date = datetime.utcnow() - timedelta(days=days)
            snapshots = [
                s for s in self.portfolio_snapshots[user_id]
                if datetime.fromisoformat(s['timestamp']) >= start_date
            ]
            
            # Sort by timestamp
            snapshots.sort(key=lambda x: x['timestamp'])
            
            performance = []
            for snapshot in snapshots:
                # Calculate portfolio value at that time
                # In production, you'd fetch historical prices from CoinGecko or store them
                total_value = sum(
                    holding['amount'] * holding['avg_price']
                    for holding in snapshot['holdings'].values()
                )
                
                performance.append({
                    'timestamp': snapshot['timestamp'],
                    'total_value': total_value,
                    'holdings_count': len(snapshot['holdings'])
                })
            
            return {
                'success': True,
                'performance': performance,
                'days': days
            }
        except Exception as e:
            return {'success': False, 'error': 'PERFORMANCE_FETCH_FAILED', 'message': str(e)}
    
    # Portfolio Alert Methods (Scenario 1)
    def create_portfolio_alert(self, user_id, alert_type, threshold_value):
        """Create portfolio-level alert (Scenario 1)"""
        try:
            alert_id = str(uuid.uuid4())
            alert = {
                'alert_id': alert_id,
                'user_id': user_id,
                'alert_type': alert_type,  # 'VALUE_BELOW', 'VALUE_ABOVE', 'PROFIT_LOSS_THRESHOLD'
                'threshold_value': float(threshold_value),
                'created_at': datetime.utcnow().isoformat(),
                'status': 'ACTIVE',
                'last_triggered': None
            }
            
            self.portfolio_alerts[alert_id] = alert
            
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
            user_alerts = [
                alert for alert in self.portfolio_alerts.values()
                if alert['user_id'] == user_id
            ]
            
            return {
                'success': True,
                'alerts': user_alerts
            }
        except Exception as e:
            return {'success': False, 'error': 'FETCH_FAILED', 'message': str(e)}
    
    def check_portfolio_alerts(self, user_id, current_portfolio_value, profit_loss):
        """Check if any portfolio alerts should be triggered"""
        try:
            triggered_alerts = []
            
            for alert_id, alert in self.portfolio_alerts.items():
                if alert['user_id'] != user_id or alert['status'] != 'ACTIVE':
                    continue
                
                should_trigger = False
                
                if alert['alert_type'] == 'VALUE_BELOW' and current_portfolio_value < alert['threshold_value']:
                    should_trigger = True
                elif alert['alert_type'] == 'VALUE_ABOVE' and current_portfolio_value > alert['threshold_value']:
                    should_trigger = True
                elif alert['alert_type'] == 'PROFIT_LOSS_THRESHOLD':
                    if profit_loss < 0 and abs(profit_loss) >= alert['threshold_value']:
                        should_trigger = True
                
                if should_trigger:
                    alert['last_triggered'] = datetime.utcnow().isoformat()
                    triggered_alerts.append(alert)
            
            return {
                'success': True,
                'triggered_alerts': triggered_alerts
            }
        except Exception as e:
            return {'success': False, 'error': 'CHECK_FAILED', 'message': str(e)}
    
    def delete_portfolio_alert(self, alert_id, user_id):
        """Delete a portfolio alert"""
        try:
            if alert_id not in self.portfolio_alerts:
                return {'success': False, 'error': 'ALERT_NOT_FOUND', 'message': 'Alert not found'}
            
            alert = self.portfolio_alerts[alert_id]
            if alert['user_id'] != user_id:
                return {'success': False, 'error': 'UNAUTHORIZED', 'message': 'Unauthorized'}
            
            del self.portfolio_alerts[alert_id]
            
            return {'success': True, 'message': 'Alert deleted successfully'}
        except Exception as e:
            return {'success': False, 'error': 'DELETE_FAILED', 'message': str(e)}
