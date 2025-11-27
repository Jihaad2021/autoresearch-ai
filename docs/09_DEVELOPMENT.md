# Development Guide - AutoResearch AI

**Last Updated**: November 25, 2024  
**Version**: 1.0  
**Status**: Sprint 1 Complete, Sprint 2-4 Planned

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Project Structure](#project-structure)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Adding New Components](#adding-new-components)
6. [Testing Strategy](#testing-strategy)
7. [Debugging Guide](#debugging-guide)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Getting Started

### Prerequisites

**Required:**
- Python 3.12+
- Git
- Virtual environment tool (venv or conda)

**Recommended:**
- VS Code or PyCharm
- Docker (for deployment)
- Postman or similar (for API testing)

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/yourusername/autoResearchAI.git
cd autoResearchAI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run tests to verify setup
pytest tests/ -v

# 6. Run a simple example
python examples/simple_article.py
```

**First Run Expected Output:**
```
✓ Environment validated
✓ Dependencies loaded
✓ Mock workers initialized
✓ Running simple article generation...

Execution ID: exec_20241125_143022
Phase: INITIALIZED → PLANNING → EXECUTING → COMPLETED
Quality: 0.88
Duration: 15 seconds
Cost: $2.35 (mock)

✓ Article generated successfully!
```

---

## 📁 Project Structure

### Directory Layout
```
autoResearchAI/
│
├── src/                          # Source code
│   ├── __init__.py
│   │
│   ├── schemas/                  # Data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── brief.py             # User input schema
│   │   ├── plan.py              # Execution plan schema
│   │   ├── task.py              # Task tracking schema
│   │   ├── state.py             # Workflow state schema
│   │   ├── worker.py            # Worker I/O schema
│   │   ├── result.py            # Final output schema
│   │   └── enums.py             # All enums
│   │
│   ├── meta_agent/              # Meta agents (orchestration)
│   │   ├── __init__.py
│   │   ├── controller.py        # Main coordinator
│   │   ├── state_manager.py    # State management
│   │   ├── planner.py           # Plan creation
│   │   ├── strategy.py          # Plan optimization
│   │   ├── orchestrator.py     # Worker execution
│   │   ├── supervisor.py        # Quality evaluation
│   │   └── merger.py            # Output packaging
│   │
│   ├── workers/                 # Workers (task executors)
│   │   ├── __init__.py
│   │   ├── base_worker.py       # Base worker class
│   │   ├── registry.py          # Worker registry
│   │   │
│   │   ├── research/            # Research workers
│   │   │   ├── web_search.py
│   │   │   ├── academic_search.py
│   │   │   ├── news_search.py
│   │   │   ├── web_scraper.py
│   │   │   └── social_media.py
│   │   │
│   │   ├── analysis/            # Analysis workers
│   │   │   ├── content_synthesizer.py
│   │   │   ├── summarization.py
│   │   │   └── insight_extractor.py
│   │   │
│   │   ├── writing/             # Writing workers
│   │   │   ├── introduction_writer.py
│   │   │   ├── article_writer.py
│   │   │   ├── conclusion_writer.py
│   │   │   └── citation_formatter.py
│   │   │
│   │   └── quality/             # Quality workers
│   │       ├── fact_checker.py
│   │       ├── editor.py
│   │       ├── seo_optimizer.py
│   │       ├── readability_checker.py
│   │       └── plagiarism_checker.py
│   │
│   ├── api/                     # API layer (Sprint 3)
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── routes.py            # API endpoints
│   │   └── middleware.py        # Auth, logging, etc.
│   │
│   ├── ui/                      # User interface (Sprint 4)
│   │   ├── __init__.py
│   │   └── streamlit_app.py    # Streamlit UI
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       ├── logger.py            # Logging configuration
│       ├── config.py            # Configuration management
│       └── exceptions.py        # Custom exceptions
│
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures
│   │
│   ├── unit/                    # Unit tests
│   │   ├── test_schemas.py
│   │   ├── test_agents.py
│   │   └── test_workers.py
│   │
│   ├── integration/             # Integration tests
│   │   ├── test_workflow.py
│   │   └── test_end_to_end.py
│   │
│   └── fixtures/                # Test data
│       ├── sample_briefs.json
│       └── expected_outputs.json
│
├── docs/                        # Documentation
│   ├── 01_PROJECT_OVERVIEW.md
│   ├── 02_ARCHITECTURE.md
│   ├── 03_DATA_MODELS.md
│   ├── 04_AGENTS.md
│   ├── 05_WORKERS.md
│   ├── 06_WORKFLOW.md
│   └── 09_DEVELOPMENT.md (this file)
│
├── examples/                    # Example scripts
│   ├── simple_article.py        # Basic usage
│   ├── research_report.py       # Complex example
│   └── batch_processing.py      # Multiple articles
│
├── config/                      # Configuration files
│   ├── development.yaml
│   ├── production.yaml
│   └── test.yaml
│
├── .env.example                 # Environment template
├── .gitignore
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Dev dependencies
├── setup.py                     # Package setup
├── pytest.ini                   # Pytest configuration
├── README.md                    # Project README
└── LICENSE

Total: ~50 files organized in clear structure
```

---

### Key Directories Explained

**`src/schemas/`** - Data Contracts
```
Contains all Pydantic models
Pure data, no business logic
Imported by all other modules
Changes here affect everything
```

**`src/meta_agent/`** - Orchestration Layer
```
7 meta agents
Manage workflow and decisions
Don't call external APIs directly
Coordinate workers
```

**`src/workers/`** - Execution Layer
```
17+ workers
Call external APIs/tools
Stateless (input → output)
Can be added/removed easily
```

**`tests/`** - Quality Assurance
```
Unit tests (fast, isolated)
Integration tests (slower, real workflow)
Fixtures (reusable test data)
80%+ coverage target
```

---

## ⚙️ Development Setup

### Step-by-Step Setup

#### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Verify Python version
python --version  # Should be 3.12+
```

#### 2. Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (includes testing, linting)
pip install -r requirements-dev.txt
```

**Core Dependencies** (`requirements.txt`):
```
# LLM & AI
anthropic==0.18.0           # Claude API
langchain==0.1.0            # Framework
langchain-anthropic==0.1.0  # Claude integration
langgraph==0.0.25          # State machine

# Data & Validation
pydantic==2.5.0            # Data models
pydantic-settings==2.1.0   # Settings management

# External APIs
tavily-python==0.3.0       # Web search
arxiv==2.0.0               # Academic search
newsapi-python==0.2.7      # News search
firecrawl==0.0.10          # Web scraping

# Utilities
python-dotenv==1.0.0       # Environment variables
requests==2.31.0           # HTTP client
```

**Dev Dependencies** (`requirements-dev.txt`):
```
# Testing
pytest==7.4.0              # Test framework
pytest-cov==4.1.0          # Coverage
pytest-asyncio==0.21.0     # Async testing
pytest-mock==3.12.0        # Mocking

# Code Quality
black==23.12.0             # Formatting
isort==5.13.0              # Import sorting
flake8==7.0.0              # Linting
mypy==1.8.0                # Type checking

# Documentation
mkdocs==1.5.3              # Docs generation
```

#### 3. Environment Variables

**Create `.env` file:**
```bash
cp .env.example .env
```

**Edit `.env` with your API keys:**
```env
# Required API Keys
ANTHROPIC_API_KEY=sk-ant-...          # Claude API
TAVILY_API_KEY=tvly-...               # Web search

# Optional API Keys (Sprint 2+)
NEWS_API_KEY=...                       # News search
FIRECRAWL_API_KEY=...                  # Web scraping

# Configuration
ENVIRONMENT=development                # development/production
LOG_LEVEL=INFO                         # DEBUG/INFO/WARNING/ERROR
MAX_ITERATIONS=3                       # Max workflow iterations

# Costs & Limits
DEFAULT_MAX_BUDGET=5.00                # Default budget per article
DEFAULT_MAX_TIME=1200                  # Default time limit (seconds)

# Worker Configuration
ENABLE_RESEARCH_WORKERS=true
ENABLE_QUALITY_WORKERS=true
```

#### 4. Verify Setup
```bash
# Run setup verification script
python scripts/verify_setup.py
```

**Expected Output:**
```
✓ Python version: 3.12.0
✓ Virtual environment: Active
✓ Dependencies: All installed (25/25)
✓ Environment variables: Configured
  ✓ ANTHROPIC_API_KEY: Set
  ✓ TAVILY_API_KEY: Set
  ⚠ NEWS_API_KEY: Not set (optional)
✓ Project structure: Valid
✓ Tests: Passing (48/48)

Setup complete! You're ready to develop.
```

---

### IDE Configuration

#### VS Code Setup

**Install Extensions:**
```
Python (Microsoft)
Pylance (Microsoft)
Python Test Explorer
autoDocstring
GitLens
```

**`.vscode/settings.json`:**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true,
  "editor.rulers": [88],
  "[python]": {
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

**`.vscode/launch.json`** (for debugging):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "justMyCode": true
    },
    {
      "name": "Run Simple Example",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/examples/simple_article.py",
      "console": "integratedTerminal"
    },
    {
      "name": "Run Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["tests/", "-v"],
      "console": "integratedTerminal"
    }
  ]
}
```

#### PyCharm Setup

**Configure Interpreter:**
```
Settings → Project → Python Interpreter
→ Add Interpreter → Existing Environment
→ Select venv/bin/python
```

**Enable Tools:**
```
Settings → Tools → Python Integrated Tools
→ Testing: pytest
→ Type checker: mypy
→ Docstring format: Google
```

---

## 📝 Coding Standards

### Python Style Guide

**We follow PEP 8 with some modifications:**

#### 1. Formatting

**Line Length:**
```python
# Maximum 88 characters (Black default)
# Not 79 (PEP 8) - Black uses 88 for better readability
```

**Imports:**
```python
# Standard library
import os
import sys
from datetime import datetime
from typing import List, Optional, Dict

# Third-party
import anthropic
from pydantic import BaseModel, Field

# Local
from src.schemas.brief import Brief
from src.meta_agent.controller import Controller
```

**Formatting Tool:**
```bash
# Format all code
black src/ tests/

# Check without modifying
black --check src/

# Sort imports
isort src/ tests/
```

#### 2. Naming Conventions
```python
# Classes: PascalCase
class ContentSynthesizer:
    pass

# Functions/Methods: snake_case
def execute_workflow(brief: Brief) -> FinalOutput:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_ITERATIONS = 3
DEFAULT_TIMEOUT = 30

# Private methods: _leading_underscore
def _helper_method(self):
    pass

# Variables: snake_case
user_input = "..."
execution_id = "exec_123"
```

#### 3. Type Hints

**Always use type hints:**
```python
# ✅ Good
def create_plan(brief: Brief) -> Plan:
    return Plan(...)

def calculate_score(accuracy: float, completeness: float) -> float:
    return (accuracy + completeness) / 2

# ❌ Bad
def create_plan(brief):  # No types
    return Plan(...)
```

**Complex types:**
```python
from typing import List, Dict, Optional, Union

def process_results(
    results: List[Dict[str, any]],
    config: Optional[Dict] = None
) -> Union[FinalOutput, None]:
    pass
```

#### 4. Docstrings

**Use Google-style docstrings:**
```python
def execute_workflow(brief: Brief, config: Optional[Dict] = None) -> FinalOutput:
    """Execute the complete content generation workflow.
    
    This function orchestrates all meta agents to process a user's brief
    and generate a complete article with quality checks and iterations.
    
    Args:
        brief: User's content generation request containing topic, requirements,
            and constraints.
        config: Optional configuration overrides for workflow execution.
            Defaults to system configuration.
    
    Returns:
        FinalOutput containing the generated article, quality scores,
        sources, and execution metrics.
    
    Raises:
        ValidationError: If the brief is invalid or missing required fields.
        WorkflowError: If a critical error occurs during execution.
        BudgetExceededError: If execution exceeds the specified budget.
    
    Example:
        >>> brief = Brief(
        ...     topic="AI in healthcare",
        ...     content_type=ContentType.ARTICLE,
        ...     target_length=2000
        ... )
        >>> output = execute_workflow(brief)
        >>> print(output.article.title)
        "AI Trends in Healthcare 2024"
    """
    # Implementation
    pass
```

**Class docstrings:**
```python
class Controller:
    """Main workflow controller that orchestrates all meta agents.
    
    The Controller is the entry point for all content generation workflows.
    It coordinates the execution of planning, strategy, orchestration,
    evaluation, and merging phases.
    
    Attributes:
        state_manager: Manages workflow state transitions and tracking.
        planner: Creates execution plans from user briefs.
        strategy: Optimizes plans for efficiency.
        orchestrator: Executes workers according to the plan.
        supervisor: Evaluates quality and decides on iterations.
        merger: Packages final output for delivery.
    
    Example:
        >>> controller = Controller()
        >>> brief = Brief(topic="AI trends", ...)
        >>> output = controller.execute(brief)
    """
    pass
```

#### 5. Error Handling

**Be explicit and specific:**
```python
# ✅ Good - Specific exceptions
try:
    worker_output = worker.execute(input_data)
except APITimeoutError as e:
    logger.warning(f"Worker {worker.id} timeout: {e}")
    raise WorkerExecutionError(f"Worker failed: {e}") from e
except ValidationError as e:
    logger.error(f"Invalid worker output: {e}")
    raise
finally:
    # Always track metrics
    state.add_cost(worker_output.cost)

# ❌ Bad - Generic exceptions
try:
    worker_output = worker.execute(input_data)
except Exception as e:  # Too broad
    print(f"Error: {e}")  # Don't use print
    pass  # Don't silently ignore
```

**Custom exceptions:**
```python
# src/utils/exceptions.py
class AutoResearchError(Exception):
    """Base exception for all AutoResearch errors."""
    pass

class WorkflowError(AutoResearchError):
    """Workflow execution error."""
    pass

class WorkerExecutionError(WorkflowError):
    """Worker failed to execute."""
    pass

class BudgetExceededError(WorkflowError):
    """Budget limit exceeded."""
    pass
```

#### 6. Logging

**Use structured logging:**
```python
import logging

logger = logging.getLogger(__name__)

# ✅ Good - Structured with context
logger.info(
    "Workflow started",
    extra={
        "execution_id": execution_id,
        "topic": brief.topic,
        "estimated_cost": plan.estimated_total_cost
    }
)

logger.warning(
    "Worker failed, retrying",
    extra={
        "worker_id": worker.id,
        "attempt": retry_count,
        "error": str(error)
    }
)

# ❌ Bad - Unstructured
print("Workflow started")  # Don't use print
logger.info("Worker failed")  # No context
```

**Log levels:**
```python
# DEBUG: Detailed diagnostic info
logger.debug(f"Processing step {step_index} with {len(workers)} workers")

# INFO: General informational messages
logger.info(f"Phase transition: {old_phase} → {new_phase}")

# WARNING: Something unexpected but handled
logger.warning(f"Optional worker {worker_id} failed, skipping")

# ERROR: Error that prevents task completion
logger.error(f"Critical worker {worker_id} failed after 3 retries")

# CRITICAL: System-level failure
logger.critical(f"Database connection lost, aborting workflow")
```

---

### Code Organization Principles

#### 1. Single Responsibility
```python
# ✅ Good - Each function does one thing
def calculate_quality_score(quality_results: List[Dict]) -> float:
    """Calculate overall quality score from individual results."""
    scores = [r["score"] for r in quality_results]
    return sum(scores) / len(scores)

def meets_threshold(score: float, threshold: float) -> bool:
    """Check if score meets minimum threshold."""
    return score >= threshold

# ❌ Bad - Function does too much
def evaluate_and_decide(state):
    # Calculate score
    score = ...
    # Check threshold
    if score >= threshold:
        # Make decision
        return "complete"
    else:
        # Create feedback
        feedback = ...
        # Update state
        state.feedback = feedback
        return "continue"
```

#### 2. Separation of Concerns
```python
# ✅ Good - Clear separation
# Data model (schemas/brief.py)
class Brief(BaseModel):
    topic: str
    content_type: ContentType

# Business logic (meta_agent/planner.py)
class Planner:
    def create_plan(self, brief: Brief) -> Plan:
        # Planning logic here
        pass

# API layer (api/routes.py)
@app.post("/research")
async def create_research(brief: Brief):
    controller = Controller()
    return controller.execute(brief)
```

#### 3. DRY (Don't Repeat Yourself)
```python
# ✅ Good - Reusable function
def add_agent_action(
    state: AgentState,
    agent_name: str,
    action: str,
    details: Optional[Dict] = None
):
    """Add agent action to state with timestamp."""
    state.agent_actions.append({
        "agent_name": agent_name,
        "action": action,
        "timestamp": datetime.now(),
        "details": details or {}
    })

# Use it everywhere
add_agent_action(state, "Planner", "create_plan", {"steps": 4})
add_agent_action(state, "Strategy", "optimize", {"cost_saved": 0.50})

# ❌ Bad - Duplicated code
# In planner.py
state.agent_actions.append({
    "agent_name": "Planner",
    "action": "create_plan",
    "timestamp": datetime.now(),
    ...
})

# In strategy.py (duplicate!)
state.agent_actions.append({
    "agent_name": "Strategy",
    "action": "optimize",
    "timestamp": datetime.now(),
    ...
})
```

---

## ➕ Adding New Components

### Adding a New Worker

**Scenario**: You want to add a Twitter search worker.

#### Step 1: Create Worker File
```python
# src/workers/research/twitter_search.py

from typing import Dict, List
from src.workers.base_worker import BaseWorker
from src.schemas.worker import WorkerInput, WorkerOutput

class TwitterSearchWorker(BaseWorker):
    """Search Twitter for recent discussions and trends.
    
    This worker uses the Twitter API to find relevant tweets,
    threads, and trending topics related to the search query.
    """
    
    def __init__(self):
        super().__init__(
            worker_id="twitter_search",
            name="Twitter Search Worker",
            category="research",
            description="Search Twitter for discussions and trends"
        )
    
    def execute(self, input_data: WorkerInput) -> WorkerOutput:
        """Execute Twitter search.
        
        Args:
            input_data: Contains query, max_results, days_back
            
        Returns:
            WorkerOutput with tweets and engagement metrics
        """
        try:
            # Extract parameters
            query = input_data.context.get("query")
            max_results = input_data.context.get("max_results", 10)
            days_back = input_data.context.get("days_back", 7)
            
            # Call Twitter API (mock in Sprint 1)
            tweets = self._search_twitter(query, max_results, days_back)
            
            # Process results
            result = {
                "tweets": tweets,
                "total_found": len(tweets),
                "trending_topics": self._extract_trends(tweets)
            }
            
            # Return success
            return WorkerOutput(
                task_id=input_data.task_id,
                worker_id=self.worker_id,
                success=True,
                result=result,
                cost=0.01,  # Twitter API cost
                tokens_used=0,
                execution_time_seconds=2.5
            )
            
        except Exception as e:
            # Return failure
            return WorkerOutput(
                task_id=input_data.task_id,
                worker_id=self.worker_id,
                success=False,
                error=str(e),
                cost=0,
                tokens_used=0,
                execution_time_seconds=0
            )
    
    def _search_twitter(
        self, 
        query: str, 
        max_results: int, 
        days_back: int
    ) -> List[Dict]:
        """Search Twitter API (to be implemented)."""
        # TODO: Implement Twitter API call in Sprint 2
        # For now, return mock data
        return [
            {
                "text": f"Mock tweet about {query}",
                "user": "user123",
                "likes": 150,
                "retweets": 45,
                "url": "https://twitter.com/..."
            }
        ]
    
    def _extract_trends(self, tweets: List[Dict]) -> List[str]:
        """Extract trending topics from tweets."""
        # Simple implementation
        # TODO: Improve with NLP in Sprint 3
        return ["trend1", "trend2", "trend3"]
```

#### Step 2: Register Worker
```python
# src/workers/registry.py

from src.workers.research.twitter_search import TwitterSearchWorker

# In registry initialization
def initialize_registry():
    """Initialize worker registry with all available workers."""
    registry = WorkerRegistry()
    
    # Research workers
    registry.register(WebSearchWorker())
    registry.register(AcademicSearchWorker())
    registry.register(TwitterSearchWorker())  # ← Add here
    # ... other workers
    
    return registry
```

#### Step 3: Add Tests
```python
# tests/unit/workers/test_twitter_search.py

import pytest
from src.workers.research.twitter_search import TwitterSearchWorker
from src.schemas.worker import WorkerInput

def test_twitter_search_success():
    """Test successful Twitter search."""
    # Arrange
    worker = TwitterSearchWorker()
    input_data = WorkerInput(
        task_id="test_001",
        worker_id="twitter_search",
        context={
            "query": "AI healthcare",
            "max_results": 10,
            "days_back": 7
        }
    )
    
    # Act
    output = worker.execute(input_data)
    
    # Assert
    assert output.success is True
    assert "tweets" in output.result
    assert len(output.result["tweets"]) > 0
    assert output.cost > 0

def test_twitter_search_handles_error():
    """Test Twitter search handles API errors."""
    # Test error handling
    pass
```

#### Step 4: Update Documentation
```python
# Add to worker's docstring
"""
Usage Example:
    >>> worker = TwitterSearchWorker()
    >>> input_data = WorkerInput(
    ...     task_id="task_001",
    ...     worker_id="twitter_search",
    ...     context={"query": "AI trends", "max_results": 20}
    ... )
    >>> output = worker.execute(input_data)
    >>> print(output.result["tweets"][0])
    
Cost: ~$0.01 per search
Speed: 2-3 seconds
Sprint: Available from Sprint 2
"""
```

#### Step 5: Use in Planner
```python
# src/meta_agent/planner.py

def _select_research_workers(self, brief: Brief) -> List[str]:
    """Select appropriate research workers based on brief."""
    workers = ["web_search"]  # Always include
    
    # Add academic if needed
    if self._needs_academic_sources(brief):
        workers.append("academic_search")
    
    # Add Twitter if social context important
    if self._needs_social_context(brief):
        workers.append("twitter_search")  # ← Use new worker
    
    return workers
```

---

### Adding a New Meta Agent

**Scenario**: You want to add a Citation Validator agent.

#### Step 1: Create Agent File
```python
# src/meta_agent/citation_validator.py

from typing import List
from src.schemas.state import AgentState
from src.schemas.result import Source

class CitationValidator:
    """Validates that all citations in the article are accurate.
    
    This agent checks that:
    - All cited sources actually exist in research results
    - Citation format is consistent
    - No broken or invalid URLs
    - Sources are properly attributed
    """
    
    def validate(self, state: AgentState) -> Dict[str, any]:
        """Validate all citations in the article.
        
        Args:
            state: Current workflow state with article and sources
            
        Returns:
            Validation results with issues found
        """
        # Record action
        state.add_agent_action(
            agent_name="CitationValidator",
            action="validate_citations"
        )
        
        # Get article and sources
        article = self._get_article(state)
        sources = self._get_sources(state)
        
        # Extract citations from article
        citations = self._extract_citations(article)
        
        # Validate each citation
        issues = []
        for citation in citations:
            if not self._is_valid_citation(citation, sources):
                issues.append(citation)
        
        # Create result
        result = {
            "total_citations": len(citations),
            "valid_citations": len(citations) - len(issues),
            "invalid_citations": len(issues),
            "issues": issues,
            "validation_passed": len(issues) == 0
        }
        
        return result
    
    def _extract_citations(self, article: str) -> List[str]:
        """Extract all citation markers from article."""
        # Implementation
        pass
    
    def _is_valid_citation(
        self, 
        citation: str, 
        sources: List[Source]
    ) -> bool:
        """Check if citation references a valid source."""
        # Implementation
        pass
```

#### Step 2: Integrate into Workflow
```python
# src/meta_agent/controller.py

class Controller:
    def __init__(self):
        self.state_manager = StateManager()
        self.planner = Planner()
        self.strategy = Strategy()
        self.orchestrator = Orchestrator()
        self.supervisor = Supervisor()
        self.merger = Merger()
        self.citation_validator = CitationValidator()  # ← Add new agent
    
    def execute(self, brief: Brief) -> FinalOutput:
        """Execute workflow with citation validation."""
        # ... existing code ...
        
        # After quality checks, before merging
        if state.current_phase == WorkflowPhase.EVALUATING:
            # Validate citations
            validation_result = self.citation_validator.validate(state)
            
            # If citations invalid, flag in state
            if not validation_result["validation_passed"]:
                state.add_warning(
                    f"Found {validation_result['invalid_citations']} "
                    f"invalid citations"
                )
        
        # ... continue with merging ...
```

#### Step 3: Add Tests
```python
# tests/unit/meta_agent/test_citation_validator.py

def test_validates_correct_citations():
    """Test validator passes valid citations."""
    pass

def test_detects_invalid_citations():
    """Test validator detects missing sources."""
    pass

def test_validates_citation_format():
    """Test validator checks citation format."""
    pass
```

---

### Adding a New Schema

**Scenario**: You want to add feedback tracking.
```python
# src/schemas/feedback.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserFeedback(BaseModel):
    """User feedback on generated content.
    
    Captures user's rating and comments on the quality
    of generated articles for continuous improvement.
    """
    
    execution_id: str = Field(
        ...,
        description="ID of the execution that generated content"
    )
    
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="User rating (1-5 stars)"
    )
    
    quality_aspects: dict = Field(
        default_factory=dict,
        description="Ratings for specific aspects (accuracy, clarity, etc.)"
    )
    
    comments: Optional[str] = Field(
        None,
        max_length=1000,
        description="User's written feedback"
    )
    
    would_use_again: bool = Field(
        ...,
        description="Whether user would use system again"
    )
    
    submitted_at: datetime = Field(
        default_factory=datetime.now,
        description="When feedback was submitted"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec_20241125_143022",
                "rating": 4,
                "quality_aspects": {
                    "accuracy": 5,
                    "clarity": 4,
                    "completeness": 4
                },
                "comments": "Great article but could use more examples",
                "would_use_again": True
            }
        }
```

---

## 🧪 Testing Strategy

### Test Pyramid
```
         ┌─────────────┐
         │ E2E Tests   │  10% - Full workflow
         │   (Slow)    │
         ├─────────────┤
         │Integration  │  30% - Component interaction
         │   Tests     │
         ├─────────────┤
         │ Unit Tests  │  60% - Individual functions
         │   (Fast)    │
         └─────────────┘
```

### Unit Tests

**What to test:**
- Individual functions
- Schema validation
- Single agent methods
- Worker execution

**Example:**
```python
# tests/unit/test_schemas.py

def test_brief_validation():
    """Test Brief schema validates input correctly."""
    # Valid brief
    brief = Brief(
        topic="AI trends",
        content_type=ContentType.ARTICLE,
        target_length=2000
    )
    assert brief.topic == "AI trends"
    
    # Invalid brief (too short topic)
    with pytest.raises(ValidationError):
        Brief(topic="", content_type=ContentType.ARTICLE, target_length=2000)
    
    # Invalid brief (length out of range)
    with pytest.raises(ValidationError):
        Brief(topic="Valid", content_type=ContentType.ARTICLE, target_length=100)

def test_plan_step_creation():
    """Test PlanStep can be created with valid data."""
    step = PlanStep(
        step_id="step_1",
        description="Research phase",
        workers=["web_search", "academic_search"],
        execution_mode=ExecutionMode.PARALLEL,
        estimated_time=300,
        estimated_cost=0.50
    )
    assert len(step.workers) == 2
    assert step.execution_mode == ExecutionMode.PARALLEL
```

**Run unit tests:**
```bash
# All unit tests
pytest tests/unit/ -v

# Specific test file
pytest tests/unit/test_schemas.py -v

# Specific test function
pytest tests/unit/test_schemas.py::test_brief_validation -v

# With coverage
pytest tests/unit/ --cov=src --cov-report=html
```

---

### Integration Tests

**What to test:**
- Agent interactions
- Worker coordination
- State transitions
- End-to-end workflow

**Example:**
```python
# tests/integration/test_workflow.py

def test_complete_workflow():
    """Test complete workflow from brief to output."""
    # Create brief
    brief = Brief(
        topic="Python programming basics",
        content_type=ContentType.ARTICLE,
        target_length=1000,
        research_depth=ResearchDepth.LIGHT
    )
    
    # Execute workflow
    controller = Controller()
    output = controller.execute(brief)
    
    # Verify output
    assert output.status == "completed"
    assert output.article.word_count >= 950  # Close to target
    assert output.article.word_count <= 1050
    assert len(output.sources) >= 3  # Minimum sources
    assert output.quality.overall >= 0.70  # Decent quality

def test_iteration_workflow():
    """Test workflow iterates when quality low."""
    # Create brief with high quality requirement
    brief = Brief(
        topic="Complex topic",
        min_quality_score=0.90  # High threshold
    )
    
    # Execute
    controller = Controller()
    output = controller.execute(brief)
    
    # May require iterations
    assert output.metrics.iteration_count >= 1
    # Should eventually meet threshold or hit max iterations
    assert (output.quality.overall >= 0.90 or 
            output.metrics.iteration_count == 3)
```

**Run integration tests:**
```bash
# All integration tests
pytest tests/integration/ -v

# Slow tests (marked as slow)
pytest tests/integration/ -v -m slow

# Skip slow tests
pytest tests/integration/ -v -m "not slow"
```

---

### Test Fixtures

**Reusable test data:**
```python
# tests/conftest.py

import pytest
from src.schemas.brief import Brief, ContentType
from src.schemas.state import AgentState

@pytest.fixture
def sample_brief():
    """Provide a standard brief for testing."""
    return Brief(
        topic="AI in healthcare",
        content_type=ContentType.ARTICLE,
        target_length=2000,
        tone=ToneStyle.PROFESSIONAL
    )

@pytest.fixture
def initialized_state(sample_brief):
    """Provide an initialized AgentState."""
    state = AgentState(
        execution_id="test_exec_001",
        brief=sample_brief,
        current_phase=WorkflowPhase.INITIALIZED
    )
    return state

@pytest.fixture
def mock_worker_output():
    """Provide mock worker output."""
    return WorkerOutput(
        task_id="task_001",
        worker_id="web_search",
        success=True,
        result={"sources": [{"title": "Test", "url": "https://..."}]},
        cost=0.02,
        tokens_used=100,
        execution_time_seconds=2.0
    )

# Use in tests
def test_something(sample_brief, initialized_state):
    """Test using fixtures."""
    assert sample_brief.topic == "AI in healthcare"
    assert initialized_state.brief == sample_brief
```

---

### Mocking External APIs

**Why mock?**
- Tests run faster (no real API calls)
- Tests don't cost money
- Tests work offline
- Tests are deterministic

**Example:**
```python
# tests/unit/workers/test_web_search.py

from unittest.mock import Mock, patch
import pytest

@patch('src.workers.research.web_search.tavily_client')
def test_web_search_worker(mock_tavily):
    """Test web search worker with mocked API."""
    # Setup mock response
    mock_tavily.search.return_value = {
        "results": [
            {
                "title": "Test Article",
                "url": "https://example.com",
                "content": "Test content"
            }
        ]
    }
    
    # Create worker and execute
    worker = WebSearchWorker()
    output = worker.execute(WorkerInput(
        task_id="test",
        worker_id="web_search",
        context={"query": "test query"}
    ))
    
    # Verify
    assert output.success is True
    assert len(output.result["sources"]) == 1
    
    # Verify API was called correctly
    mock_tavily.search.assert_called_once_with(
        query="test query",
        max_results=10
    )
```

---

### Test Coverage

**Target: 80%+ coverage**
```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View in browser
open htmlcov/index.html

# Check specific thresholds
pytest tests/ --cov=src --cov-fail-under=80
```

**Coverage report example:**
```
Name                                 Stmts   Miss  Cover
--------------------------------------------------------
src/__init__.py                          0      0   100%
src/schemas/brief.py                    45      2    96%
src/schemas/plan.py                     38      1    97%
src/meta_agent/controller.py           120     15    88%
src/meta_agent/planner.py               95      8    92%
src/workers/research/web_search.py      55      5    91%
--------------------------------------------------------
TOTAL                                 1850    145    92%
```

---

## 🐛 Debugging Guide

### Common Debugging Scenarios

#### 1. Workflow Not Completing

**Symptom**: Workflow hangs or never reaches COMPLETED

**Debug Steps:**
```python
# Add debug logging to state transitions
# src/meta_agent/state_manager.py

def transition_phase(state, new_phase):
    logger.debug(
        f"Phase transition: {state.current_phase} → {new_phase}",
        extra={
            "execution_id": state.execution_id,
            "iteration": state.iteration_count
        }
    )
    # ... rest of code
```

**Check:**
- Are all workers completing?
- Is Supervisor making a decision?
- Is max iterations being hit?

**Breakpoint locations:**
```python
# Set breakpoints at key decision points

# Controller.execute() - main workflow
breakpoint()  # After each phase

# Supervisor.evaluate() - quality decision
if quality_score < threshold:
    breakpoint()  # Check why quality is low

# Orchestrator.execute_step() - worker execution
if not output.success:
    breakpoint()  # Check why worker failed
```

#### 2. Worker Failing

**Symptom**: Worker returns success=False

**Debug Steps:**
```python
# Add detailed error logging in worker
# src/workers/base_worker.py

def execute(self, input_data: WorkerInput) -> WorkerOutput:
    try:
        result = self._do_work(input_data)
        return WorkerOutput(success=True, result=result, ...)
    except Exception as e:
        logger.error(
            f"Worker {self.worker_id} failed",
            extra={
                "task_id": input_data.task_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "input_context": input_data.context
            },
            exc_info=True  # Include stack trace
        )
        return WorkerOutput(success=False, error=str(e), ...)
```

**Check:**
- API key configured?
- API rate limit exceeded?
- Network connection working?
- Input data valid?

**Test worker in isolation:**
```python
# Create a test script
# scripts/test_worker.py

from src.workers.research.web_search import WebSearchWorker
from src.schemas.worker import WorkerInput

worker = WebSearchWorker()
input_data = WorkerInput(
    task_id="debug_001",
    worker_id="web_search",
    context={"query": "test", "max_results": 5}
)

print(f"Testing {worker.worker_id}...")
output = worker.execute(input_data)
print(f"Success: {output.success}")
if not output.success:
    print(f"Error: {output.error}")
else:
    print(f"Result: {output.result}")
```

#### 3. Low Quality Scores

**Symptom**: Quality always below threshold, infinite iterations

**Debug Steps:**
```python
# Add detailed quality logging
# src/meta_agent/supervisor.py

def evaluate(self, state: AgentState) -> Dict:
    # Calculate individual scores
    article_quality = self._calculate_article_quality(state)
    source_quality = self._calculate_source_quality(state)
    factual_quality = self._calculate_factual_quality(state)
    writing_quality = self._calculate_writing_quality(state)
    
    # Log each component
    logger.info(
        "Quality breakdown",
        extra={
            "article": article_quality,
            "sources": source_quality,
            "factual": factual_quality,
            "writing": writing_quality,
            "threshold": state.brief.min_quality_score
        }
    )
    
    # Which component is failing?
    if article_quality < 0.70:
        logger.warning("Article quality is low - incomplete coverage?")
    if source_quality < 0.70:
        logger.warning("Source quality is low - not enough sources?")
    # ... etc
```

**Check:**
- Are there enough sources?
- Is the article complete?
- Are fact-checks passing?
- Is threshold too high?

#### 4. Memory Leaks

**Symptom**: Memory usage grows over time

**Debug with memory profiler:**
```bash
pip install memory-profiler

# Add decorator to suspected functions
from memory_profiler import profile

@profile
def execute_workflow(brief):
    # ... code
```

**Check:**
- Are large objects being kept in memory?
- Are we properly cleaning up after workers?
- Are there circular references?

**Best practices:**
```python
# Clear results after processing
state.research_results.clear()  # If no longer needed

# Use generators for large data
def process_sources(sources):
    for source in sources:  # Don't load all at once
        yield process(source)

# Explicitly delete large objects
del large_data_structure
```

---

### Debugging Tools

**1. Print Debugging (Quick & Simple)**
```python
# Temporary debug prints
print(f"DEBUG: State phase = {state.current_phase}")
print(f"DEBUG: Quality score = {quality_score}")
print(f"DEBUG: Worker output = {output.result}")

# Remove before commit!
```

**2. Logging (Production-Ready)**
```python
# Proper logging
logger.debug(f"State phase = {state.current_phase}")
logger.info(f"Quality score = {quality_score}")
logger.warning(f"Worker returned unexpected result")
```

**3. Python Debugger (pdb)**
```python
# Set breakpoint
import pdb; pdb.set_trace()

# Or use built-in breakpoint (Python 3.7+)
breakpoint()

# When breakpoint hits:
# n - next line
# s - step into function
# c - continue execution
# p variable_name - print variable
# pp variable_name - pretty print
# l - show code around current line
# h - help
```

**4. VS Code Debugger (GUI)**
```
F5 - Start debugging
F9 - Toggle breakpoint
F10 - Step over
F11 - Step into
Shift+F11 - Step out
F5 - Continue
```

**5. IPython for Interactive Debugging**
```python
# Install
pip install ipython

# Use in code
from IPython import embed
embed()  # Opens interactive shell at this point

# Now you can:
# - Inspect variables
# - Call functions
# - Test code snippets
```

---

## 🔧 Common Tasks

### Task 1: Run a Simple Article Generation
```bash
# Using example script
python examples/simple_article.py

# Or directly in Python
python -c "
from src.schemas.brief import Brief, ContentType
from src.meta_agent.controller import Controller

brief = Brief(
    topic='Python programming basics',
    content_type=ContentType.ARTICLE,
    target_length=1000
)

controller = Controller()
output = controller.execute(brief)

print(f'Title: {output.article.title}')
print(f'Words: {output.article.word_count}')
print(f'Quality: {output.quality.overall}')
"
```

### Task 2: Test a Single Worker
```python
# scripts/test_single_worker.py

from src.workers.research.web_search import WebSearchWorker
from src.schemas.worker import WorkerInput

def test_worker():
    # Create worker
    worker = WebSearchWorker()
    
    # Create input
    input_data = WorkerInput(
        task_id="test_001",
        worker_id="web_search",
        context={
            "query": "Python programming",
            "max_results": 5
        }
    )
    
    # Execute
    print("Executing worker...")
    output = worker.execute(input_data)
    
    # Display results
    print(f"\nSuccess: {output.success}")
    print(f"Cost: ${output.cost}")
    print(f"Time: {output.execution_time_seconds}s")
    
    if output.success:
        print(f"Sources found: {len(output.result['sources'])}")
        for i, source in enumerate(output.result['sources'], 1):
            print(f"{i}. {source['title']}")
    else:
        print(f"Error: {output.error}")

if __name__ == "__main__":
    test_worker()
```
```bash
python scripts/test_single_worker.py
```

### Task 3: Format All Code
```bash
# Format with Black
black src/ tests/ examples/

# Sort imports
isort src/ tests/ examples/

# Run both
black src/ tests/ && isort src/ tests/
```

### Task 4: Run Linting
```bash
# Check with flake8
flake8 src/ tests/

# Check types with mypy
mypy src/

# Run all checks
flake8 src/ && mypy src/ && echo "✓ All checks passed"
```

### Task 5: Generate Documentation
```bash
# Generate API documentation
pdoc --html --output-dir docs/api src/

# View in browser
open docs/api/src/index.html
```

### Task 6: Profile Performance
```python
# scripts/profile_workflow.py

import cProfile
import pstats
from src.schemas.brief import Brief, ContentType
from src.meta_agent.controller import Controller

def run_workflow():
    brief = Brief(
        topic="AI trends",
        content_type=ContentType.ARTICLE,
        target_length=2000
    )
    controller = Controller()
    return controller.execute(brief)

# Profile
profiler = cProfile.Profile()
profiler.enable()

output = run_workflow()

profiler.disable()

# Print stats
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```
```bash
python scripts/profile_workflow.py
```

### Task 7: Check Test Coverage
```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=src --cov-report=html

# View report
open htmlcov/index.html

# Check coverage threshold
pytest tests/ --cov=src --cov-fail-under=80
```

### Task 8: Create Migration

**When schemas change:**
```python
# scripts/create_migration.py

"""
Create database migration for schema changes.

Usage:
    python scripts/create_migration.py "add_feedback_table"
"""

import sys
from datetime import datetime

def create_migration(name: str):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"migrations/{timestamp}_{name}.py"
    
    template = f'''"""
Migration: {name}
Created: {datetime.now().isoformat()}
"""

def upgrade():
    """Apply migration."""
    # TODO: Add upgrade logic
    pass

def downgrade():
    """Revert migration."""
    # TODO: Add downgrade logic
    pass
'''
    
    with open(filename, 'w') as f:
        f.write(template)
    
    print(f"Created migration: {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_migration.py <name>")
        sys.exit(1)
    
    create_migration(sys.argv[1])
```

---

## ❗ Troubleshooting

### Issue 1: Import Errors

**Problem:**
```
ImportError: No module named 'src'
```

**Solution:**
```bash
# Option 1: Install package in editable mode
pip install -e .

# Option 2: Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Option 3: Use absolute imports
from src.schemas.brief import Brief  # Not: from schemas.brief
```

### Issue 2: API Key Not Found

**Problem:**
```
Error: ANTHROPIC_API_KEY not set
```

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Check .env content
cat .env | grep ANTHROPIC_API_KEY

# Load .env manually
export $(cat .env | xargs)

# Or in Python
from dotenv import load_dotenv
load_dotenv()  # Call at start of script
```

### Issue 3: Tests Failing

**Problem:**
```
pytest: command not found
```

**Solution:**
```bash
# Ensure dev dependencies installed
pip install -r requirements-dev.txt

# Or install pytest directly
pip install pytest pytest-cov

# Verify installation
pytest --version
```

### Issue 4: Docker Issues

**Problem:**
```
Cannot connect to Docker daemon
```

**Solution:**
```bash
# Start Docker
sudo systemctl start docker  # Linux
# Or start Docker Desktop app on Mac/Windows

# Verify Docker running
docker ps

# Check Docker version
docker --version
```

### Issue 5: Memory Issues

**Problem:**
```
MemoryError: Unable to allocate array
```

**Solution:**
```python
# Process in smaller batches
def process_large_dataset(data):
    batch_size = 100
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        process_batch(batch)  # Process smaller chunks

# Use generators
def load_data():
    for item in items:  # Don't load all at once
        yield process(item)

# Clear memory explicitly
import gc
gc.collect()  # Force garbage collection
```

### Issue 6: Slow Tests

**Problem:**
```
Tests taking too long (>5 minutes)
```

**Solution:**
```bash
# Run only fast tests
pytest tests/unit/ -v

# Skip slow tests
pytest tests/ -v -m "not slow"

# Run tests in parallel
pip install pytest-xdist
pytest tests/ -n auto  # Use all CPU cores

# Cache results
pytest tests/ --cache-clear  # Clear first
pytest tests/  # Subsequent runs faster
```

---

## 📚 Additional Resources

### Documentation

- **Architecture**: [02_ARCHITECTURE.md](./02_ARCHITECTURE.md)
- **Data Models**: [03_DATA_MODELS.md](./03_DATA_MODELS.md)
- **Agents**: [04_AGENTS.md](./04_AGENTS.md)
- **Workers**: [05_WORKERS.md](./05_WORKERS.md)
- **Workflow**: [06_WORKFLOW.md](./06_WORKFLOW.md)

### External Resources

**Python Best Practices:**
- PEP 8: https://pep8.org/
- Google Python Style Guide: https://google.github.io/styleguide/pyguide.html
- Real Python Tutorials: https://realpython.com/

**Testing:**
- Pytest Documentation: https://docs.pytest.org/
- Test-Driven Development: https://www.obeythetestinggoat.com/

**LangChain & LangGraph:**
- LangChain Docs: https://python.langchain.com/docs/
- LangGraph Docs: https://langchain-ai.github.io/langgraph/

**Pydantic:**
- Pydantic Docs: https://docs.pydantic.dev/

---

## ✅ Development Checklist

**Before Starting Work:**
- [ ] Virtual environment activated
- [ ] Dependencies up to date (`pip install -r requirements.txt`)
- [ ] Environment variables configured (`.env`)
- [ ] Tests passing (`pytest tests/`)

**While Developing:**
- [ ] Following coding standards (PEP 8, type hints)
- [ ] Writing docstrings for new functions
- [ ] Adding tests for new code
- [ ] Running tests frequently

**Before Committing:**
- [ ] Code formatted (`black src/ tests/`)
- [ ] Imports sorted (`isort src/ tests/`)
- [ ] Linting passed (`flake8 src/`)
- [ ] Type checking passed (`mypy src/`)
- [ ] All tests passing (`pytest tests/`)
- [ ] No sensitive data (API keys, passwords)
- [ ] Meaningful commit message

**Before Pull Request:**
- [ ] Tests cover new code (>80%)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts
- [ ] CI/CD checks passing

---

## 🔗 Quick Links

**Commands:**
```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt

# Development
black src/ tests/
pytest tests/ -v
python examples/simple_article.py

# Quality
flake8 src/
mypy src/
pytest tests/ --cov=src
```

**File Locations:**
- Schemas: `src/schemas/`
- Agents: `src/meta_agent/`
- Workers: `src/workers/`
- Tests: `tests/`
- Examples: `examples/`

**Key Files:**
- Entry point: `src/meta_agent/controller.py`
- Main workflow: `06_WORKFLOW.md`
- API (Sprint 3): `src/api/main.py`

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2024  
**Target Audience**: Developers

---

END OF DEVELOPMENT GUIDE