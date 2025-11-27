# API Reference - AutoResearch AI

**Last Updated**: November 25, 2024  
**Version**: 1.0  
**Status**: Sprint 3 - API Complete

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Authentication](#authentication)
4. [Core Endpoints](#core-endpoints)
5. [Request & Response Formats](#request--response-formats)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Webhooks](#webhooks)
9. [SDK & Libraries](#sdk--libraries)
10. [Examples](#examples)

---

## 🎯 Introduction

### What is the API?

The AutoResearch AI API allows you to programmatically generate research-based articles and content. Instead of using the web interface, you can integrate article generation directly into your applications.

### Use Cases

**1. Content Management Systems**
```
WordPress → API → Generate Article → Publish
```

**2. Automated Publishing**
```
Cron Job → API → Generate Daily Articles → Database
```

**3. Custom Applications**
```
Your App → API → Generate Content → Display to Users
```

**4. Integration with Other Services**
```
Zapier/Make → API → Generate → Send to Email/Slack
```

### API Base URLs
```
Development:  http://localhost:8000
Staging:      https://staging-api.autoresearch.ai
Production:   https://api.autoresearch.ai
```

---

## 🚀 Getting Started

### Quick Start

**1. Get API Access**
```bash
# For development (Sprint 1-2): No API key needed (localhost)
# For production (Sprint 3+): Get API key from dashboard
```

**2. Make Your First Request**
```bash
curl -X POST "https://api.autoresearch.ai/v1/research" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "topic": "Artificial Intelligence in Healthcare",
    "content_type": "article",
    "target_length": 2000
  }'
```

**3. Get Response**
```json
{
  "execution_id": "exec_20241125_143022",
  "status": "completed",
  "article": {
    "title": "AI in Healthcare: Transforming Patient Care",
    "content": "# AI in Healthcare\n\nArtificial intelligence...",
    "word_count": 2047
  },
  "quality": {
    "overall": 0.88,
    "article_quality": 0.90,
    "source_quality": 0.87
  },
  "sources": [...],
  "metrics": {
    "total_cost": 2.35,
    "total_duration_seconds": 18.5
  }
}
```

---

## 🔐 Authentication

### API Key Authentication

**Get API Key:**
```
1. Login to dashboard: https://dashboard.autoresearch.ai
2. Navigate to: Settings → API Keys
3. Click: "Create New API Key"
4. Copy key: Starts with "ar_" (e.g., ar_1234abcd...)
```

**Use API Key:**

**Option 1: Authorization Header (Recommended)**
```bash
curl -H "Authorization: Bearer ar_1234abcd..." \
  https://api.autoresearch.ai/v1/research
```

**Option 2: X-API-Key Header**
```bash
curl -H "X-API-Key: ar_1234abcd..." \
  https://api.autoresearch.ai/v1/research
```

**Option 3: Query Parameter (Not Recommended)**
```bash
curl "https://api.autoresearch.ai/v1/research?api_key=ar_1234abcd..."
```

### Security Best Practices

**✅ DO:**
- Store API keys in environment variables
- Use different keys for development/production
- Rotate keys regularly (every 90 days)
- Revoke keys if compromised

**❌ DON'T:**
- Commit API keys to Git
- Share keys in public channels
- Use same key for multiple apps
- Include keys in client-side code

**Example (Python):**
```python
import os

# ✅ GOOD - From environment variable
api_key = os.getenv("AUTORESEARCH_API_KEY")

# ❌ BAD - Hardcoded
api_key = "ar_1234abcd..."  # Never do this!
```

---

## 📡 Core Endpoints

### Overview
```
POST   /v1/research              Create research request
GET    /v1/research/{id}         Get research status
GET    /v1/research/{id}/result  Get final result
DELETE /v1/research/{id}         Cancel research

POST   /v1/validate              Validate brief
GET    /v1/health                Health check
GET    /v1/metrics               System metrics
```

---

### 1. Create Research Request

**Endpoint:** `POST /v1/research`

**Description:** Start a new article generation workflow

**Request Body:**
```json
{
  "topic": "string (required, 1-500 chars)",
  "content_type": "article | blog_post | research_report | tutorial",
  "target_length": "integer (500-10000, default: 2000)",
  "tone": "professional | casual | academic | conversational",
  "research_depth": "light | standard | deep",
  "min_sources": "integer (3-50, default: 10)",
  "min_quality_score": "float (0.5-1.0, default: 0.80)",
  "max_budget": "float (0.50-50.00, default: 5.00)",
  "max_time": "integer (60-7200, default: 1200)",
  "requirements": {
    "include_keywords": ["keyword1", "keyword2"],
    "exclude_topics": ["topic1", "topic2"],
    "target_audience": "string (optional)",
    "specific_sections": ["Introduction", "Benefits", "Challenges"]
  },
  "metadata": {
    "user_id": "string (optional)",
    "project_id": "string (optional)",
    "tags": ["tag1", "tag2"]
  }
}
```

**Minimal Request:**
```json
{
  "topic": "Python programming basics"
}
```

**Complete Request Example:**
```json
{
  "topic": "Impact of AI on healthcare in 2024",
  "content_type": "article",
  "target_length": 2500,
  "tone": "professional",
  "research_depth": "deep",
  "min_sources": 15,
  "min_quality_score": 0.85,
  "max_budget": 5.00,
  "max_time": 900,
  "requirements": {
    "include_keywords": ["machine learning", "patient care", "diagnosis"],
    "exclude_topics": ["cost analysis", "legal issues"],
    "target_audience": "Healthcare professionals",
    "specific_sections": [
      "Introduction",
      "Current Applications",
      "Benefits",
      "Challenges",
      "Future Outlook",
      "Conclusion"
    ]
  },
  "metadata": {
    "user_id": "user_12345",
    "project_id": "proj_healthcare_series",
    "tags": ["AI", "healthcare", "2024"]
  }
}
```

**Response (202 Accepted):**
```json
{
  "execution_id": "exec_20241125_143022",
  "status": "processing",
  "message": "Research request accepted and processing",
  "estimated_completion": "2024-11-25T14:33:00Z",
  "created_at": "2024-11-25T14:30:22Z",
  "links": {
    "status": "/v1/research/exec_20241125_143022",
    "result": "/v1/research/exec_20241125_143022/result",
    "cancel": "/v1/research/exec_20241125_143022"
  }
}
```

---

### 2. Get Research Status

**Endpoint:** `GET /v1/research/{execution_id}`

**Description:** Check the status of a research request

**Path Parameters:**
- `execution_id` (string, required): The execution ID from create request

**Request:**
```bash
curl -X GET "https://api.autoresearch.ai/v1/research/exec_20241125_143022" \
  -H "Authorization: Bearer ar_1234abcd..."
```

**Response (200 OK):**
```json
{
  "execution_id": "exec_20241125_143022",
  "status": "processing",
  "current_phase": "EXECUTING",
  "progress": {
    "percentage": 65,
    "current_step": "Research phase - 3 of 4 steps complete",
    "estimated_time_remaining": 8
  },
  "brief": {
    "topic": "Impact of AI on healthcare in 2024",
    "target_length": 2500
  },
  "metrics": {
    "elapsed_time": 12.5,
    "current_cost": 1.85,
    "iteration_count": 1
  },
  "created_at": "2024-11-25T14:30:22Z",
  "updated_at": "2024-11-25T14:30:35Z"
}
```

**Status Values:**
- `queued` - Request accepted, waiting to start
- `processing` - Currently generating
- `completed` - Successfully completed
- `partial` - Completed with warnings
- `failed` - Failed with errors
- `cancelled` - User cancelled

**Response when Completed:**
```json
{
  "execution_id": "exec_20241125_143022",
  "status": "completed",
  "current_phase": "COMPLETED",
  "progress": {
    "percentage": 100,
    "current_step": "Complete",
    "estimated_time_remaining": 0
  },
  "result_available": true,
  "links": {
    "result": "/v1/research/exec_20241125_143022/result"
  },
  "metrics": {
    "total_duration": 18.5,
    "total_cost": 2.35,
    "iteration_count": 1
  },
  "created_at": "2024-11-25T14:30:22Z",
  "completed_at": "2024-11-25T14:30:40Z"
}
```

---

### 3. Get Research Result

**Endpoint:** `GET /v1/research/{execution_id}/result`

**Description:** Get the final generated article and details

**Path Parameters:**
- `execution_id` (string, required): The execution ID

**Request:**
```bash
curl -X GET "https://api.autoresearch.ai/v1/research/exec_20241125_143022/result" \
  -H "Authorization: Bearer ar_1234abcd..."
```

**Response (200 OK):**
```json
{
  "execution_id": "exec_20241125_143022",
  "status": "completed",
  "article": {
    "title": "AI in Healthcare: Transforming Patient Care in 2024",
    "content": "# AI in Healthcare: Transforming Patient Care in 2024\n\n## Introduction\n\nArtificial intelligence (AI) is revolutionizing healthcare...\n\n## Current Applications\n\n### Diagnostic Assistance\n\nAI algorithms are now capable of analyzing medical images...\n\n### Personalized Treatment\n\nMachine learning models help physicians create...\n\n## Benefits\n\n1. **Improved Accuracy**: AI systems reduce diagnostic errors by 40%...\n2. **Faster Processing**: Analysis that took hours now takes minutes...\n3. **Cost Reduction**: Healthcare systems save an average of 15%...\n\n## Challenges\n\nDespite the promise, several challenges remain...\n\n## Future Outlook\n\nThe next 5 years will see...\n\n## Conclusion\n\nAI in healthcare represents a paradigm shift...\n\n## References\n\n[1] Smith, J. (2024). \"AI in Medical Diagnosis\"...",
    "word_count": 2547,
    "reading_time_minutes": 10,
    "sections": [
      {
        "title": "Introduction",
        "word_count": 234,
        "start_index": 0
      },
      {
        "title": "Current Applications",
        "word_count": 512,
        "start_index": 234
      }
    ]
  },
  "quality": {
    "overall": 0.88,
    "article_quality": 0.90,
    "source_quality": 0.87,
    "factual_accuracy": 0.89,
    "writing_quality": 0.86,
    "details": {
      "completeness": 0.92,
      "coherence": 0.88,
      "readability": 0.85
    }
  },
  "sources": [
    {
      "id": 1,
      "type": "web",
      "title": "AI Revolutionizes Medical Imaging",
      "url": "https://healthtech.com/ai-imaging",
      "author": "Dr. Jane Smith",
      "published_date": "2024-10-15",
      "relevance_score": 0.95,
      "credibility_score": 0.88,
      "citations_in_article": 3
    },
    {
      "id": 2,
      "type": "academic",
      "title": "Machine Learning in Clinical Decision Support",
      "url": "https://arxiv.org/abs/2410.12345",
      "authors": ["Johnson, M.", "Lee, K."],
      "published_date": "2024-09-20",
      "journal": "Journal of Medical AI",
      "relevance_score": 0.92,
      "credibility_score": 0.95,
      "citations_in_article": 5
    }
  ],
  "metrics": {
    "total_cost": 2.35,
    "total_tokens": 12500,
    "total_duration_seconds": 18.5,
    "iteration_count": 1,
    "workers_used": [
      "web_search",
      "academic_search",
      "content_synthesizer",
      "article_writer",
      "fact_checker",
      "editor"
    ]
  },
  "workflow": {
    "phases_executed": [
      "INITIALIZED",
      "PLANNING",
      "STRATEGY",
      "EXECUTING",
      "EVALUATING",
      "MERGING",
      "COMPLETED"
    ],
    "iterations": 1,
    "total_steps": 4,
    "total_tasks": 8
  },
  "warnings": [],
  "created_at": "2024-11-25T14:30:22Z",
  "completed_at": "2024-11-25T14:30:40Z"
}
```

**Response when Not Ready (202 Accepted):**
```json
{
  "execution_id": "exec_20241125_143022",
  "status": "processing",
  "message": "Result not yet available. Please check status.",
  "links": {
    "status": "/v1/research/exec_20241125_143022"
  }
}
```

**Response when Failed (200 OK with error details):**
```json
{
  "execution_id": "exec_20241125_143022",
  "status": "failed",
  "error": {
    "code": "WORKER_FAILURE",
    "message": "Critical worker failed after maximum retries",
    "details": {
      "failed_worker": "article_writer",
      "retry_attempts": 3,
      "last_error": "API timeout"
    }
  },
  "partial_results": {
    "research_completed": true,
    "sources_found": 12,
    "outline_created": true
  },
  "created_at": "2024-11-25T14:30:22Z",
  "failed_at": "2024-11-25T14:31:10Z"
}
```

---

### 4. Cancel Research Request

**Endpoint:** `DELETE /v1/research/{execution_id}`

**Description:** Cancel an ongoing research request

**Path Parameters:**
- `execution_id` (string, required): The execution ID to cancel

**Request:**
```bash
curl -X DELETE "https://api.autoresearch.ai/v1/research/exec_20241125_143022" \
  -H "Authorization: Bearer ar_1234abcd..."
```

**Response (200 OK):**
```json
{
  "execution_id": "exec_20241125_143022",
  "status": "cancelled",
  "message": "Research request successfully cancelled",
  "refund": {
    "original_budget": 5.00,
    "amount_used": 1.25,
    "amount_refunded": 3.75
  },
  "cancelled_at": "2024-11-25T14:31:15Z"
}
```

**Response when Already Completed (400 Bad Request):**
```json
{
  "error": {
    "code": "CANNOT_CANCEL",
    "message": "Cannot cancel research that is already completed",
    "execution_id": "exec_20241125_143022",
    "current_status": "completed"
  }
}
```

---

### 5. Validate Brief

**Endpoint:** `POST /v1/validate`

**Description:** Validate a research brief without actually executing it

**Use Cases:**
- Validate user input before submission
- Check budget/time requirements
- Preview estimated cost

**Request:**
```bash
curl -X POST "https://api.autoresearch.ai/v1/validate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ar_1234abcd..." \
  -d '{
    "topic": "AI in healthcare",
    "target_length": 2000,
    "max_budget": 3.00
  }'
```

**Response (200 OK - Valid):**
```json
{
  "valid": true,
  "message": "Brief is valid and ready for submission",
  "estimates": {
    "cost_estimate": {
      "min": 1.80,
      "max": 2.80,
      "average": 2.30
    },
    "time_estimate": {
      "min": 12,
      "max": 25,
      "average": 18
    },
    "sources_estimate": {
      "min": 8,
      "max": 15,
      "average": 12
    }
  },
  "suggestions": [
    "Consider using 'deep' research depth for better quality",
    "Increase min_sources to 15 for comprehensive coverage"
  ]
}
```

**Response (400 Bad Request - Invalid):**
```json
{
  "valid": false,
  "message": "Brief validation failed",
  "errors": [
    {
      "field": "topic",
      "error": "Topic too short. Minimum length is 10 characters",
      "current_value": "AI",
      "required": "10-500 characters"
    },
    {
      "field": "target_length",
      "error": "Target length exceeds maximum",
      "current_value": 15000,
      "required": "500-10000"
    }
  ]
}
```

---

### 6. Health Check

**Endpoint:** `GET /v1/health`

**Description:** Check API health status

**Request:**
```bash
curl "https://api.autoresearch.ai/v1/health"
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-11-25T14:30:00Z",
  "uptime_seconds": 86400,
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "claude_api": "healthy",
    "tavily_api": "healthy"
  }
}
```

**Response (503 Service Unavailable - Unhealthy):**
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2024-11-25T14:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "unhealthy",
    "claude_api": "degraded",
    "tavily_api": "healthy"
  },
  "errors": [
    "Redis connection timeout",
    "Claude API experiencing high latency"
  ]
}
```

---

### 7. System Metrics

**Endpoint:** `GET /v1/metrics`

**Description:** Get system usage metrics (requires admin access)

**Request:**
```bash
curl "https://api.autoresearch.ai/v1/metrics" \
  -H "Authorization: Bearer ar_admin_key..."
```

**Response (200 OK):**
```json
{
  "requests": {
    "total": 1234,
    "completed": 1156,
    "failed": 45,
    "cancelled": 33,
    "success_rate": 0.937
  },
  "performance": {
    "average_duration_seconds": 17.3,
    "p50_duration": 15.2,
    "p95_duration": 28.5,
    "p99_duration": 42.1
  },
  "costs": {
    "total": 2847.50,
    "average_per_request": 2.31
  },
  "quality": {
    "average_quality_score": 0.86,
    "average_source_count": 11.3
  },
  "workers": {
    "most_used": [
      {"worker": "web_search", "count": 1234},
      {"worker": "article_writer", "count": 1234},
      {"worker": "fact_checker", "count": 1156}
    ],
    "failure_rates": [
      {"worker": "academic_search", "rate": 0.05},
      {"worker": "web_scraper", "rate": 0.12}
    ]
  },
  "timestamp": "2024-11-25T14:30:00Z",
  "period": "last_24_hours"
}
```

---

## 📦 Request & Response Formats

### Content Types

**Request:**
- Accept: `application/json`
- Content-Type: `application/json`

**Response:**
- Content-Type: `application/json`

---

### Common Fields

**Timestamps:**
```
Format: ISO 8601 UTC
Example: "2024-11-25T14:30:22Z"
```

**Money:**
```
Format: Decimal with 2 places
Currency: USD
Example: 2.35
```

**Percentages:**
```
Format: Float 0.0-1.0
Example: 0.88 (means 88%)
```

---

### Pagination (Future Feature)

**For list endpoints (coming in Sprint 4):**

**Request:**
```
GET /v1/research?page=2&per_page=20
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total_items": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": true
  }
}
```

---

## ⚠️ Error Handling

### HTTP Status Codes

| Code | Meaning | When |
|------|---------|------|
| **200** | OK | Request successful |
| **202** | Accepted | Request accepted, processing |
| **400** | Bad Request | Invalid input data |
| **401** | Unauthorized | Missing or invalid API key |
| **403** | Forbidden | Valid key but insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |
| **503** | Service Unavailable | Service temporarily down |

---

### Error Response Format

**Standard Error Response:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "request_id": "req_1234abcd",
    "timestamp": "2024-11-25T14:30:00Z"
  }
}
```

---

### Common Error Codes

**Authentication Errors:**
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "The provided API key is invalid or has been revoked"
  }
}
```
```json
{
  "error": {
    "code": "API_KEY_EXPIRED",
    "message": "Your API key has expired. Please generate a new one"
  }
}
```

**Validation Errors:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "topic": "Field required",
      "target_length": "Must be between 500 and 10000"
    }
  }
}
```

