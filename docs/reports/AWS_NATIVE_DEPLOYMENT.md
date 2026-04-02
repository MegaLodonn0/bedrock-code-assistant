# 🚀 AWS Native Deployment Guide

## Overview

Bedrock Copilot is **AWS-first**, designed to work seamlessly across AWS services without requiring hardcoded credentials. This guide covers deployment in multiple AWS environments.

---

## Table of Contents

1. [Quick Start by Environment](#quick-start)
2. [Credential Chain Explained](#credential-chain)
3. [Local Development](#local-development)
4. [AWS SSO (Identity Center)](#aws-sso)
5. [EC2 Deployment](#ec2-deployment)
6. [ECS/Fargate Deployment](#ecs-fargate)
7. [Lambda Deployment](#lambda-deployment)
8. [Cross-Region & Inference Profiles](#cross-region)
9. [Troubleshooting](#troubleshooting)
10. [Security Best Practices](#security-best-practices)

---

## Quick Start

### 1. **Local Development (AWS Profile)**
```bash
export AWS_PROFILE=my-svc-account
python src/main.py analyze /path/to/repo
```

### 2. **EC2 with IAM Role**
```bash
# Attach IAM role to EC2 instance, then run:
python src/main.py analyze /path/to/repo  # No env vars needed!
```

### 3. **AWS SSO**
```bash
aws sso login --profile my-sso-profile
export AWS_PROFILE=my-sso-profile
python src/main.py analyze /path/to/repo
```

### 4. **ECS/Fargate**
```bash
# Task role handles credentials automatically
docker run -e AWS_REGION=us-east-1 bedrock-copilot:latest analyze /repo
```

### 5. **Lambda**
```bash
sam deploy --capabilities CAPABILITY_IAM
# Lambda execution role handles credentials
```

---

## Credential Chain (Automatic Resolution)

The tool checks credentials in this order (**no manual configuration required**):

```
1. Environment Variables
   ├─ AWS_ACCESS_KEY_ID
   ├─ AWS_SECRET_ACCESS_KEY
   └─ AWS_SESSION_TOKEN (optional)
       ↓
2. AWS Profile (~/.aws/credentials)
   ├─ AWS_PROFILE env var or "default"
   └─ Fallback to ~/.aws/config profiles
       ↓
3. AWS SSO (Identity Center)
   ├─ ~/.aws/config SSO profiles
   └─ Token cache: ~/.aws/sso/cache
       ↓
4. EC2 Instance Profile
   ├─ IAM role attached to instance
   └─ Metadata service (169.254.169.254)
       ↓
5. ECS Task Role
   ├─ ECS_RELATIVE_URI environment variable
   └─ Container credentials endpoint
       ↓
6. Lambda Execution Role
   ├─ Lambda provides credentials via environment
   └─ Automatic rotation
```

✅ **Whichever credentials are found first are used**. Stop worrying about credential management!

---

## Local Development

### Option A: AWS Profile (Recommended)

**Setup (one-time):**
```bash
# Create a named profile
aws configure --profile my-svc-account
# Enter: Access Key, Secret Key, Region

# Or use existing profile from your organization
```

**Use it:**
```bash
export AWS_PROFILE=my-svc-account
python src/main.py analyze /path/to/repo
```

### Option B: Environment Variables (Testing Only)

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_REGION=us-east-1

python src/main.py analyze /path/to/repo
```

⚠️ **Never commit `.env` files with credentials!**

### Verify Setup

```bash
# Check credentials are available
aws sts get-caller-identity
# Output: Account ID, ARN, User ID

# List available profiles
aws configure list-profiles

# Test Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

---

## AWS SSO (Identity Center)

### Setup AWS SSO Profile

```bash
# Configure SSO
aws configure sso
# Follow prompts:
#   - SSO session name: my-org-sso
#   - Start URL: https://my-org.awsapps.com/start
#   - SSO region: us-east-1
#   - Account ID: 123456789012
#   - Role name: DeveloperAccess
#   - Profile name: my-sso-profile
#   - Default region: us-east-1

# Login
aws sso login --profile my-sso-profile
```

### Use SSO Profile with Copilot

```bash
export AWS_PROFILE=my-sso-profile
python src/main.py analyze /path/to/repo
```

### SSO Troubleshooting

```bash
# Check SSO session status
aws sts get-caller-identity --profile my-sso-profile

# Re-login if expired
aws sso login --profile my-sso-profile

# Clear cached tokens (forces re-login)
rm -rf ~/.aws/sso/cache/
```

---

## EC2 Deployment

### Step 1: Create IAM Role

**Create a trust policy (trust_policy.json):**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Create the role:**
```bash
aws iam create-role \
  --role-name BedrockCopilotRole \
  --assume-role-policy-document file://trust_policy.json
```

### Step 2: Attach Minimum Privilege Policy

```bash
# Use the provided bedrock_copilot_policy.json
aws iam create-policy \
  --policy-name BedrockCopilotPolicy \
  --policy-document file://bedrock_copilot_policy.json

aws iam attach-role-policy \
  --role-name BedrockCopilotRole \
  --policy-arn arn:aws:iam::ACCOUNT-ID:policy/BedrockCopilotPolicy
```

### Step 3: Create Instance Profile

```bash
aws iam create-instance-profile --instance-profile-name BedrockCopilotProfile

aws iam add-role-to-instance-profile \
  --instance-profile-name BedrockCopilotProfile \
  --role-name BedrockCopilotRole
```

### Step 4: Launch EC2 Instance with Role

```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --iam-instance-profile Name=BedrockCopilotProfile \
  --key-name my-key-pair \
  --security-groups sg-12345678 \
  --region us-east-1
```

Or attach role to existing instance:
```bash
aws ec2 associate-iam-instance-profile \
  --iam-instance-profile Name=BedrockCopilotProfile \
  --instance-id i-1234567890abcdef0
```

### Step 5: Deploy and Run

```bash
# SSH to instance
ssh -i my-key.pem ec2-user@instance-public-ip

# Install Python & dependencies
sudo yum update -y
sudo yum install -y python3 git
python3 -m pip install --upgrade pip

# Clone repository
git clone https://github.com/your-org/bedrock-copilot.git
cd bedrock-copilot

# Install requirements
pip install -r requirements.txt

# Run without any environment variables!
python src/main.py analyze /path/to/repo
```

✅ **That's it! The instance profile is automatically used.**

### Verify EC2 Role

```bash
# From EC2 instance, check role:
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Should return role name: BedrockCopilotRole
```

---

## ECS/Fargate Deployment

### Step 1: Create Task Execution Role

```bash
aws iam create-role \
  --role-name BedrockCopilotTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach execution policy
aws iam attach-role-policy \
  --role-name BedrockCopilotTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

### Step 2: Create Task Role

```bash
aws iam create-role \
  --role-name BedrockCopilotTaskRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach Bedrock policy
aws iam attach-role-policy \
  --role-name BedrockCopilotTaskRole \
  --policy-arn arn:aws:iam::ACCOUNT-ID:policy/BedrockCopilotPolicy
```

### Step 3: Register Task Definition

```json
{
  "family": "bedrock-copilot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::ACCOUNT-ID:role/BedrockCopilotTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT-ID:role/BedrockCopilotTaskRole",
  "containerDefinitions": [
    {
      "name": "bedrock-copilot",
      "image": "your-registry/bedrock-copilot:latest",
      "essential": true,
      "environment": [
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/bedrock-copilot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Step 4: Run Task

```bash
aws ecs run-task \
  --cluster my-cluster \
  --task-definition bedrock-copilot:1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx]}"
```

✅ **Task role credentials are automatically injected. No env vars needed!**

---

## Lambda Deployment

### Step 1: Create Lambda Execution Role

```bash
aws iam create-role \
  --role-name BedrockCopilotLambdaRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policies
aws iam attach-role-policy \
  --role-name BedrockCopilotLambdaRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name BedrockCopilotLambdaRole \
  --policy-arn arn:aws:iam::ACCOUNT-ID:policy/BedrockCopilotPolicy
```

### Step 2: Package Function

```bash
# Create Lambda function
mkdir bedrock-copilot-lambda
cd bedrock-copilot-lambda

# Copy application code
cp -r /path/to/bedrock-copilot/src .
cp requirements.txt .

# Install dependencies
pip install -r requirements.txt -t .

# Create handler
cat > lambda_handler.py << 'EOF'
from src.main import CopilotCLI
import json

def handler(event, context):
    cli = CopilotCLI()
    result = cli.analyze(event.get('repo_path'))
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
EOF

# Zip
zip -r function.zip .
```

### Step 3: Deploy

```bash
aws lambda create-function \
  --function-name bedrock-copilot \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT-ID:role/BedrockCopilotLambdaRole \
  --handler lambda_handler.handler \
  --zip-file fileb://function.zip \
  --timeout 300 \
  --memory-size 1024
```

### Step 4: Invoke

```bash
aws lambda invoke \
  --function-name bedrock-copilot \
  --payload '{"repo_path": "/tmp/repo"}' \
  response.json

cat response.json
```

✅ **Lambda execution role provides credentials automatically!**

---

## Cross-Region & Inference Profiles

### Using Inference Profiles (Recommended)

Bedrock Inference Profiles automatically route traffic to regions with capacity:

```python
from src.core.security.credential_chain import get_bedrock_client

# Use inference profile for automatic region selection
client = get_bedrock_client(region="us-west-2")

# Converse API with inference profile
response = client.converse(
    modelId="anthropic.claude-3-5-sonnet-20241022",
    messages=[...],
    inferenceConfig={
        "maxTokens": 2048,
        "temperature": 0.7
    }
)
```

### Cross-Region Failover

```python
from src.core.security.credential_chain import get_bedrock_client

regions = ["us-east-1", "us-west-2", "eu-west-1"]

for region in regions:
    try:
        client = get_bedrock_client(region=region)
        response = client.converse(...)
        break  # Success!
    except Exception as e:
        print(f"Failed in {region}, trying next...")
        continue
```

---

## Troubleshooting

### Issue: "No credentials found"

```bash
# Check 1: Environment variables
env | grep AWS_

# Check 2: AWS config files
cat ~/.aws/credentials  # Check format
cat ~/.aws/config       # Check profiles

# Check 3: If EC2, check role
curl http://169.254.169.254/latest/meta-data/iam/info

# Check 4: If ECS, check environment
env | grep AWS_CONTAINER
```

### Issue: "Bedrock model not available in region"

```bash
# List available models
aws bedrock list-foundation-models --region us-east-1

# Switch region
export AWS_REGION=us-west-2
python src/main.py analyze /path/to/repo
```

### Issue: "Access Denied (UnauthorizedOperation)"

```bash
# Verify credentials work
aws sts get-caller-identity --profile my-profile

# Check IAM policy is attached
aws iam list-attached-role-policies --role-name BedrockCopilotRole

# Verify policy allows Bedrock
aws iam get-role-policy --role-name BedrockCopilotRole \
  --policy-name BedrockCopilotPolicy
```

### Issue: "SSO session expired"

```bash
# Re-login
aws sso login --profile my-sso-profile

# Verify
aws sts get-caller-identity --profile my-sso-profile
```

---

## Security Best Practices

### ✅ Do's

- ✅ Use IAM roles for cloud deployments (EC2, Lambda, ECS)
- ✅ Use AWS profiles for local development
- ✅ Use AWS SSO for organizational authentication
- ✅ Enable CloudTrail to audit Bedrock API calls
- ✅ Rotate API keys quarterly (if using access keys)
- ✅ Use least privilege IAM policies
- ✅ Enable MFA for console access

### ❌ Don'ts

- ❌ Never commit credentials to Git
- ❌ Never hardcode API keys in code
- ❌ Never share .aws credentials files
- ❌ Never use root account for API access
- ❌ Never enable public access to IAM users
- ❌ Never skip credential encryption in transit

### Audit & Monitoring

```bash
# View Bedrock API calls
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceType,AttributeValue=AWS::Bedrock::Model \
  --max-results 50

# Set up cost alerts
aws budgets create-budget \
  --account-id ACCOUNT-ID \
  --budget file://budget.json

# Enable CloudWatch logging
export CLOUDWATCH_LOGS=True
python src/main.py analyze /path/to/repo
```

---

## Summary Table

| Environment | Setup Time | Credentials | Best For |
|-------------|-----------|-------------|----------|
| **Local Dev** | 2 min | AWS Profile | Development & testing |
| **Local SSO** | 5 min | SSO Profile | Org authentication |
| **EC2** | 10 min | IAM Role | Production servers |
| **Lambda** | 15 min | Lambda Role | Serverless workloads |
| **ECS** | 10 min | Task Role | Container orchestration |
| **Multi-Region** | 5 min | Inference Profiles | Global applications |

---

## Next Steps

- [Full Documentation](./README.md)
- [Security Details](./docs/SECURITY.md)
- [Bedrock API Reference](https://docs.aws.amazon.com/bedrock/latest/userguide/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

---

**Last Updated**: 2026-03-29
**Status**: Production Ready ✅
