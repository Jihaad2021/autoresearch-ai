# Deployment Guide - AutoResearch AI

**Last Updated**: November 25, 2024  
**Version**: 1.0  
**Status**: Sprint 4 - Deployment Ready

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Deployment Options](#deployment-options)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Local Development Deployment](#local-development-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [Environment Configuration](#environment-configuration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Scaling Strategies](#scaling-strategies)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Introduction

### What is Deployment?

**Deployment** is the process of making your application available to users:
```
Development Environment (Your laptop)
    ↓
Testing/Staging Environment (Pre-production)
    ↓
Production Environment (Live users)
```

### Deployment Goals

**1. Availability**
```
System should be accessible 24/7
Target: 99.9% uptime = ~43 minutes downtime per month
```

**2. Performance**
```
Response time should be consistent
Target: <3 seconds for article generation
```

**3. Scalability**
```
Handle increasing load without degradation
Target: 100+ concurrent requests
```

**4. Security**
```
Protect sensitive data and API keys
Secure communication (HTTPS)
```

**5. Maintainability**
```
Easy to update and rollback
Clear monitoring and logging
```

---

## 🏗️ Deployment Options

### Comparison Matrix

| Option | Complexity | Cost | Control | Best For |
|--------|-----------|------|---------|----------|
| **Local** | ⭐ Low | Free | Full | Development, Testing |
| **Docker Local** | ⭐⭐ Medium | Free | Full | Development, Demo |
| **VPS (DigitalOcean)** | ⭐⭐⭐ Medium | $5-50/mo | High | Small Production |
| **PaaS (Railway)** | ⭐⭐ Medium | $5-20/mo | Medium | Quick Production |
| **Container (AWS ECS)** | ⭐⭐⭐⭐ High | $20-100/mo | High | Scalable Production |
| **Kubernetes** | ⭐⭐⭐⭐⭐ Very High | $50-500/mo | Full | Enterprise Production |

---

### Decision Guide

**For Portfolio/Demo:**
```
Local + Docker → Show in video, GitHub
Cost: $0
Time: 1 hour setup
```

**For Small Users (1-10):**
```
Railway or Render
Cost: $5-20/month
Time: 2-3 hours setup
```

**For Growing Product (10-100 users):**
```
DigitalOcean Droplet + Docker
Cost: $20-50/month
Time: 1 day setup
```

**For Production (100+ users):**
```
AWS ECS or Google Cloud Run
Cost: $50-200/month
Time: 2-3 days setup
```

**For Enterprise (1000+ users):**
```
Kubernetes on AWS/GCP
Cost: $200-1000/month
Time: 1-2 weeks setup
```

---

## ✅ Pre-Deployment Checklist

### Code Readiness

- [ ] All tests passing (`pytest tests/ -v`)
- [ ] Code linting passed (`flake8 src/`)
- [ ] Type checking passed (`mypy src/`)
- [ ] Coverage ≥80% (`pytest --cov=src --cov-fail-under=80`)
- [ ] No hardcoded secrets in code
- [ ] Error handling comprehensive
- [ ] Logging implemented

### Configuration

- [ ] Environment variables documented (`.env.example`)
- [ ] Configuration for different environments (dev, staging, prod)
- [ ] API keys obtained and tested
- [ ] Database migrations ready (if applicable)
- [ ] External service accounts created

### Documentation

- [ ] README.md complete with setup instructions
- [ ] API documentation generated
- [ ] Deployment guide written (this doc)
- [ ] Architecture diagrams updated
- [ ] Troubleshooting guide available

### Infrastructure

- [ ] Domain name purchased (if needed)
- [ ] SSL certificate configured
- [ ] Database provisioned (if needed)
- [ ] Monitoring tools set up
- [ ] Backup strategy defined

### Security

- [ ] API keys stored securely (not in code)
- [ ] HTTPS enabled
- [ ] Authentication implemented (if needed)
- [ ] Rate limiting configured
- [ ] CORS configured properly
- [ ] Input validation comprehensive

---

## 💻 Local Development Deployment

### Quick Start (Development)

**Purpose**: Run system on your local machine for development/testing

**Time**: 5 minutes

**Steps:**
```bash
# 1. Clone repository
git clone https://github.com/yourusername/autoResearchAI.git
cd autoResearchAI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys:
# ANTHROPIC_API_KEY=sk-ant-...
# TAVILY_API_KEY=tvly-...

# 5. Run tests to verify setup
pytest tests/ -v

# 6. Start the application
# Option A: Run example
python examples/simple_article.py

# Option B: Start API server (Sprint 3+)
uvicorn src.api.main:app --reload --port 8000

# Option C: Start UI (Sprint 4+)
streamlit run src/ui/streamlit_app.py
```

**Access:**
- API: http://localhost:8000
- UI: http://localhost:8501
- API Docs: http://localhost:8000/docs

---

### Local with Streamlit UI
```bash
# Install Streamlit
pip install streamlit

# Run UI
streamlit run src/ui/streamlit_app.py

# UI will open at http://localhost:8501
```

**UI Features:**
- Upload documents
- Configure article parameters
- Real-time generation
- View results
- Download article

---

## 🐳 Docker Deployment

### Why Docker?

**Benefits:**
- ✅ Consistent environment (works everywhere)
- ✅ Easy deployment
- ✅ Isolated dependencies
- ✅ Easy scaling
- ✅ Version control for infrastructure

**Use Cases:**
- Development consistency
- Production deployment
- Demo/presentation
- CI/CD pipelines

---

### Docker Setup

**1. Dockerfile**
```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Docker Compose (Full Stack)**
```yaml
# docker-compose.yml
version: '3.8'

services:
  # API Backend
  api:
    build: .
    container_name: autoresearch-api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - TAVILY_API_KEY=${TAVILY_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - autoresearch-network
    depends_on:
      - redis
      - postgres

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: autoresearch-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    networks:
      - autoresearch-network

  # PostgreSQL Database (optional)
  postgres:
    image: postgres:15-alpine
    container_name: autoresearch-postgres
    environment:
      - POSTGRES_DB=autoresearch
      - POSTGRES_USER=autoresearch
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - autoresearch-network

  # Streamlit UI
  ui:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    container_name: autoresearch-ui
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://api:8000
    depends_on:
      - api
    restart: unless-stopped
    networks:
      - autoresearch-network

volumes:
  redis-data:
  postgres-data:

networks:
  autoresearch-network:
    driver: bridge
```

**3. Streamlit Dockerfile**
```dockerfile
# Dockerfile.streamlit
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install streamlit

# Copy UI code
COPY src/ui/ ./src/ui/

EXPOSE 8501

CMD ["streamlit", "run", "src/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

### Running with Docker
```bash
# 1. Build images
docker-compose build

# 2. Start all services
docker-compose up -d

# 3. View logs
docker-compose logs -f

# 4. Check status
docker-compose ps

# 5. Stop services
docker-compose down

# 6. Stop and remove volumes (clean slate)
docker-compose down -v
```

**Access:**
- API: http://localhost:8000
- UI: http://localhost:8501
- Redis: localhost:6379
- PostgreSQL: localhost:5432

---

### Docker Production Best Practices
```dockerfile
# Multi-stage build for smaller images
FROM python:3.12-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

# Copy only installed packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY src/ ./src/

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser /app
USER appuser

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ☁️ Cloud Deployment

### Option 1: Railway (Easiest)

**Time**: 30 minutes  
**Cost**: $5-20/month  
**Best For**: Quick deployment, demos, small production

**Steps:**

**1. Prepare Repository**
```bash
# Create railway.json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300
  }
}

# Create Procfile
web: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

**2. Deploy to Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Add environment variables
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set TAVILY_API_KEY=tvly-...

# Deploy
railway up

# Get URL
railway domain
```

**3. Configure Custom Domain (Optional)**
```bash
# In Railway dashboard:
Settings → Domains → Add Custom Domain
→ Enter: api.yourdomain.com
→ Add DNS record (provided by Railway)
```

**Access:**
- Auto-generated URL: https://your-app.railway.app
- Custom domain: https://api.yourdomain.com

---

### Option 2: DigitalOcean Droplet

**Time**: 2-3 hours  
**Cost**: $6-50/month  
**Best For**: Full control, medium production

**Steps:**

**1. Create Droplet**
```bash
# On DigitalOcean Dashboard:
Create → Droplets
→ Choose: Ubuntu 22.04 LTS
→ Size: Basic ($12/month recommended)
→ Datacenter: Nearest to users
→ Add SSH key
→ Create Droplet
```

**2. Initial Server Setup**
```bash
# SSH into droplet
ssh root@your_droplet_ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Create non-root user
adduser deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Switch to deploy user
su - deploy
```

**3. Deploy Application**
```bash
# Clone repository
git clone https://github.com/yourusername/autoResearchAI.git
cd autoResearchAI

# Create .env file
nano .env
# Add your API keys

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

**4. Configure Nginx (Reverse Proxy)**
```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/autoresearch

# Add configuration:
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/autoresearch /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**5. Setup SSL (HTTPS)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

**Access:**
- HTTPS: https://api.yourdomain.com
- Auto-redirect from HTTP to HTTPS

---

### Option 3: AWS ECS (Scalable)

**Time**: 1 day  
**Cost**: $50-200/month  
**Best For**: Scalable production, enterprise

**High-Level Steps:**

**1. Prepare Docker Image**
```bash
# Build and tag
docker build -t autoresearch-api .

# Test locally
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e TAVILY_API_KEY=tvly-... \
  autoresearch-api
```

**2. Push to Amazon ECR**
```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name autoresearch-api

# Tag image
docker tag autoresearch-api:latest \
  YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/autoresearch-api:latest

# Push
docker push YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/autoresearch-api:latest
```

**3. Create ECS Cluster**
```bash
# Using AWS Console:
ECS → Clusters → Create Cluster
→ Name: autoresearch-cluster
→ Infrastructure: AWS Fargate (serverless)
→ Create
```

**4. Create Task Definition**
```json
{
  "family": "autoresearch-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "autoresearch-api",
      "image": "YOUR_AWS_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/autoresearch-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:xxx:secret:anthropic-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/autoresearch",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "api"
        }
      }
    }
  ]
}
```

**5. Create Service with Load Balancer**
```bash
# Through AWS Console:
ECS → Cluster → Services → Create
→ Task Definition: autoresearch-task
→ Service Name: autoresearch-service
→ Desired Tasks: 2 (for redundancy)
→ Load Balancer: Application Load Balancer
→ Health Check Path: /health
→ Auto Scaling: Enable (Min: 2, Max: 10)
→ Create
```

**6. Configure Domain & SSL**
```bash
# Route 53:
Create hosted zone for yourdomain.com
Add A record: api.yourdomain.com → ALB DNS

