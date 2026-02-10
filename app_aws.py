"""
CrypSync - AWS Production Application
Flask application configured for AWS Elastic Beanstalk deployment
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# Load environment variables
load_dotenv()

# --- Initialize AWS services ---
# Use os.getenv to keep your code flexible for Scenario 3 (Scalability)
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
USERS_TABLE = os.getenv('DYNAMODB_USERS_TABLE', 'Users')
PRICES_TABLE = os.getenv('DYNAMODB_PRICES_TABLE', 'CryptoPrices')
ALERTS_TABLE = os.getenv('DYNAMODB_ALERTS_TABLE', 'PriceAlerts')

# Initialize Clients and Resources
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
sns_client = boto3.client('sns', region_name=os.getenv('AWS_REGION', 'us-east-1'))
cloudwatch = boto3.client('cloudwatch', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Import services
from services.auth_service_aws import AuthServiceAWS
from services.price_service import PriceService
from services.alert_service_aws import AlertServiceAWS
from services.historical_service_aws import HistoricalServiceAWS
from services.visualization_service import VisualizationService
from services.notification_service import NotificationService
from services.portfolio_service_aws import PortfolioServiceAWS

# Initialize Flask app
application = Flask(__name__)
application.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize AWS services
dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
cloudwatch = boto3.client('cloudwatch', region_name=os.getenv('AWS_REGION', 'us-east-1'))
ses = boto3.client('ses', region_name=os.getenv('AWS_REGION', 'us-east-1'))

# Initialize application services
auth_service = AuthServiceAWS(dynamodb)
price_service = PriceService()
alert_service = AlertServiceAWS(dynamodb)
historical_service = HistoricalServiceAWS(dynamodb)
visualization_service = VisualizationService()
notification_service = NotificationService(ses)
portfolio_service = PortfolioServiceAWS(dynamodb)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            return redirect(url_for('login'))
        
        result = auth_service.validate_session(session['session_token'])
        if not result['success']:
            session.clear()
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# CloudWatch metrics helper
def send_metric(metric_name, value, unit='Count'):
    try:
        cloudwatch.put_metric_data(
            Namespace='CrypSync',
            MetricData=[
                {
                    'MetricName': metric_name,
                    'Value': value,
                    'Unit': unit
                }
            ]
        )
    except Exception as e:
        print(f"Failed to send CloudWatch metric: {e}")

# Routes
@application.route('/')
def index():
    if 'session_token' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@application.route('/home')
def home():
    return render_template('home.html')

@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        result = auth_service.register_user(data['email'], data['password'])
        send_metric('UserRegistration', 1 if result['success'] else 0)
        return jsonify(result)
    return render_template('register.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        result = auth_service.authenticate_user(data['email'], data['password'])
        if result['success']:
            session['session_token'] = result['session_token']
            session['user_id'] = result['user_id']
            session['email'] = result['email']
            send_metric('UserLogin', 1)
        return jsonify(result)
    return render_template('login.html')

@application.route('/logout')
def logout():
    if 'session_token' in session:
        auth_service.logout_user(session['session_token'])
    session.clear()
    return redirect(url_for('login'))

@application.route('/dashboard')
@login_required
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Dashboard error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@application.route('/api/prices')
@login_required
def get_prices():
    crypto_ids = request.args.get('ids', 'bitcoin,ethereum').split(',')
    result = price_service.get_current_prices(crypto_ids)
    
    # Store prices in historical database
    if result['success']:
        for crypto_id, price_data in result['data'].items():
            historical_service.store_price_snapshot(
                crypto_id,
                price_data['price_usd']
            )
    
    send_metric('PriceAPICall', 1)
    return jsonify(result)

@application.route('/api/alerts', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_alerts():
    user_id = session['user_id']
    
    if request.method == 'GET':
        result = alert_service.get_user_alerts(user_id)
        return jsonify(result)
    
    elif request.method == 'POST':
        data = request.get_json()
        result = alert_service.create_alert(
            user_id,
            data['crypto_id'],
            data['threshold'],
            data['alert_type']
        )
        send_metric('AlertCreated', 1 if result['success'] else 0)
        return jsonify(result)
    
    elif request.method == 'DELETE':
        alert_id = request.args.get('alert_id')
        result = alert_service.delete_alert(alert_id, user_id)
        return jsonify(result)

@application.route('/api/historical')
@login_required
def get_historical():
    crypto_id = request.args.get('crypto_id', 'bitcoin')
    days = int(request.args.get('days', 7))
    
    result = historical_service.get_historical_data(crypto_id, days)
    if result['success']:
        chart_data = visualization_service.prepare_chart_data(result['data'])
        return jsonify({'success': True, 'data': chart_data})
    return jsonify(result)

@application.route('/api/portfolio', methods=['GET'])
@login_required
def get_portfolio():
    try:
        user_id = session['user_id']
        result = portfolio_service.get_user_portfolio(user_id)
        
        if not result['success']:
            return jsonify(result)
        
        # Get current prices for all holdings
        holdings = result.get('holdings', [])
        if holdings:
            crypto_ids = [h['crypto_id'] for h in holdings]
            price_result = price_service.get_current_prices(crypto_ids)
            
            if price_result['success']:
                current_prices = price_result['data']
                
                # Calculate portfolio value
                total_value = 0
                holdings_with_prices = []
                
                for holding in holdings:
                    crypto_id = holding['crypto_id']
                    if crypto_id in current_prices:
                        current_price = current_prices[crypto_id]['price_usd']
                        current_value = holding['total_amount'] * current_price
                        profit_loss = current_value - holding['total_invested']
                        profit_loss_pct = (profit_loss / holding['total_invested'] * 100) if holding['total_invested'] > 0 else 0
                        
                        holdings_with_prices.append({
                            'crypto_id': crypto_id,
                            'amount': holding['total_amount'],
                            'avg_price': holding['avg_buy_price'],
                            'current_price': current_price,
                            'current_value': current_value,
                            'total_invested': holding['total_invested'],
                            'profit_loss': profit_loss,
                            'profit_loss_pct': profit_loss_pct
                        })
                        
                        total_value += current_value
                
                return jsonify({
                    'success': True,
                    'portfolio': {h['crypto_id']: h for h in holdings_with_prices},
                    'portfolio_value': {
                        'total_value': total_value,
                        'holdings': holdings_with_prices
                    },
                    'transactions': result.get('transactions', [])
                })
        
        # Empty portfolio
        return jsonify({
            'success': True,
            'portfolio': {},
            'portfolio_value': {'total_value': 0, 'holdings': []},
            'transactions': []
        })
        
    except Exception as e:
        print(f"Portfolio fetch error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'PORTFOLIO_ERROR', 'message': str(e)})

@application.route('/api/portfolio/buy', methods=['POST'])
@login_required
def buy_crypto():
    user_id = session['user_id']
    data = request.get_json()
    
    # Get price from request or fetch current price
    price = data.get('price') or data.get('purchase_price') or data.get('price_usd')
    if not price:
        # Fetch current price if not provided
        crypto_id = data['crypto_id']
        price_result = price_service.get_current_prices([crypto_id])
        if price_result['success'] and crypto_id in price_result['data']:
            price = price_result['data'][crypto_id]['price_usd']
        else:
            return jsonify({'success': False, 'error': 'PRICE_NOT_FOUND', 'message': 'Could not determine price'})
    
    result = portfolio_service.add_transaction(
        user_id,
        data['crypto_id'],
        'BUY',
        float(data['amount']),
        float(price)
    )
    
    # Send SNS notification
    if result['success']:
        try:
            user_email = session.get('email', 'user')
            total_cost = float(data['amount']) * float(price)
            message = f"""
