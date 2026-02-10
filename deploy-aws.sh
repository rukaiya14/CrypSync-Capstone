#!/bin/bash

# CrypSync AWS Deployment Script
# This script deploys the application to AWS Elastic Beanstalk

set -e

echo "=== CrypSync AWS Deployment ==="

# Configuration
APP_NAME="crypsync"
ENV_NAME="crypsync-prod"
REGION="us-east-1"
STACK_NAME="crypsync-infrastructure"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo "Error: Elastic Beanstalk CLI is not installed. Please install it first."
    echo "Run: pip install awsebcli"
    exit 1
fi

echo "Step 1: Deploying CloudFormation infrastructure..."
aws cloudformation deploy \
    --template-file aws-infrastructure.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        EnvironmentName=production \
        ApplicationName=$APP_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

echo "Step 2: Getting stack outputs..."
USERS_TABLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`UsersTableName`].OutputValue' \
    --output text \
    --region $REGION)

ALERTS_TABLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`AlertsTableName`].OutputValue' \
    --output text \
    --region $REGION)

PRICES_TABLE=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`PricesTableName`].OutputValue' \
    --output text \
    --region $REGION)

echo "DynamoDB Tables created:"
echo "  Users: $USERS_TABLE"
echo "  Alerts: $ALERTS_TABLE"
echo "  Prices: $PRICES_TABLE"

echo "Step 3: Creating .env.aws file..."
cat > .env.aws << EOF
SECRET_KEY=$(openssl rand -hex 32)
FLASK_ENV=production
AWS_REGION=$REGION
DYNAMODB_USERS_TABLE=$USERS_TABLE
DYNAMODB_ALERTS_TABLE=$ALERTS_TABLE
DYNAMODB_PRICES_TABLE=$PRICES_TABLE
EOF

echo "Step 4: Initializing Elastic Beanstalk..."
if [ ! -d ".elasticbeanstalk" ]; then
    eb init $APP_NAME --platform python-3.9 --region $REGION
fi

echo "Step 5: Creating Elastic Beanstalk environment..."
if ! eb list | grep -q $ENV_NAME; then
    eb create $ENV_NAME \
        --instance-type t3.small \
        --envvars $(cat .env.aws | tr '\n' ',' | sed 's/,$//')
else
    echo "Environment $ENV_NAME already exists. Deploying update..."
    eb deploy $ENV_NAME
fi

echo "Step 6: Setting environment variables..."
eb setenv $(cat .env.aws | tr '\n' ' ')

echo "=== Deployment Complete ==="
echo "Application URL:"
eb status $ENV_NAME | grep CNAME

echo ""
echo "To view logs: eb logs $ENV_NAME"
echo "To open application: eb open $ENV_NAME"
echo "To terminate environment: eb terminate $ENV_NAME"
