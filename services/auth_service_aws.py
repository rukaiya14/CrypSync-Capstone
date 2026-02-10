"""
Authentication Service - AWS DynamoDB Implementation
"""
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
import os
from decimal import Decimal

class AuthServiceAWS:
    def __init__(self, dynamodb):
        self.dynamodb = dynamodb
        self.table_name = os.getenv('DYNAMODB_USERS_TABLE', 'crypsync-users-production')
        self.table = dynamodb.Table(self.table_name)
        self.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
        self.sessions = {}  # In-memory session cache
    
    def register_user(self, email, password):
        """Register a new user"""
        try:
            # Check if user exists using GSI
            response = self.table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            if response['Items']:
                return {'success': False, 'error': 'USER_EXISTS', 'message': 'User already exists'}
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')
            
            # Create user
            user_id = str(uuid.uuid4())
            self.table.put_item(
                Item={
                    'user_id': user_id,
                    'email': email,
                    'password_hash': password_hash,
                    'created_at': datetime.utcnow().isoformat(),
                    'last_login': None
                }
            )
            
            return {'success': True, 'user_id': user_id, 'message': 'User registered successfully'}
        
        except Exception as e:
            return {'success': False, 'error': 'REGISTRATION_FAILED', 'message': str(e)}
    
    def authenticate_user(self, email, password):
        """Authenticate user and create session"""
        try:
            # Get user by email
            response = self.table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            
            if not response['Items']:
                return {'success': False, 'error': 'INVALID_CREDENTIALS', 'message': 'Invalid email or password'}
            
            user = response['Items'][0]
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return {'success': False, 'error': 'INVALID_CREDENTIALS', 'message': 'Invalid email or password'}
            
            # Update last login
            self.table.update_item(
                Key={'user_id': user['user_id']},
                UpdateExpression='SET last_login = :login_time',
                ExpressionAttributeValues={':login_time': datetime.utcnow().isoformat()}
            )
            
            # Create JWT token
            session_token = jwt.encode({
                'user_id': user['user_id'],
                'email': email,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }, self.secret_key, algorithm='HS256')
            
            # Cache session
            self.sessions[session_token] = {
                'user_id': user['user_id'],
                'email': email
            }
            
            return {
                'success': True,
                'session_token': session_token,
                'user_id': user['user_id'],
                'email': email,
                'message': 'Login successful'
            }
        
        except Exception as e:
            return {'success': False, 'error': 'AUTHENTICATION_FAILED', 'message': str(e)}
    
    def validate_session(self, session_token):
        """Validate session token"""
        try:
            payload = jwt.decode(session_token, self.secret_key, algorithms=['HS256'])
            return {
                'success': True,
                'user_id': payload['user_id'],
                'email': payload['email']
            }
        except jwt.ExpiredSignatureError:
            return {'success': False, 'error': 'SESSION_EXPIRED', 'message': 'Session has expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'error': 'INVALID_TOKEN', 'message': 'Invalid session token'}
        except Exception as e:
            return {'success': False, 'error': 'VALIDATION_FAILED', 'message': str(e)}
    
    def logout_user(self, session_token):
        """Invalidate session"""
        try:
            if session_token in self.sessions:
                del self.sessions[session_token]
            return {'success': True, 'message': 'Logout successful'}
        except Exception as e:
            return {'success': False, 'error': 'LOGOUT_FAILED', 'message': str(e)}