CrypSync Transaction Notification

Transaction Type: BUY
Cryptocurrency: {data['crypto_id'].upper()}
Amount: {data['amount']}
Price per unit: ${price:,.2f}
Total Cost: ${total_cost:,.2f}
User: {user_email}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Thank you for using CrypSync!
"""
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f'CrypSync: BUY {data["crypto_id"].upper()}',
                Message=message
            )
        except Exception as e:
            print(f"Failed to send SNS notification: {e}")
    
    send_metric('CryptoPurchase', 1 if result['success'] else 0)
    return jsonify(result)

@application.route('/api/portfolio/sell', methods=['POST'])
@login_required
def sell_crypto():
    user_id = session['user_id']
    data = request.get_json()
    
    # Get price from request or fetch current price
    price = data.get('price') or data.get('sale_price')
    if not price:
        # Fetch current price if not provided
        crypto_id = data['crypto_id']
        price_result = price_service.get_current_prices([crypto_id])
        if price_result['success'] and crypto_id in price_result['data']:
            price = price_result['data'][crypto_id]['price_usd']
        else:
            return jsonify({'success': False, 'error': 'PRICE_NOT_FOUND', 'message': 'Could not determine price'})
    
    result = portfolio_service.add_transaction(
        user_id,
        data['crypto_id'],
        'SELL',
        float(data['amount']),
        float(price)
    )
    
    # Send SNS notification
    if result['success']:
        try:
            user_email = session.get('email', 'user')
            total_revenue = float(data['amount']) * float(price)
            message = f"""
CrypSync Transaction Notification

Transaction Type: SELL
Cryptocurrency: {data['crypto_id'].upper()}
Amount: {data['amount']}
Price per unit: ${price:,.2f}
Total Revenue: ${total_revenue:,.2f}
User: {user_email}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Thank you for using CrypSync!
"""
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f'CrypSync: SELL {data["crypto_id"].upper()}',
                Message=message
            )
        except Exception as e:
            print(f"Failed to send SNS notification: {e}")
    
    send_metric('CryptoSale', 1 if result['success'] else 0)
    return jsonify(result)

@application.route('/charts')
@login_required
def charts():
    return render_template('charts.html')

@application.route('/about')
def about():
    return render_template('about.html')

@application.route('/portfolio')
@login_required
def portfolio():
    return render_template('portfolio.html')

@application.route('/trading')
@login_required
def trading():
    return render_template('trading.html')

@application.route('/watchlist')
@login_required
def watchlist():
    return render_template('watchlist.html')

@application.route('/alerts')
@login_required
def alerts():
    return render_template('alerts.html')

@application.route('/historical')
@login_required
def historical():
    return render_template('historical.html')

@application.route('/analyst')
@login_required
def analyst_dashboard():
    return render_template('analyst_dashboard.html')

@application.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@application.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'CrypSync'}), 200

# Error handlers
@application.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@application.errorhandler(500)
def internal_error(error):
    import traceback
    print("500 Error occurred:")
    print(traceback.format_exc())
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500

if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5000)