**Resource Errors:**
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Research request not found",
    "details": {
      "execution_id": "exec_invalid_123"
    }
  }
}
```

**Quota Errors:**
```json
{
  "error": {
    "code": "BUDGET_EXCEEDED",
    "message": "Estimated cost exceeds maximum budget",
    "details": {
      "estimated_cost": 6.50,
      "max_budget": 5.00,
      "suggestion": "Increase max_budget or reduce requirements"
    }
  }
}
```

**Rate Limit Errors:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later",
    "details": {
      "limit": 100,
      "remaining": 0,
      "reset_at": "2024-11-25T15:00:00Z",
      "retry_after": 300
    }
  }
}
```

**Worker Errors:**
```json
{
  "error": {
    "code": "WORKER_FAILURE",
    "message": "Critical worker failed",
    "details": {
      "worker": "article_writer",
      "reason": "API timeout after 3 retries"
    }
  }
}
```

---

### Error Handling Best Practices

**1. Check HTTP Status First**
```python
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    result = response.json()
    print("Success!")
elif response.status_code == 202:
    print("Accepted, processing...")
elif response.status_code == 400:
    error = response.json()["error"]
    print(f"Validation error: {error['message']}")
elif response.status_code == 429:
    retry_after = response.json()["error"]["details"]["retry_after"]
    print(f"Rate limited. Retry after {retry_after} seconds")
else:
    print(f"Error: {response.status_code}")
```