# Certificate Manager:
Request certificate for api.yourdomain.com
Validate via DNS
Attach to ALB listener
```

**Access:**
- Load Balancer URL: https://autoresearch-alb-xxx.us-east-1.elb.amazonaws.com
- Custom Domain: https://api.yourdomain.com

---

### Option 4: Google Cloud Run (Serverless)

**Time**: 2-3 hours  
**Cost**: Pay per use ($0-50/month)  
**Best For**: Variable traffic, cost optimization

**Steps:**
```bash
# 1. Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# 2. Initialize and login
gcloud init
gcloud auth login

# 3. Configure Docker for GCR
gcloud auth configure-docker

# 4. Build and push image
docker build -t gcr.io/YOUR_PROJECT_ID/autoresearch-api .
docker push gcr.io/YOUR_PROJECT_ID/autoresearch-api

# 5. Deploy to Cloud Run
gcloud run deploy autoresearch-api \
  --image gcr.io/YOUR_PROJECT_ID/autoresearch-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=production \
  --set-secrets ANTHROPIC_API_KEY=anthropic-key:latest \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10

# 6. Get URL
gcloud run services describe autoresearch-api --region us-central1
```

**Access:**
- Auto URL: https://autoresearch-api-xxx-uc.a.run.app
- Custom domain: Configure in Cloud Run console

---

## ⚙️ Environment Configuration

### Environment Variables

**Development (.env.development):**
```env
# Environment
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# API Keys
ANTHROPIC_API_KEY=sk-ant-api-key-here
TAVILY_API_KEY=tvly-api-key-here
NEWS_API_KEY=news-api-key-here

