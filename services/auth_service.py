"""
Authentication Service
Handles user registration, login, and session management with SQLite database
"""
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
import os
from database import get_db_connection

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    def register_user(self, email, password):
        """Register a new user with email and password"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT user_id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                conn.close()
                return {'success': False, 'error': 'USER_EXISTS', 'message': 'User already exists'}
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
            
            # Create user
            user_id = str(uuid.uuid4())
            created_at = datetime.utcnow().isoformat()
            
            cursor.execute('''
                INSERT INTO users (user_id, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, email, password_hash, created_at))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'user_id': user_id, 'message': 'User registered successfully'}
        
        except Exception as e:
            return {'success': False, 'error': 'REGISTRATION_FAILED', 'message': str(e)}
    
    def authenticate_user(self, email, password):
        """Authenticate user credentials and create session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if not user:
                conn.close()
                return {'success': False, 'error': 'INVALID_CREDENTIALS', 'message': 'Invalid email or password'}
            
            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
                conn.close()
                return {'success': False, 'error': 'INVALID_CREDENTIALS', 'message': 'Invalid email or password'}
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE user_id = ?', 
                         (datetime.utcnow().isoformat(), user['user_id']))
            
            # Create JWT token
            session_token = jwt.encode({
                'user_id': user['user_id'],
                'email': email,
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            }, self.secret_key, algorithm='HS256')
            
            # Store session
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_token, user_id, email, created_at)
                VALUES (?, ?, ?, ?)
            ''', (session_token, user['user_id'], email, datetime.utcnow().isoformat()))
            
            conn.commit()
            conn.close()
            
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
        """Validate session token and return associated user"""
        try:
            # Decode JWT
            payload = jwt.decode(session_token, self.secret_key, algorithms=['HS256'])
            
            # Check if session exists in database
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM sessions WHERE session_token = ?', (session_token,))
            session = cursor.fetchone()
            conn.close()
            
            if not session:
                return {'success': False, 'error': 'INVALID_TOKEN', 'message': 'Invalid session token'}
            
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
        """Invalidate user session"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
            conn.commit()
            conn.close()
            return {'success': True, 'message': 'Logout successful'}
        except Exception as e:
            return {'success': False, 'error': 'LOGOUT_FAILED', 'message': str(e)}