**2. Implement Retry Logic**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def create_research(brief):
    response = requests.post(url, json=brief, headers=headers)
    if response.status_code == 429:
        raise Exception("Rate limited")  # Will retry
    return response.json()
```

**3. Handle Specific Error Codes**
```python
def handle_error(error):
    code = error["code"]
    
    if code == "RATE_LIMIT_EXCEEDED":
        retry_after = error["details"]["retry_after"]
        time.sleep(retry_after)
        return "retry"
    
    elif code == "BUDGET_EXCEEDED":
        # Increase budget or reduce requirements
        return "adjust_budget"
    
    elif code == "VALIDATION_ERROR":
        # Fix validation errors
        return "fix_validation"
    
    else:
        # Unknown error
        return "fail"
```

---

## 🚦 Rate Limiting

### Rate Limits

| Plan | Requests/Minute | Requests/Hour | Requests/Day |
|------|----------------|---------------|--------------|
| **Free** | 10 | 100 | 1,000 |
| **Starter** | 30 | 500 | 5,000 |
| **Pro** | 100 | 2,000 | 20,000 |
| **Enterprise** | Custom | Custom | Custom |

---

### Rate Limit Headers

**Every response includes rate limit headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1700924400
```

**Example:**
```bash
curl -I "https://api.autoresearch.ai/v1/research/exec_123" \
  -H "Authorization: Bearer ar_key..."

HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1700924400
Content-Type: application/json
```

