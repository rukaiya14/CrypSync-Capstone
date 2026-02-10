"""
CrypSync - Cryptocurrency Real-Time Price Tracker
Main Flask application entry point
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize database
from database import init_database, create_admin_user
init_database()
create_admin_user()  # Create default admin user

# Import services
from services.auth_service import AuthService
from services.price_service import PriceService
from services.alert_service import AlertService
from services.historical_service import HistoricalService
from services.visualization_service import VisualizationService
from services.portfolio_service_db import PortfolioService
from services.admin_service import AdminService

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize services
auth_service = AuthService()
price_service = PriceService()
alert_service = AlertService()
historical_service = HistoricalService()
visualization_service = VisualizationService()
portfolio_service = PortfolioService()
admin_service = AdminService()

# Mock notification service for local development
class MockNotificationService:
    def send_trade_notification(self, email, transaction):
        print(f"[MOCK EMAIL] Trade notification sent to {email}")
        print(f"Transaction: {transaction['type']} {transaction['amount']} {transaction['crypto_id']} @ ${transaction['price_usd']}")
        return {'success': True, 'message': 'Mock notification sent'}

notification_service = MockNotificationService()

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

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'session_token' not in session:
            return redirect(url_for('login'))
        
        result = auth_service.validate_session(session['session_token'])
        if not result['success']:
            session.clear()
            return redirect(url_for('login'))
        
        if not admin_service.is_admin(session['user_id']):
            return jsonify({'success': False, 'error': 'UNAUTHORIZED', 'message': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        result = auth_service.register_user(data['email'], data['password'])
        return jsonify(result)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        result = auth_service.authenticate_user(data['email'], data['password'])
        if result['success']:
            session['session_token'] = result['session_token']
            session['user_id'] = result['user_id']
            session['email'] = result['email']
            session['role'] = data.get('role', 'user')  # Store selected role
            # Check if user is admin in database
            session['is_admin'] = admin_service.is_admin(result['user_id'])
        return jsonify(result)
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'session_token' in session:
        auth_service.logout_user(session['session_token'])
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    # Get user's portfolio
    portfolio_result = portfolio_service.get_user_portfolio(user_id)
    return render_template('dashboard.html', portfolio=portfolio_result.get('portfolio', {}))

@app.route('/analyst')
@login_required
def analyst_dashboard():
    return render_template('analyst_dashboard.html')

@app.route('/api/prices')
@login_required
def get_prices():
    crypto_ids = request.args.get('ids', 'bitcoin,ethereum').split(',')
    result = price_service.get_current_prices(crypto_ids)
    return jsonify(result)

@app.route('/api/alerts', methods=['GET', 'POST', 'DELETE'])
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
        return jsonify(result)
    
    elif request.method == 'DELETE':
        alert_id = request.args.get('alert_id')
        result = alert_service.delete_alert(alert_id, user_id)
        return jsonify(result)

@app.route('/api/historical')
@login_required
def get_historical():
    crypto_id = request.args.get('crypto_id', 'bitcoin')
    days = int(request.args.get('days', 7))
    
    result = historical_service.get_historical_data(crypto_id, days)
    if result['success']:
        chart_data = visualization_service.prepare_chart_data(result['data'])
        return jsonify({'success': True, 'data': chart_data})
    return jsonify(result)

@app.route('/historical')
@login_required
def historical():
    return render_template('historical.html')

@app.route('/alerts')
@login_required
def alerts():
    return render_template('alerts.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
@login_required
def portfolio():
    return render_template('portfolio.html')

@app.route('/trading')
@login_required
def trading():
    return render_template('trading.html')

@app.route('/watchlist')
@login_required
def watchlist():
    return render_template('watchlist.html')

@app.route('/crypto/<crypto_id>')
def crypto_detail(crypto_id):
    return render_template('crypto_detail.html', crypto_id=crypto_id)

# Portfolio API endpoints
@app.route('/api/portfolio', methods=['GET'])
@login_required
def get_portfolio():
    user_id = session['user_id']
    result = portfolio_service.get_user_portfolio(user_id)
    
    if result['success'] and result['portfolio']:
        # Get current prices for portfolio value calculation
        crypto_ids = list(result['portfolio'].keys())
        prices_result = price_service.get_current_prices(crypto_ids)
        
        if prices_result['success']:
            current_prices = {k: v['price_usd'] for k, v in prices_result['data'].items()}
            value_result = portfolio_service.get_portfolio_value(user_id, current_prices)
            result['portfolio_value'] = value_result
    
    return jsonify(result)

@app.route('/api/portfolio/buy', methods=['POST'])
@login_required
def buy_crypto():
    user_id = session['user_id']
    user_email = session.get('email', 'user@example.com')
    data = request.get_json()
    
    # Get current price
    price_result = price_service.get_current_prices([data['crypto_id']])
    if not price_result['success']:
        return jsonify({'success': False, 'error': 'PRICE_FETCH_FAILED', 'message': 'Could not fetch current price'})
    
    current_price = price_result['data'][data['crypto_id']]['price_usd']
    
    # Execute buy
    result = portfolio_service.buy_crypto(
        user_id,
        data['crypto_id'],
        data['amount'],
        current_price
    )
    
    # Send notification if successful
    if result['success']:
        notification_service.send_trade_notification(user_email, result['transaction'])
    
    return jsonify(result)

@app.route('/api/portfolio/sell', methods=['POST'])
@login_required
def sell_crypto():
    user_id = session['user_id']
    user_email = session.get('email', 'user@example.com')
    data = request.get_json()
    
    # Get current price
    price_result = price_service.get_current_prices([data['crypto_id']])
    if not price_result['success']:
        return jsonify({'success': False, 'error': 'PRICE_FETCH_FAILED', 'message': 'Could not fetch current price'})
    
    current_price = price_result['data'][data['crypto_id']]['price_usd']
    
    # Execute sell
    result = portfolio_service.sell_crypto(
        user_id,
        data['crypto_id'],
        data['amount'],
        current_price
    )
    
    # Send notification if successful
    if result['success']:
        notification_service.send_trade_notification(user_email, result['transaction'])
    
    return jsonify(result)

@app.route('/api/portfolio/transactions', methods=['GET'])
@login_required
def get_transactions():
    user_id = session['user_id']
    limit = int(request.args.get('limit', 50))
    result = portfolio_service.get_transaction_history(user_id, limit)
    return jsonify(result)

# Portfolio Alert endpoints (Scenario 1)
@app.route('/api/portfolio/alerts', methods=['GET', 'POST', 'DELETE'])
@login_required
def manage_portfolio_alerts():
    user_id = session['user_id']
    
    if request.method == 'GET':
        result = portfolio_service.get_portfolio_alerts(user_id)
        return jsonify(result)
    
    elif request.method == 'POST':
        data = request.get_json()
        result = portfolio_service.create_portfolio_alert(
            user_id,
            data['alert_type'],
            data['threshold_value']
        )
        return jsonify(result)
    
    elif request.method == 'DELETE':
        alert_id = request.args.get('alert_id')
        result = portfolio_service.delete_portfolio_alert(alert_id, user_id)
        return jsonify(result)

# Portfolio Performance History endpoint (Scenario 2)
@app.route('/api/portfolio/performance', methods=['GET'])
@login_required
def get_portfolio_performance():
    user_id = session['user_id']
    days = int(request.args.get('days', 30))
    
    result = portfolio_service.get_portfolio_performance_history(user_id, days)
    return jsonify(result)

# Admin Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    result = admin_service.get_all_users()
    return jsonify(result)

@app.route('/api/admin/statistics', methods=['GET'])
@admin_required
def get_statistics():
    result = admin_service.get_user_statistics()
    return jsonify(result)

@app.route('/api/admin/coins', methods=['GET'])
@admin_required
def get_tracked_coins():
    result = admin_service.get_tracked_coins()
    return jsonify(result)

@app.route('/api/admin/coins/add', methods=['POST'])
@admin_required
def add_coin():
    data = request.get_json()
    result = admin_service.add_tracked_coin(
        data['coin_id'],
        data['name'],
        data['symbol'],
        session['user_id']
    )
    return jsonify(result)

@app.route('/api/admin/coins/remove', methods=['POST'])
@admin_required
def remove_coin():
    data = request.get_json()
    result = admin_service.remove_tracked_coin(data['coin_id'])
    return jsonify(result)

@app.route('/api/admin/transactions', methods=['GET'])
@admin_required
def get_all_transactions():
    limit = int(request.args.get('limit', 50))
    result = admin_service.get_recent_transactions(limit)
    return jsonify(result)

@app.route('/api/admin/users/delete', methods=['POST'])
@admin_required
def delete_user():
    data = request.get_json()
    result = admin_service.delete_user(data['user_id'])
    return jsonify(result)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('404.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
