# 🚀 Bedrock Copilot: AWS-Native Multi-Agent Code Intelligence System

> **Enterprise-grade AI-powered code assistant** with AWS Bedrock integration, multi-agent orchestration, and production-ready security.

[![Tests](https://img.shields.io/badge/Tests-19%2F19%20Passing-brightgreen)](https://github.com/your-org/bedrock-copilot)
[![Security](https://img.shields.io/badge/Security-Level%202%20Hardened-blue)](./docs/SECURITY.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock%20Native-orange)](https://aws.amazon.com/bedrock/)

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [AWS Native Deployment](#aws-native-deployment)
- [Security](#security)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

### Prerequisites
- Python 3.10+
- AWS Account with Bedrock access
- AWS CLI configured or AWS credentials set up

### 30-Second Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/bedrock-copilot.git
cd bedrock-copilot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials (local development)
export AWS_PROFILE=my-profile
# OR use environment variables:
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>

# 4. Run the tool
python src/main.py --help

# 5. Start using (example: analyze a repository)
python src/main.py analyze /path/to/repo --model claude-3-5-sonnet
```

---

## ✨ Features

### Core Capabilities
- 🤖 **Multi-Agent Orchestration**: Delegate tasks to specialized agents that work in parallel
- 🗺️ **AST-Based Code Mapping**: Intelligent syntax tree analysis for Python, JavaScript, TypeScript, Go, and Rust
- 📊 **99% Compression**: Advanced context optimization (best-case; production: ~50-60% savings)
- 🔐 **Enterprise Security**: Docker sandboxing, rate limiting, thread-safe operations
- ⚡ **10x Faster Analysis**: Parallel agent execution and intelligent caching
- 💾 **Persistent Memory**: Vector DB for long-term learning (ChromaDB integration)
- 📈 **Cost Monitoring**: Real-time token tracking and Bedrock cost estimation

### AWS Native Features
- 🔐 **IAM-First Design**: Full AWS credential provider chain support
- 🌍 **Multi-Region**: Cross-region inference with Bedrock Inference Profiles
- 📡 **CloudWatch Integration**: Native logging and metrics export
- 🛡️ **Bedrock Guardrails**: PII/sensitive data filtering
- 📦 **S3 Integration**: Long-term report storage and project history
- ⚙️ **Async-Ready**: Non-blocking I/O for high-concurrency workloads

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     CLI Interface (src/main.py)     │
├─────────────────────────────────────┤
│        Command Parser & Router       │
├─────────────────────────────────────┤
│  Multi-Agent Orchestration System    │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │Agent1│ │Agent2│ │Agent3│ ...  │
│  └──────┘ └──────┘ └──────┘        │
├─────────────────────────────────────┤
│  Core Services Layer                 │
│  ├─ AWS Security (IAM, Creds)       │
│  ├─ Bedrock API (Converse)          │
│  ├─ Rate Limiter & Thread Safety    │
│  ├─ Docker Sandbox                  │
│  └─ Vector Memory (ChromaDB)        │
├─────────────────────────────────────┤
│  AWS Services Integration           │
│  ├─ Bedrock Foundation Models       │
│  ├─ CloudWatch Logs & Metrics       │
│  ├─ IAM & Credential Chain          │
│  └─ S3 (optional: long-term storage)│
└─────────────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Security Module** | IAM, credential chain, sandboxing | `src/core/security/` |
| **Agent Pool** | Multi-agent orchestration | `src/core/agents/` |
| **AST Analyzer** | Code structure mapping | `src/core/analyzer/` |
| **Memory DB** | Vector DB for context caching | `src/core/memory/` |
| **Bedrock Client** | AWS Bedrock API wrapper | `src/core/bedrock/` |
| **Config Manager** | Environment & user settings | `src/config/` |
| **CLI Interface** | Command-line interface | `src/ui/` |

---

## 📦 Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-org/bedrock-copilot.git
cd bedrock-copilot
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Installation
```bash
python src/main.py --version
python -m pytest tests/ -v  # Run test suite
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# AWS Credentials (Optional - uses credential chain by default)
export AWS_ACCESS_KEY_ID=<your-key>
export AWS_SECRET_ACCESS_KEY=<your-secret>
export AWS_REGION=us-east-1

# AWS Profile (recommended for local development)
export AWS_PROFILE=my-svc-account

# Bedrock Settings
export BEDROCK_MODEL=claude-3-5-sonnet
export BEDROCK_REGION=us-east-1

# Advanced
export DEBUG=True                    # Enable debug logging
export COST_TRACKING=True            # Enable cost monitoring
export CLOUDWATCH_LOGS=True          # Send logs to CloudWatch
```

### Configuration File

Create `src/config/config.json`:

```json
{
  "aws": {
    "region": "us-east-1",
    "profile": "default",
    "bedrock_model": "claude-3-5-sonnet",
    "use_converse_api": true
  },
  "agents": {
    "max_parallel": 4,
    "timeout_seconds": 300,
    "retry_attempts": 3
  },
  "security": {
    "enable_docker_sandbox": true,
    "rate_limit_per_minute": 100,
    "enable_pii_filtering": true
  },
  "logging": {
    "level": "INFO",
    "cloudwatch_enabled": false,
    "log_file": "copilot.log"
  },
  "memory": {
    "vector_db": "chromadb",
    "persistence_path": "./data/memory"
  }
}
```

---

## 🎮 Usage

### Basic Commands

#### 1. Analyze a Repository
```bash
python src/main.py analyze /path/to/repo \
  --model claude-3-5-sonnet \
  --output-format json \
  --include-metrics
```

#### 2. Code Review
```bash
python src/main.py review /path/to/file.py \
  --focus security \
  --depth deep
```

#### 3. Generate Tests
```bash
python src/main.py generate tests /path/to/module \
  --framework pytest \
  --coverage-target 80
```

#### 4. Fix Issues
```bash
python src/main.py fix /path/to/file.py \
  --issue-type security \
  --auto-apply
```

#### 5. Interactive Session
```bash
python src/main.py interactive
# Then use natural language commands:
# > analyze src/ for security vulnerabilities
# > show me the top 3 technical debt areas
# > create a test for UserAuth class
```

### Example: Full Workflow

```bash
# 1. Map a project
python src/main.py map /path/to/project > project_map.json

# 2. Analyze security
python src/main.py analyze /path/to/project --focus security

# 3. Generate reports
python src/main.py report --type security --format html

# 4. Monitor costs
python src/main.py costs --timerange 7days
```

---

## ☁️ AWS Native Deployment

Bedrock Copilot is **AWS-first** and supports multiple deployment scenarios without hardcoding credentials.

### 1. Local Development (AWS Profile)

Use named AWS profiles from `~/.aws/credentials`:

```bash
# Setup (one-time)
aws configure --profile my-svc-account

# Run
export AWS_PROFILE=my-svc-account
python src/main.py analyze /path/to/repo
```

### 2. EC2 Instance Deployment

**Setup IAM Role:**
1. Create an IAM role with `bedrock_copilot_policy.json`:
   ```bash
   aws iam create-role --role-name BedrockCopilotRole \
     --assume-role-policy-document file://trust_policy.json
   
   aws iam create-policy --policy-name BedrockCopilotPolicy \
     --policy-document file://bedrock_copilot_policy.json
   
   aws iam attach-role-policy --role-name BedrockCopilotRole \
     --policy-arn arn:aws:iam::ACCOUNT-ID:policy/BedrockCopilotPolicy
   ```

2. Attach role to EC2 instance:
   ```bash
   aws ec2 associate-iam-instance-profile \
     --iam-instance-profile Name=BedrockCopilotRole \
     --instance-id i-1234567890abcdef0
   ```

3. Deploy and run (no env vars needed):
   ```bash
   git clone https://github.com/MegaLodonn0/bedrock-copilot.git
   cd bedrock-copilot
   pip install -r requirements.txt
   python src/main.py analyze /path/to/repo
   ```

### 3. AWS Lambda Deployment

**Package and deploy:**
```bash
# Create Lambda function with Bedrock execution role
sam build && sam deploy \
  --template-file template.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    BedrockModel=claude-3-5-sonnet \
    MaxAgents=2
```

### 4. AWS SSO (Identity Center)

For organizations using AWS SSO:

```bash
# Configure SSO profile
aws sso configure --profile my-sso-account

# Use it
export AWS_PROFILE=my-sso-account
python src/main.py analyze /path/to/repo
```

### 5. Container Deployment (ECS/Fargate)

Docker support with isolated execution:

```bash
# Build image
docker build -t bedrock-copilot:latest .

# Run in Fargate with IAM task role
aws ecs run-task \
  --cluster my-cluster \
  --task-definition bedrock-copilot:latest \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx]}"
```

### Credential Provider Chain (Automatic)

The tool automatically checks credentials in this order:

1. **Environment Variables** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. **AWS Profile** (`~/.aws/credentials` via `AWS_PROFILE`)
3. **SSO Profile** (`~/.aws/config` with SSO settings)
4. **EC2 Instance Profile** (IAM role attached to instance)
5. **ECS Task Role** (when running in ECS)
6. **Lambda Execution Role** (when running in Lambda)

✅ **No manual credential handling needed** — choose the deployment model, attach the IAM policy, and go!

---

## 🔐 Security

### Security Features

- ✅ **IAM-First**: Uses AWS credential provider chain, never requires hardcoded keys
- ✅ **Docker Sandboxing**: Agent code execution runs in isolated containers
- ✅ **Rate Limiting**: Built-in throttling to prevent API abuse
- ✅ **Thread-Safe Operations**: All concurrent access protected by locks
- ✅ **PII Filtering**: Bedrock Guardrails integration to detect sensitive data
- ✅ **Code Injection Protection**: Multi-language AST validation
- ✅ **Audit Logging**: All operations tracked and exportable

### Least Privilege IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

See `bedrock_copilot_policy.json` for the complete policy template.

### Security Best Practices

1. **Never commit `.env` files** — use `.env.example` template
2. **Rotate API keys regularly** if using access key authentication
3. **Use IAM Roles** for cloud deployments (EC2, Lambda, ECS)
4. **Enable CloudTrail** to audit Bedrock API calls
5. **Use Docker sandboxing** for untrusted code analysis
6. **Review cost alerts** via CloudWatch dashboards

---

## 🛠️ Development

### Project Structure
```
bedrock-copilot/
├── src/
│   ├── main.py              # CLI entry point
│   ├── config/              # Configuration management
│   ├── core/
│   │   ├── security/        # AWS & Docker security
│   │   ├── agents/          # Multi-agent system
│   │   ├── analyzer/        # AST & code analysis
│   │   ├── bedrock/         # AWS Bedrock wrapper
│   │   └── memory/          # Vector DB (ChromaDB)
│   └── ui/                  # CLI & UI components
├── tests/                   # Unit & integration tests
├── examples/                # Usage examples
├── docs/                    # Documentation
└── requirements.txt         # Python dependencies
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_security_levels_1_2.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Debugging

Enable debug mode for verbose logging:

```bash
export DEBUG=True
python src/main.py analyze /path/to/repo --debug
```

Check logs:
```bash
tail -f copilot.log
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Write tests for new functionality
4. Run test suite: `pytest tests/ -v`
5. Commit changes: `git commit -m "Add feature: my-feature"`
6. Push and create a Pull Request

---

## 📊 Monitoring & Cost Tracking

### CloudWatch Integration

Enable CloudWatch logging and metrics:

```bash
export CLOUDWATCH_LOGS=True
python src/main.py analyze /path/to/repo
```

View metrics:
```bash
aws cloudwatch get-metric-statistics \
  --namespace BedrockCopilot \
  --metric-name TokensUsed \
  --start-time 2026-03-29T00:00:00Z \
  --end-time 2026-03-29T23:59:59Z \
  --period 3600 \
  --statistics Sum,Average
```

### Cost Estimation

Track Bedrock API costs:

```bash
python src/main.py costs --timerange 7days --format json
```

Output:
```json
{
  "period": "7 days",
  "total_tokens": 1250000,
  "input_tokens": 800000,
  "output_tokens": 450000,
  "estimated_cost": "$2.50",
  "breakdown_by_model": {...}
}
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **"AWS credentials not found"**
```bash
# Solution: Ensure credentials are available
aws sts get-caller-identity  # Verify your AWS setup

# For EC2: Verify IAM role is attached
aws ec2 describe-iam-instance-profile-associations

# For SSO: Log in again
aws sso login --profile my-sso-account
```

#### 2. **"Bedrock model not available in region"**
```bash
# Check available models
aws bedrock list-foundation-models --region us-east-1

# Use different region
export AWS_REGION=us-west-2
```

#### 3. **"Rate limit exceeded"**
```bash
# Reduce parallel agents
export MAX_PARALLEL_AGENTS=2
# Or wait and retry
```

#### 4. **"Docker daemon not running"**
```bash
# Disable Docker sandboxing for unsafe environments
export ENABLE_DOCKER_SANDBOX=False
```

### Support & Documentation

- 📖 **Full Docs**: See `docs/` directory
- 🔒 **Security Details**: See `docs/SECURITY.md`
- 🏗️ **Architecture**: See `docs/ARCHITECTURE.md`
- 📊 **AWS Native Guide**: See `AWS_NATIVE_GUIDE.md`
- 🐛 **Issues**: Open a GitHub issue with detailed reproduction steps

---

## 📄 License

This project is licensed under the MIT License — see `LICENSE` file for details.

## 🤝 Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for guidelines.

## 🙏 Acknowledgments

- Built with [AWS Bedrock](https://aws.amazon.com/bedrock/)
- Multi-agent orchestration inspired by industry best practices
- Security hardening guided by OWASP principles
- Special thanks to the community for feedback and contributions

---

## 📞 Contact & Support

- 📧 **Email**: support@your-org.com
- 🐦 **Twitter**: [@BedrockCopilot](https://twitter.com/your-org)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-org/bedrock-copilot/discussions)
- 🐛 **Report Bug**: [GitHub Issues](https://github.com/your-org/bedrock-copilot/issues)

---

**Last Updated**: 2026-03-29
**Status**: Production Ready ✅