**Python Example:**
```python
response = requests.get(url, headers=headers)

limit = int(response.headers.get('X-RateLimit-Limit'))
remaining = int(response.headers.get('X-RateLimit-Remaining'))
reset_timestamp = int(response.headers.get('X-RateLimit-Reset'))

print(f"Remaining requests: {remaining}/{limit}")

if remaining < 10:
    print("WARNING: Approaching rate limit!")
```

---

### Handling Rate Limits

**Best Practices:**

**1. Monitor Headers**
```python
def check_rate_limit(response):
    remaining = int(response.headers.get('X-RateLimit-Remaining', 999))
    if remaining < 10:
        logger.warning(f"Only {remaining} requests remaining")
```

**2. Implement Backoff**
```python
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    # Retry request
```

**3. Batch Requests**
```python
# Instead of 10 separate requests
for topic in topics:
    create_research(topic)  # 10 API calls

# Batch them (future feature)
create_batch_research(topics)  # 1 API call
```

---

## 🪝 Webhooks

### Webhook Overview

**Instead of polling for status, get notified when research completes:**
```
Your App → Create Research → API
                ↓
          Processing...
                ↓
API → Webhook → Your App (Result ready!)
```

### Setting Up Webhooks

**1. Configure Webhook URL (in Dashboard):**
```
Settings → Webhooks → Add Webhook
URL: https://your-app.com/webhooks/autoresearch
Events: research.completed, research.failed
```

