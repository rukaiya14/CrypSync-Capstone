# CrypSync - AWS Deployment Guide

Complete guide for deploying CrypSync to AWS Elastic Beanstalk with DynamoDB.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users / Analysts                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Elastic Beanstalk                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Flask Web Application (Auto-scaled)          │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │   Auth      │  │    Price     │  │   Historical    │  │  │
│  │  │  Service    │  │   Service    │  │     Service     │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │   Alert     │  │  Notification│  │   Visualization │  │  │
│  │  │  Service    │  │   Service    │  │     Service     │  │  │
│  │  └─────────────┘  └──────────────┘  └─────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────┬──────────────────┬──────────────────┬──────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│   DynamoDB      │  │   CloudWatch    │  │  CoinGecko API      │
│                 │  │                 │  │  (External)         │
│ - Users Table   │  │ - Metrics       │  │                     │
│ - Alerts Table  │  │ - Logs          │  │ - Real-time prices  │
│ - Prices Table  │  │ - Alarms        │  │ - Historical data   │
└─────────────────┘  └─────────────────┘  └─────────────────────┘
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **EB CLI** (Elastic Beanstalk CLI) installed
4. **Python 3.9+** installed locally
5. **Git** for version control

## Installation Steps

### 1. Install AWS CLI

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Windows
# Download and run the AWS CLI MSI installer
```

### 2. Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your default output format (json)
```

### 3. Install Elastic Beanstalk CLI

```bash
pip install awsebcli
```

### 4. Clone and Setup Project

```bash
git clone <repository-url>
cd crypsync
cp .env.aws.example .env.aws
```

## Deployment

### Option 1: Automated Deployment (Recommended)

```bash
chmod +x deploy-aws.sh
./deploy-aws.sh
```

This script will:
1. Deploy CloudFormation infrastructure
2. Create DynamoDB tables
3. Initialize Elastic Beanstalk application
4. Deploy the application
5. Configure environment variables

### Option 2: Manual Deployment

#### Step 1: Deploy Infrastructure

```bash
aws cloudformation deploy \
    --template-file aws-infrastructure.yaml \
    --stack-name crypsync-infrastructure \
    --parameter-overrides \
        EnvironmentName=production \
        ApplicationName=crypsync \
    --capabilities CAPABILITY_NAMED_IAM \
    --region us-east-1
```

#### Step 2: Get DynamoDB Table Names

```bash
aws cloudformation describe-stacks \
    --stack-name crypsync-infrastructure \
    --query 'Stacks[0].Outputs' \
    --region us-east-1
```

#### Step 3: Initialize Elastic Beanstalk

```bash
eb init crypsync --platform python-3.9 --region us-east-1
```

#### Step 4: Create Environment

```bash
eb create crypsync-prod \
    --instance-type t3.small \
    --envvars \
        SECRET_KEY=your-secret-key,\
        FLASK_ENV=production,\
        AWS_REGION=us-east-1,\
        DYNAMODB_USERS_TABLE=crypsync-users-production,\
        DYNAMODB_ALERTS_TABLE=crypsync-alerts-production,\
        DYNAMODB_PRICES_TABLE=crypsync-prices-production
```

#### Step 5: Deploy Application

```bash
eb deploy crypsync-prod
```

## Post-Deployment Configuration

### 1. Verify SES Email

```bash
aws ses verify-email-identity --email-address noreply@yourdomain.com
```

### 2. Create Admin User

```bash
python init_admin.py
```

### 3. Configure Custom Domain (Optional)

```bash
# In Route 53, create a CNAME record pointing to your EB environment
eb setenv DOMAIN_NAME=crypsync.yourdomain.com
```

## Monitoring and Maintenance

### View Application Logs

```bash
eb logs crypsync-prod
```

### Monitor CloudWatch Metrics

```bash
aws cloudwatch get-metric-statistics \
    --namespace CrypSync \
    --metric-name ResponseTime \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Average
```

### Scale Application

```bash
# Update instance count
eb scale 3 crypsync-prod

# Update instance type
eb config crypsync-prod
# Edit the configuration file and save
```

### Update Application

```bash
# Make your code changes
git add .
git commit -m "Update application"

# Deploy update
eb deploy crypsync-prod
```

## Database Schema

### Users Table
- **Partition Key:** user_id (String)
- **GSI:** email-index on email
- **Attributes:** email, password_hash, created_at, last_login

### Alerts Table
- **Partition Key:** user_id (String)
- **Sort Key:** alert_id (String)
- **GSI:** state-index on state
- **Attributes:** crypto_id, threshold, alert_type, state, created_at, last_triggered

### Prices Table
- **Partition Key:** crypto_id (String)
- **Sort Key:** timestamp (Number)
- **TTL:** expires_at (90 days)
- **Attributes:** price_usd, recorded_at, source

## Cost Optimization

### DynamoDB
- Uses on-demand billing mode
- Estimated cost: $1-5/month for low traffic
- Consider provisioned capacity for predictable workloads

### Elastic Beanstalk
- t3.small instance: ~$15/month
- Auto-scaling: Additional instances as needed
- Consider Reserved Instances for 30-40% savings

### CloudWatch
- Logs: $0.50/GB ingested
- Metrics: First 10 custom metrics free
- Alarms: $0.10 per alarm per month

### Total Estimated Cost
- **Low Traffic:** $20-30/month
- **Medium Traffic:** $50-100/month
- **High Traffic:** $200+/month

## Troubleshooting

### Application Won't Start

```bash
# Check logs
eb logs crypsync-prod

# Check environment health
eb health crypsync-prod

# SSH into instance
eb ssh crypsync-prod
```

### DynamoDB Access Issues

```bash
# Verify IAM role permissions
aws iam get-role --role-name crypsync-ec2-role-production

# Test DynamoDB access
aws dynamodb describe-table --table-name crypsync-users-production
```

### High Response Times

1. Check CloudWatch metrics
2. Increase instance size or count
3. Enable DynamoDB caching
4. Optimize database queries

## Security Best Practices

1. **Rotate Secrets Regularly**
   ```bash
   eb setenv SECRET_KEY=new-secret-key
   ```

2. **Enable HTTPS**
   - Configure SSL certificate in EB console
   - Force HTTPS redirects

3. **Restrict Database Access**
   - Use VPC security groups
   - Enable DynamoDB encryption at rest

4. **Monitor Security**
   - Enable AWS CloudTrail
   - Set up CloudWatch alarms
   - Review IAM policies regularly

## Backup and Recovery

### DynamoDB Backups

```bash
# Enable point-in-time recovery
aws dynamodb update-continuous-backups \
    --table-name crypsync-users-production \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true

# Create on-demand backup
aws dynamodb create-backup \
    --table-name crypsync-users-production \
    --backup-name crypsync-users-backup-$(date +%Y%m%d)
```

### Application Backup

```bash
# Create application version
eb appversion create crypsync-backup-$(date +%Y%m%d)
```

## Cleanup

### Delete Application

```bash
# Terminate environment
eb terminate crypsync-prod

# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name crypsync-infrastructure
```

## Support

For issues and questions:
- Check AWS documentation
- Review CloudWatch logs
- Contact AWS Support

## License

MIT License