# Application Settings
MAX_ITERATIONS=3
DEFAULT_MAX_BUDGET=10.00
DEFAULT_MAX_TIME=3600

# Feature Flags
ENABLE_CACHING=false
ENABLE_RESEARCH_WORKERS=true
ENABLE_QUALITY_WORKERS=true

# Database (optional)
DATABASE_URL=sqlite:///./dev.db

# Redis (optional)
REDIS_URL=redis://localhost:6379
```

**Staging (.env.staging):**
```env
ENVIRONMENT=staging
LOG_LEVEL=INFO
ANTHROPIC_API_KEY=sk-ant-staging-key
TAVILY_API_KEY=tvly-staging-key
ENABLE_CACHING=true
DATABASE_URL=postgresql://user:pass@staging-db:5432/autoresearch
REDIS_URL=redis://staging-redis:6379
```

**Production (.env.production):**
```env
ENVIRONMENT=production
LOG_LEVEL=WARNING
ANTHROPIC_API_KEY=sk-ant-production-key
TAVILY_API_KEY=tvly-production-key
ENABLE_CACHING=true
ENABLE_RATE_LIMITING=true
DATABASE_URL=postgresql://user:pass@prod-db:5432/autoresearch
REDIS_URL=redis://prod-redis:6379

# Security
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
API_KEY_REQUIRED=true
```

---

### Configuration Management

**Using Python-dotenv:**
```python
# src/utils/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    # API Keys
    anthropic_api_key: str
    tavily_api_key: str
    news_api_key: Optional[str] = None
    
    # Application
    max_iterations: int = 3
    default_max_budget: float = 5.00
    default_max_time: int = 1200
    
    # Features
    enable_caching: bool = True
    enable_rate_limiting: bool = False
    
    # Database
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # Security
    allowed_origins: list[str] = ["*"]
    api_key_required: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()