**2. Receive Webhooks:**
```python
# Flask example
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/autoresearch', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-AutoResearch-Signature')
    payload = request.data
    
    expected = hmac.new(
        webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if signature != expected:
        return "Invalid signature", 401
    
    # Process webhook
    event = request.json
    
    if event['type'] == 'research.completed':
        handle_completion(event['data'])
    elif event['type'] == 'research.failed':
        handle_failure(event['data'])
    
    return "OK", 200
```

### Webhook Events

**research.completed:**
```json
{
  "type": "research.completed",
  "timestamp": "2024-11-25T14:30:40Z",
  "data": {
    "execution_id": "exec_20241125_143022",
    "status": "completed",
    "quality_score": 0.88,
    "cost": 2.35,
    "duration": 18.5,
    "result_url": "/v1/research/exec_20241125_143022/result"
  }
}
```

**research.failed:**
```json
{
  "type": "research.failed",
  "timestamp": "2024-11-25T14:31:10Z",
  "data": {
    "execution_id": "exec_20241125_143022",
    "status": "failed",
    "error_code": "WORKER_FAILURE",
    "error_message": "Critical worker failed",
    "partial_results_available": true
  }
}
```

**research.partial:**
```json
{
  "type": "research.partial",
  "timestamp": "2024-11-25T14:31:20Z",
  "data": {
    "execution_id": "exec_20241125_143022",
    "status": "partial",
    "quality_score": 0.75,
    "warning": "Quality below threshold after max iterations",
    "result_url": "/v1/research/exec_20241125_143022/result"
  }
}
```

