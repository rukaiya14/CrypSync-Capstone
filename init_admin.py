#!/usr/bin/env python3
"""
Initialize Admin User for CrypSync
Creates an admin user in the database
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if running in AWS mode
if os.getenv('DYNAMODB_USERS_TABLE'):
    import boto3
    from services.auth_service_aws import AuthServiceAWS
    
    print("Initializing admin user in AWS DynamoDB...")
    dynamodb = boto3.resource('dynamodb', region_name=os.getenv('AWS_REGION', 'us-east-1'))
    auth_service = AuthServiceAWS(dynamodb)
else:
    from services.auth_service import AuthService
    
    print("Initializing admin user in local storage...")
    auth_service = AuthService()

def create_admin_user():
    """Create admin user"""
    print("\n=== CrypSync Admin User Creation ===\n")
    
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    confirm_password = input("Confirm password: ")
    
    if password != confirm_password:
        print("Error: Passwords do not match!")
        sys.exit(1)
    
    if len(password) < 8:
        print("Error: Password must be at least 8 characters!")
        sys.exit(1)
    
    print("\nCreating admin user...")
    result = auth_service.register_user(email, password)
    
    if result['success']:
        print(f"\n✓ Admin user created successfully!")
        print(f"  User ID: {result['user_id']}")
        print(f"  Email: {email}")
        print("\nYou can now login with these credentials.")
    else:
        print(f"\n✗ Failed to create admin user: {result['message']}")
        sys.exit(1)

if __name__ == '__main__':
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
