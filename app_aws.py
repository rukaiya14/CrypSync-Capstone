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

# Load environment variables
load_dotenv()

# Import services
from services.auth_service_aws import AuthServiceAWS
from services.price_service import PriceService
from services.alert_service_aws import AlertServiceAWS
from services.historical_service_aws import HistoricalServiceAWS
from services.visualization_service import VisualizationService
from services.notification_service import NotificationService

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
    return redirect(url_for('login'))

@application.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        result = auth_service.register_user(data['email'], data['password'])
        send_metric('UserRegistration', 1 if result['success'] else 0)
        return jsonify(result)
    return render_template('signup.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        result = auth_service.authenticate_user(data['email'], data['password'])
        if result['success']:
            session['session_token'] = result['session_token']
            session['user_id'] = result['user_id']
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
    return render_template('home.html')

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

@application.route('/charts')
@login_required
def charts():
    return render_template('charts.html')

@application.route('/about')
def about():
    return render_template('about.html')

@application.route('/admin')
@login_required
def admin():
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
    return render_template('500.html'), 500

if __name__ == '__main__':
    application.run(debug=False, host='0.0.0.0', port=8080)