---

## 📚 SDK & Libraries

### Official SDKs

**Python SDK:**
```bash
pip install autoresearch-python
```
```python
from autoresearch import AutoResearch

client = AutoResearch(api_key="ar_1234abcd...")

# Create research
research = client.research.create(
    topic="AI in healthcare",
    target_length=2000
)

# Wait for completion
result = research.wait()

print(result.article.title)
print(result.quality.overall)
```

**JavaScript/TypeScript SDK:**
```bash
npm install @autoresearch/sdk
```
```typescript
import { AutoResearch } from '@autoresearch/sdk';

const client = new AutoResearch({ apiKey: 'ar_1234abcd...' });

// Create research
const research = await client.research.create({
  topic: 'AI in healthcare',
  targetLength: 2000
});

// Poll for result
const result = await research.wait();

console.log(result.article.title);
console.log(result.quality.overall);
```

---

### Community Libraries

**Go:**
```
go get github.com/autoresearch/go-sdk
```

**Ruby:**
```
gem install autoresearch
```

**PHP:**
```
composer require autoresearch/sdk
```

---

## 💡 Examples

### Example 1: Simple Article Generation

**cURL:**
```bash
curl -X POST "https://api.autoresearch.ai/v1/research" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ar_1234abcd..." \
  -d '{
    "topic": "Benefits of meditation",
    "target_length": 1500
  }'
```

**Python:**
```python
import requests

url = "https://api.autoresearch.ai/v1/research"
headers = {
    "Authorization": "Bearer ar_1234abcd...",
    "Content-Type": "application/json"
}
data = {
    "topic": "Benefits of meditation",
    "target_length": 1500
}

# Create research
response = requests.post(url, json=data, headers=headers)
execution_id = response.json()["execution_id"]

print(f"Research started: {execution_id}")
```