```

**Usage:**
```python
from src.utils.config import settings

# Access settings
api_key = settings.anthropic_api_key
max_budget = settings.default_max_budget

# Environment-specific behavior
if settings.environment == "production":
    # Production-specific logic
    pass
```

---

### Secret Management

**Never commit secrets to Git:**
```bash
# .gitignore
.env
.env.local
.env.production
*.pem
*.key
secrets/
```

**Options for Secret Storage:**

**1. Environment Variables (Simple)**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

**2. AWS Secrets Manager (AWS)**
```bash
# Store secret
aws secretsmanager create-secret \
  --name anthropic-api-key \
  --secret-string sk-ant-...

# Retrieve in application
import boto3
client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='anthropic-api-key')
api_key = response['SecretString']
```

**3. Google Secret Manager (GCP)**
```bash
# Store secret
echo -n "sk-ant-..." | gcloud secrets create anthropic-api-key --data-file=-

# Use in Cloud Run
--set-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest
```

**4. HashiCorp Vault (Advanced)**
```bash
# Store secret
vault kv put secret/autoresearch/anthropic-key value=sk-ant-...

# Retrieve
vault kv get -field=value secret/autoresearch/anthropic-key
```

---

## 📊 Monitoring & Logging

### Application Logging

**Structured Logging:**
```python
# src/utils/logger.py

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easy parsing."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'execution_id'):
            log_data['execution_id'] = record.execution_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        return json.dumps(log_data)

def setup_logging():
    """Configure application logging."""
    logger = logging.getLogger('autoresearch')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler (production)
    if settings.environment == "production":
        file_handler = logging.FileHandler('logs/app.log')
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    
    return logger
```

**Usage:**
```python
from src.utils.logger import setup_logging

logger = setup_logging()

# Log with context
logger.info(
    "Article generation started",
    extra={
        "execution_id": execution_id,
        "topic": brief.topic,
        "estimated_cost": plan.estimated_total_cost
    }
)
```

---

### Monitoring Tools

**1. Application Metrics**
```python
# src/utils/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
request_count = Counter(
    'autoresearch_requests_total',
    'Total number of requests',
    ['endpoint', 'status']
)

request_duration = Histogram(
    'autoresearch_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint']
)

active_requests = Gauge(
    'autoresearch_active_requests',
    'Number of active requests'
)

generation_cost = Histogram(
    'autoresearch_generation_cost_dollars',
    'Cost of article generation',
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
)

# Usage in FastAPI
from fastapi import FastAPI
from prometheus_client import make_asgi_app

app = FastAPI()

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.post("/research")
async def create_research(brief: Brief):
    active_requests.inc()
    start_time = time.time()
    
    try:
        output = controller.execute(brief)
        request_count.labels(endpoint='research', status='success').inc()
        generation_cost.observe(output.metrics.total_cost)
        return output
    except Exception as e:
        request_count.labels(endpoint='research', status='error').inc()
        raise
    finally:
        duration = time.time() - start_time
        request_duration.labels(endpoint='research').observe(duration)
        active_requests.dec()
```

**2. Health Checks**
```python
# src/api/health.py

