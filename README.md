# 🚀 Serverless CI/CD Pipeline

A complete CI/CD pipeline demonstrating DevOps best practices with AWS serverless technologies.

![Architecture](https://img.shields.io/badge/Architecture-Serverless-orange)
![AWS](https://img.shields.io/badge/AWS-Free%20Tier-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)

## 📋 Overview

This project implements a **Task Manager REST API** with a fully automated CI/CD pipeline using AWS services:

```
GitHub Push → CodePipeline → CodeBuild → CloudFormation → Lambda + API Gateway
                                              ↓
                              CloudWatch Logs + Alarms → SNS Notifications
```

## 🏗️ Architecture

| Component | AWS Service | Purpose |
|-----------|-------------|---------|
| Source Control | GitHub | Version control |
| CI/CD Orchestration | CodePipeline | Automate deployments |
| Build & Test | CodeBuild | Run tests, build artifacts |
| Infrastructure as Code | CloudFormation/SAM | Define infrastructure |
| Compute | Lambda | Run API handlers |
| API | API Gateway | REST endpoints |
| Database | DynamoDB | Store tasks |
| Monitoring | CloudWatch | Logs, metrics, alarms |
| Notifications | SNS | Pipeline alerts |

## 📁 Project Structure

```
serverless-cicd-pipeline/
├── README.md                       # This file
├── template.yaml                   # SAM template (Lambda, API, DynamoDB)
├── buildspec.yml                   # CodeBuild configuration
├── samconfig.toml                  # SAM deployment settings
├── env.json                        # Local testing environment
├── .gitignore
├── src/
│   ├── handlers/
│   │   └── app.py                  # Lambda function code
│   ├── tests/
│   │   └── test_app.py             # Unit tests
│   └── requirements.txt            # Python dependencies
└── infrastructure/
    └── pipeline-template.yaml      # CI/CD pipeline CloudFormation
```

## 🚀 Getting Started

### Prerequisites

1. **AWS Account** (Free Tier eligible)
2. **AWS CLI** configured with credentials
3. **SAM CLI** installed ([Installation Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
4. **Python 3.11+**
5. **GitHub Account**

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/serverless-cicd-pipeline.git
cd serverless-cicd-pipeline

# Install dependencies
pip install -r src/requirements.txt
pip install pytest boto3
```

### Step 2: Run Tests Locally

```bash
# Run unit tests
python -m pytest src/tests/ -v

# Validate SAM template
sam validate --lint
```

### Step 3: Test Locally with SAM

```bash
# Build the application
sam build

# Start local API
sam local start-api --env-vars env.json

# Test endpoint (in another terminal)
curl http://localhost:3000/health
```

### Step 4: Deploy the Application

```bash
# First deployment (creates S3 bucket for artifacts)
sam deploy --guided

# Subsequent deployments
sam deploy
```

### Step 5: Deploy the CI/CD Pipeline

```bash
# Deploy pipeline infrastructure
aws cloudformation deploy \
  --template-file infrastructure/pipeline-template.yaml \
  --stack-name task-manager-pipeline \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    GitHubOwner=YOUR_GITHUB_USERNAME \
    GitHubRepo=serverless-cicd-pipeline \
    GitHubBranch=main

# IMPORTANT: After deployment, go to AWS Console → CodePipeline → Settings → Connections
# and authorize the GitHub connection
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/tasks` | List all tasks |
| POST | `/tasks` | Create a task |
| GET | `/tasks/{id}` | Get a task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

### Example Requests

```bash
# Health check
curl https://YOUR_API_URL/dev/health

# Create a task
curl -X POST https://YOUR_API_URL/dev/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn AWS", "priority": "high"}'

# Get all tasks
curl https://YOUR_API_URL/dev/tasks
```

## 📊 Monitoring

### CloudWatch Dashboard
After deployment, a dashboard is created at:
`AWS Console → CloudWatch → Dashboards → task-manager-pipeline-dev`

### Alarms
- **Lambda Errors**: Triggers when errors > 5 in 5 minutes
- **API Latency**: Triggers when latency > 3 seconds

### SNS Notifications
Subscribe to the SNS topic to receive:
- Pipeline start/success/failure notifications
- CloudWatch alarm notifications

## 🧪 Interview Talking Points

This project demonstrates:

1. **CI/CD Pipeline**: Automated testing and deployment
2. **Infrastructure as Code**: CloudFormation/SAM templates
3. **Serverless Architecture**: Lambda, API Gateway, DynamoDB
4. **Testing**: Unit tests with pytest and mocking
5. **Monitoring**: CloudWatch logs, metrics, alarms
6. **Security**: IAM roles with least privilege
7. **Multi-environment**: Dev, Staging, Production configs

## 💰 AWS Free Tier Usage

| Service | Free Tier Limit | Estimated Usage |
|---------|-----------------|-----------------|
| Lambda | 1M requests/month | ✅ Well under |
| API Gateway | 1M calls/month | ✅ Well under |
| DynamoDB | 25 GB storage | ✅ Well under |
| CodeBuild | 100 mins/month | ✅ Sufficient |
| CodePipeline | 1 free pipeline | ✅ Using 1 |
| S3 | 5 GB storage | ✅ Well under |
| CloudWatch | 10 custom metrics | ✅ Within limit |

## 🔧 Customization

### Add a New Environment

1. Update `samconfig.toml` with new environment settings
2. Update `pipeline-template.yaml` to add new stage
3. Deploy with `--config-env your-env`

### Add More Lambda Functions

1. Add handler in `src/handlers/`
2. Add function definition in `template.yaml`
3. Add tests in `src/tests/`

## 📝 License

MIT License - Feel free to use for learning and interviews!

---

**Built with ❤️ for DevOps learning**