**JavaScript:**
```javascript
const axios = require('axios');

const url = 'https://api.autoresearch.ai/v1/research';
const headers = {
  'Authorization': 'Bearer ar_1234abcd...',
  'Content-Type': 'application/json'
};
const data = {
  topic: 'Benefits of meditation',
  targetLength: 1500
};

// Create research
axios.post(url, data, { headers })
  .then(response => {
    const executionId = response.data.execution_id;
    console.log(`Research started: ${executionId}`);
  });
```

---

### Example 2: Poll for Completion

**Python:**
```python
import requests
import time

def wait_for_completion(execution_id, api_key):
    url = f"https://api.autoresearch.ai/v1/research/{execution_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    while True:
        response = requests.get(url, headers=headers)
        status = response.json()["status"]
        
        print(f"Status: {status}")
        
        if status in ["completed", "failed", "partial"]:
            break
        
        time.sleep(5)  # Poll every 5 seconds
    
    # Get result
    result_url = f"{url}/result"
    result = requests.get(result_url, headers=headers).json()
    return result

# Usage
execution_id = "exec_20241125_143022"
result = wait_for_completion(execution_id, "ar_1234abcd...")

print(f"Title: {result['article']['title']}")
print(f"Quality: {result['quality']['overall']}")
```

---

### Example 3: Complete Workflow with Error Handling

**Python:**
```python
import requests
import time
from typing import Optional

class AutoResearchClient:
    def __init__(self, api_key: str, base_url: str = "https://api.autoresearch.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_research(self, topic: str, **kwargs) -> str:
        """Create a new research request."""
        url = f"{self.base_url}/v1/research"
        data = {"topic": topic, **kwargs}
        
        try:
            response = requests.post(url, json=data, headers=self.headers)
            response.raise_for_status()
            return response.json()["execution_id"]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                error = e.response.json()["error"]
                raise ValueError(f"Validation error: {error['message']}")
            elif e.response.status_code == 429:
                retry_after = e.response.headers.get('Retry-After', 60)
                raise Exception(f"Rate limited. Retry after {retry_after}s")
            else:
                raise
    
    def get_status(self, execution_id: str) -> dict:
        """Get research status."""
        url = f"{self.base_url}/v1/research/{execution_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_result(self, execution_id: str) -> Optional[dict]:
        """Get research result if ready."""
        url = f"{self.base_url}/v1/research/{execution_id}/result"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 202:
            return None  # Not ready yet
        
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(
        self, 
        execution_id: str, 
        poll_interval: int = 5,
        max_wait: int = 600
    ) -> dict:
        """Wait for research to complete."""
        start_time = time.time()
        
        while True:
            # Check timeout
            if time.time() - start_time > max_wait:
                raise TimeoutError("Research did not complete in time")
            
            # Check status
            status = self.get_status(execution_id)
            current_status = status["status"]
            
            if current_status == "completed":
                return self.get_result(execution_id)
            
            elif current_status == "failed":
                error = status.get("error", {})
                raise Exception(f"Research failed: {error.get('message')}")
            
            elif current_status == "partial":
                result = self.get_result(execution_id)
                print("WARNING: Research completed with warnings")
                return result
            
            # Wait before next poll
            time.sleep(poll_interval)

# Usage
client = AutoResearchClient(api_key="ar_1234abcd...")

try:
    # Create research
    execution_id = client.create_research(
        topic="Python programming best practices",
        target_length=2000,
        research_depth="deep"
    )
    print(f"Research started: {execution_id}")
    
    # Wait for completion
    result = client.wait_for_completion(execution_id)
    
    # Process result
    print(f"\nTitle: {result['article']['title']}")
    print(f"Words: {result['article']['word_count']}")
    print(f"Quality: {result['quality']['overall']:.2f}")
    print(f"Sources: {len(result['sources'])}")
    print(f"Cost: ${result['metrics']['total_cost']:.2f}")
    print(f"Duration: {result['metrics']['total_duration_seconds']:.1f}s")
    
    # Save article
    with open('article.md', 'w') as f:
        f.write(result['article']['content'])
    print("\nArticle saved to article.md")
    
except ValueError as e:
    print(f"Validation error: {e}")
except TimeoutError as e:
    print(f"Timeout: {e}")
except Exception as e:
    print(f"Error: {e}")
```

---

### Example 4: Batch Processing