from fastapi import APIRouter, HTTPException
from datetime import datetime
import httpx

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/ready")
async def readiness_check():
    """Readiness check - are dependencies available?"""
    checks = {}
    overall_healthy = True
    
    # Check Redis
    try:
        # redis_client.ping()
        checks['redis'] = 'healthy'
    except Exception as e:
        checks['redis'] = f'unhealthy: {str(e)}'
        overall_healthy = False
    
    # Check Claude API
    try:
        # Make test call to Claude
        checks['claude_api'] = 'healthy'
    except Exception as e:
        checks['claude_api'] = f'unhealthy: {str(e)}'
        overall_healthy = False
    
    # Check Tavily API
    try:
        # Make test call to Tavily
        checks['tavily_api'] = 'healthy'
    except Exception as e:
        checks['tavily_api'] = f'unhealthy: {str(e)}'
        overall_healthy = False
    
    if not overall_healthy:
        raise HTTPException(status_code=503, detail=checks)
    
    return {
        "status": "ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

**3. External Monitoring Services**

**Sentry (Error Tracking):**
```python
# pip install sentry-sdk

import sentry_sdk

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    environment=settings.environment,
    traces_sample_rate=0.1  # 10% of transactions
)

# Errors automatically reported
# Manual reporting:
sentry_sdk.capture_exception(exception)
```

**Datadog (Full Observability):**
```python
# pip install ddtrace

from ddtrace import tracer

@tracer.wrap()
def generate_article(brief):
    # Automatically traced
    pass
```

**New Relic (APM):**
```python
# pip install newrelic

import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

@newrelic.agent.background_task()
def process_article():
    pass
```

---

### Log Aggregation

**Option 1: CloudWatch (AWS)**
```bash
# Already configured in ECS task definition
# View logs in AWS Console: CloudWatch → Log Groups
```

**Option 2: Papertrail**
```bash
# Add remote syslog handler
import logging
from logging.handlers import SysLogHandler

papertrail = SysLogHandler(address=('logs.papertrailapp.com', XXXXX))
logger.addHandler(papertrail)
```

**Option 3: ELK Stack (Self-Hosted)**
```yaml
# docker-compose.yml
  elasticsearch:
    image: elasticsearch:8.11.0
  
  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  
  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
```

---

## 📈 Scaling Strategies

### Horizontal Scaling (More Instances)

**When to Scale:**
```
Single instance can handle ~10-20 concurrent requests
If experiencing:
- Response times increasing
- Request queue building up
- CPU usage consistently >70%
→ Add more instances
```

**Docker Compose Scaling:**
```bash
# Scale to 3 API instances
docker-compose up --scale api=3 -d

# Add load balancer (Nginx)
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

**Nginx Load Balancer Config:**
```nginx
upstream api_backend {
    least_conn;  # Route to least busy server
    server api_1:8000;
    server api_2:8000;
    server api_3:8000;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Kubernetes Scaling:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: autoresearch-api
spec:
  replicas: 3  # Start with 3 instances
  template:
    # ...

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: autoresearch-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: autoresearch-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

### Vertical Scaling (Bigger Instances)

**When to Scale:**
```
If single requests are slow:
- Long processing times
- High memory usage
- Complex computations
→ Use larger instances
```

**Docker Resources:**
```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

**AWS ECS:**
```json
{
  "cpu": "2048",     // 2 vCPU (was 512)
  "memory": "4096"   // 4 GB (was 1 GB)
}
```

---

### Caching Strategy

**Redis Caching:**
```python
# src/utils/cache.py

import redis
import json
import hashlib
from functools import wraps

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True
)

def cache_result(ttl=3600):
    """Cache function results in Redis.
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function and arguments
            key_data = f"{func.__name__}:{args}:{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=1800)  # Cache for 30 minutes
def generate_article(brief: Brief) -> FinalOutput:
    # Expensive operation
    controller = Controller()
    return controller.execute(brief)
```

**Cache Invalidation:**
```python
def invalidate_cache(pattern: str):
    """Invalidate cached results matching pattern."""
    for key in redis_client.scan_iter(match=pattern):
        redis_client.delete(key)

# When new data uploaded
invalidate_cache("generate_article:*")
```

---

### Database Optimization

**Connection Pooling:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=10,        # Connections to keep open
    max_overflow=20,     # Extra connections when needed
    pool_timeout=30,     # Wait timeout
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

**Indexing:**
```sql
-- Index frequently queried fields
CREATE INDEX idx_execution_id ON workflows(execution_id);
CREATE INDEX idx_created_at ON workflows(created_at);
CREATE INDEX idx_status ON workflows(status);
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Container Won't Start**
```bash
# Check logs
docker-compose logs api

# Common causes:
# - Missing environment variables
# - Port already in use
# - Syntax error in config

# Debug:
docker-compose config  # Validate compose file
docker-compose ps      # Check container status
```

**2. API Returns 502/504 Errors**
```bash
# Possible causes:
# - Application crashed
# - Timeout (request taking too long)
# - Out of memory

# Check:
docker stats           # Memory/CPU usage
docker-compose logs api  # Application logs

# Increase timeout in nginx:
proxy_read_timeout 300s;
proxy_connect_timeout 300s;
```

**3. High Memory Usage**
```python
# Memory leak detection
import tracemalloc

tracemalloc.start()

# ... run your code ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

for stat in top_stats[:10]:
    print(stat)
```

**4. Slow Performance**
```python
# Profile code
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here
result = generate_article(brief)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest
```

**5. API Rate Limits**
```python
# Implement exponential backoff
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_api():
    # API call here
    pass
```

---

### Health Check Failures

**Debug Steps:**
```bash
# 1. Check if service is running
docker-compose ps

# 2. Check application logs
docker-compose logs api --tail=100

# 3. Test health endpoint manually
curl http://localhost:8000/health

# 4. Check resource usage
docker stats

# 5. Check network connectivity
docker-compose exec api ping google.com
```

---

### Database Connection Issues
```python
# Add connection retry logic
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import time

def create_db_engine_with_retry(max_retries=5):
    for attempt in range(max_retries):
        try:
            engine = create_engine(settings.database_url)
            # Test connection
            engine.connect()
            return engine
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Database connection failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
```

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] Code reviewed and merged to main
- [ ] Version tagged (e.g., v1.0.0)
- [ ] Environment variables configured
- [ ] Database migrations prepared
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Rollback plan documented

### Deployment

- [ ] Deploy to staging first
- [ ] Run smoke tests on staging
- [ ] Monitor staging for 24 hours
- [ ] Deploy to production
- [ ] Run smoke tests on production
- [ ] Monitor logs for errors
- [ ] Verify health checks passing
- [ ] Check performance metrics

### Post-Deployment

- [ ] Announce deployment to team
- [ ] Monitor for 1-2 hours
- [ ] Check error rates
- [ ] Verify user experience
- [ ] Update documentation
- [ ] Tag production version
- [ ] Celebrate success! 🎉

---

## 🔗 Quick Reference

### Essential Commands
```bash
# Docker
docker-compose up -d           # Start services
docker-compose down            # Stop services
docker-compose logs -f         # View logs
docker-compose ps              # Check status
docker-compose restart api     # Restart service

# Railway
railway up                     # Deploy
railway logs                   # View logs
railway variables              # Manage env vars

# AWS
aws ecr get-login-password     # Docker login
aws ecs update-service         # Deploy update
aws logs tail                  # View logs

# Health Checks
curl http://localhost:8000/health
curl http://localhost:8000/health/ready
curl http://localhost:8000/metrics
```

---

### Deployment URLs by Option

| Option | Setup Time | URL Format | Cost/Month |
|--------|-----------|------------|------------|
| **Local** | 5 min | localhost:8000 | $0 |
| **Docker Local** | 15 min | localhost:8000 | $0 |
| **Railway** | 30 min | your-app.railway.app | $5-20 |
| **DigitalOcean** | 2-3 hours | your-domain.com | $6-50 |
| **AWS ECS** | 1 day | your-domain.com | $50-200 |
| **GCP Cloud Run** | 2-3 hours | xxx-uc.a.run.app | $0-50 |

---

## 📚 Additional Resources

**Docker:**
- Official Docs: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- Best Practices: https://docs.docker.com/develop/dev-best-practices/

**Cloud Platforms:**
- Railway Docs: https://docs.railway.app/
- DigitalOcean Tutorials: https://www.digitalocean.com/community/tutorials
- AWS ECS Guide: https://docs.aws.amazon.com/ecs/
- GCP Cloud Run: https://cloud.google.com/run/docs

**Monitoring:**
- Prometheus: https://prometheus.io/docs/
- Grafana: https://grafana.com/docs/
- Sentry: https://docs.sentry.io/

---

## 🔗 Related Documentation

- **[Development Guide](./09_DEVELOPMENT.md)** - Setup and development
- **[Testing Guide](./10_TESTING.md)** - Testing strategies
- **[Architecture](./02_ARCHITECTURE.md)** - System design

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2024  
**Target Audience**: DevOps, Developers, System Administrators

---

END OF DEPLOYMENT GUIDE