**Python:**
```python
import concurrent.futures
from typing import List

def generate_article(topic: str) -> dict:
    """Generate single article."""
    client = AutoResearchClient(api_key="ar_1234abcd...")
    execution_id = client.create_research(topic=topic, target_length=1500)
    return client.wait_for_completion(execution_id)

def batch_generate(topics: List[str], max_workers: int = 5):
    """Generate multiple articles in parallel."""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        futures = {
            executor.submit(generate_article, topic): topic 
            for topic in topics
        }
        
        # Collect results
        for future in concurrent.futures.as_completed(futures):
            topic = futures[future]
            try:
                result = future.result()
                results.append({
                    "topic": topic,
                    "success": True,
                    "result": result
                })
                print(f"✓ Completed: {topic}")
            except Exception as e:
                results.append({
                    "topic": topic,
                    "success": False,
                    "error": str(e)
                })
                print(f"✗ Failed: {topic} - {e}")
    
    return results

# Usage
topics = [
    "Benefits of meditation",
    "History of artificial intelligence",
    "Climate change solutions",
    "Healthy eating habits",
    "Remote work best practices"
]

results = batch_generate(topics, max_workers=3)

# Summary
successful = sum(1 for r in results if r["success"])
print(f"\n{successful}/{len(topics)} articles generated successfully")
```

---

### Example 5: Webhook Handler (Flask)

**Python:**
```python
from flask import Flask, request, jsonify
import hmac
import hashlib
import os

app = Flask(__name__)

WEBHOOK_SECRET = os.getenv("AUTORESEARCH_WEBHOOK_SECRET")

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify webhook signature."""
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.route('/webhooks/autoresearch', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-AutoResearch-Signature')
    if not verify_signature(request.data, signature):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Parse event
    event = request.json
    event_type = event['type']
    data = event['data']
    
    # Handle different event types
    if event_type == 'research.completed':
        handle_completion(data)
    elif event_type == 'research.failed':
        handle_failure(data)
    elif event_type == 'research.partial':
        handle_partial(data)
    
    return jsonify({"status": "received"}), 200

def handle_completion(data):
    """Handle successful completion."""
    execution_id = data['execution_id']
    print(f"Research {execution_id} completed!")
    
    # Fetch full result
    client = AutoResearchClient(api_key="ar_1234abcd...")
    result = client.get_result(execution_id)
    
    # Store in database, send email, etc.
    # ...

def handle_failure(data):
    """Handle failure."""
    execution_id = data['execution_id']
    error = data['error_message']
    print(f"Research {execution_id} failed: {error}")
    
    # Send notification, log error, etc.
    # ...

def handle_partial(data):
    """Handle partial completion."""
    execution_id = data['execution_id']
    print(f"Research {execution_id} completed with warnings")
    
    # Decide whether to accept or retry
    # ...

if __name__ == '__main__':
    app.run(port=5000)
```

---

## 🔗 Quick Reference

### Base URLs
```
Production:   https://api.autoresearch.ai
Staging:      https://staging-api.autoresearch.ai
Development:  http://localhost:8000
```

### Authentication
```
Header: Authorization: Bearer {api_key}
Format: ar_{32_characters}
```

### Key Endpoints
```
POST   /v1/research              # Create research
GET    /v1/research/{id}         # Get status
GET    /v1/research/{id}/result  # Get result
DELETE /v1/research/{id}         # Cancel
```

### Rate Limits
```
Free:       10/min,   100/hour,   1,000/day
Starter:    30/min,   500/hour,   5,000/day
Pro:       100/min, 2,000/hour,  20,000/day
```

### Status Values
```
queued      # Waiting to start
processing  # Currently generating
completed   # Success
partial     # Completed with warnings
failed      # Failed with errors
cancelled   # User cancelled
```

---

## 📚 Additional Resources

**Developer Portal:**
- Dashboard: https://dashboard.autoresearch.ai
- API Keys: https://dashboard.autoresearch.ai/api-keys
- Usage Stats: https://dashboard.autoresearch.ai/usage

**Documentation:**
- Full Docs: https://docs.autoresearch.ai
- Architecture: [02_ARCHITECTURE.md](./02_ARCHITECTURE.md)
- Data Models: [03_DATA_MODELS.md](./03_DATA_MODELS.md)

**Support:**
- Email: api-support@autoresearch.ai
- Discord: https://discord.gg/autoresearch
- Status Page: https://status.autoresearch.ai

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2024  
**API Version**: v1  
**Target Audience**: Developers, API Consumers

---

END OF API REFERENCE