# Testing Guide - AutoResearch AI

**Last Updated**: November 25, 2024  
**Version**: 1.0  
**Status**: Sprint 1 - Testing Infrastructure Complete

---

## 📋 Table of Contents

1. [Introduction](#introduction)
2. [Testing Philosophy](#testing-philosophy)
3. [Test Types](#test-types)
4. [Test Structure](#test-structure)
5. [Writing Good Tests](#writing-good-tests)
6. [Testing Patterns](#testing-patterns)
7. [Mocking & Fixtures](#mocking--fixtures)
8. [Running Tests](#running-tests)
9. [Coverage & Quality](#coverage--quality)
10. [CI/CD Integration](#cicd-integration)

---

## 🎯 Introduction

### Why Testing Matters

**Without Tests:**
```
Make change → Deploy → User finds bug → Emergency fix → Deploy again
Result: Stress, downtime, unhappy users
```

**With Tests:**
```
Make change → Run tests → Tests fail → Fix locally → Deploy confidently
Result: Confidence, reliability, happy users
```

### Testing Benefits

**1. Catch Bugs Early**
```
Bug found in development: $1 to fix
Bug found in production: $100+ to fix (downtime, users affected)

ROI: 100x cheaper to catch bugs in tests
```

**2. Enable Refactoring**
```
Without tests:
"I want to improve this code but I'm scared I'll break something"

With tests:
"I'll refactor, run tests, and know immediately if I broke anything"
```

**3. Document Behavior**
```
Tests show HOW the system should work:

def test_article_generation():
    brief = Brief(topic="AI", target_length=2000)
    output = generate_article(brief)
    assert output.word_count >= 1900  # Tolerance: ±5%
    assert output.quality >= 0.80
    
This documents expected behavior clearly!
```

**4. Enable Team Confidence**
```
New developer joins:
- Reads code (confusing)
- Reads tests (clear examples)
- Makes changes
- Runs tests (confident it works)
```

---

## 🧠 Testing Philosophy

### Our Testing Principles

**1. Test Behavior, Not Implementation**
```python
# ❌ BAD - Testing implementation details
def test_planner_creates_dict():
    planner = Planner()
    result = planner.create_plan(brief)
    assert isinstance(result, dict)  # Who cares if it's a dict?
    assert "steps" in result          # Implementation detail

# ✅ GOOD - Testing behavior
def test_planner_creates_valid_plan():
    planner = Planner()
    plan = planner.create_plan(brief)
    # Test what the plan DOES, not what it IS
    assert plan.estimated_total_cost <= brief.max_budget
    assert len(plan.steps) >= 3  # At least research, write, quality
```

**Why:** Implementation can change, but behavior shouldn't.

---

**2. Tests Should Be Fast**
```python
# ❌ SLOW - Calls real API
def test_web_search():
    worker = WebSearchWorker()
    result = worker.execute(...)  # 2-5 seconds per test!

# ✅ FAST - Uses mock
@patch('src.workers.research.web_search.tavily_client')
def test_web_search(mock_tavily):
    mock_tavily.search.return_value = {"results": [...]}
    worker = WebSearchWorker()
    result = worker.execute(...)  # < 0.1 seconds
```

**Target:** Unit tests < 0.1s each, entire suite < 60s

---

**3. Tests Should Be Isolated**
```python
# ❌ BAD - Tests depend on each other
def test_step_1():
    global state
    state = create_state()
    state.phase = "PLANNING"

def test_step_2():  # Depends on test_step_1 running first!
    global state
    assert state.phase == "PLANNING"

# ✅ GOOD - Each test is independent
def test_step_1():
    state = create_state()  # Fresh state
    state.phase = "PLANNING"
    assert state.phase == "PLANNING"

def test_step_2():
    state = create_state()  # Fresh state
    state.phase = "EXECUTING"
    assert state.phase == "EXECUTING"
```

**Why:** Tests can run in any order, parallel, or individually.

---

**4. One Assertion Per Concept**
```python
# ❌ BAD - Too many assertions
def test_everything():
    output = generate_article(brief)
    assert output.word_count > 1000
    assert output.quality > 0.8
    assert len(output.sources) > 5
    assert output.article.title
    assert output.status == "completed"
    # If any fails, we don't know which concept broke

# ✅ GOOD - One concept per test
def test_article_meets_length_requirement():
    output = generate_article(brief)
    assert output.word_count >= brief.target_length * 0.95

def test_article_meets_quality_threshold():
    output = generate_article(brief)
    assert output.quality >= brief.min_quality_score

def test_article_has_sufficient_sources():
    output = generate_article(brief)
    assert len(output.sources) >= brief.min_sources
```

**Why:** Clear failure messages, easier debugging.

---

### Testing Pyramid
```
         ┌─────────────────┐
         │   E2E Tests     │  5% (10 tests)
         │   (Slowest)     │  Full workflow, real components
         ├─────────────────┤
         │  Integration    │  25% (50 tests)
         │     Tests       │  Multiple components together
         ├─────────────────┤
         │   Unit Tests    │  70% (140 tests)
         │   (Fastest)     │  Individual functions/classes
         └─────────────────┘

Total: ~200 tests (target for complete system)
```

**Current Status (Sprint 1):**
- Unit Tests: 48 tests ✅
- Integration Tests: 12 tests ✅
- E2E Tests: 3 tests ✅
- **Total: 63 tests**

---

## 🔬 Test Types

### 1. Unit Tests

**What:** Test individual functions/classes in isolation

**When:** Testing single components without dependencies

**Speed:** Very fast (< 0.1s each)

**Example Scenarios:**
- Schema validation
- Helper functions
- Single agent methods
- Worker logic (mocked)

**Example:**
```python
# tests/unit/schemas/test_brief.py

def test_brief_validates_topic_length():
    """Topic must be 1-500 characters."""
    # Valid topic
    brief = Brief(topic="AI trends", content_type=ContentType.ARTICLE)
    assert brief.topic == "AI trends"
    
    # Too short
    with pytest.raises(ValidationError):
        Brief(topic="", content_type=ContentType.ARTICLE)
    
    # Too long
    with pytest.raises(ValidationError):
        Brief(topic="x" * 501, content_type=ContentType.ARTICLE)

def test_brief_validates_length_range():
    """Target length must be 500-10,000 words."""
    # Valid length
    brief = Brief(topic="Valid", target_length=2000)
    assert brief.target_length == 2000
    
    # Too short
    with pytest.raises(ValidationError):
        Brief(topic="Valid", target_length=100)
    
    # Too long
    with pytest.raises(ValidationError):
        Brief(topic="Valid", target_length=15000)
```

**Run:**
```bash
pytest tests/unit/ -v
```

---

### 2. Integration Tests

**What:** Test multiple components working together

**When:** Testing interactions between components

**Speed:** Medium (0.5-2s each)

**Example Scenarios:**
- Agent coordination
- Worker execution via Orchestrator
- State transitions
- Plan creation and optimization

**Example:**
```python
# tests/integration/test_planning_workflow.py

def test_planner_and_strategy_integration():
    """Test Planner creates plan and Strategy optimizes it."""
    # Setup
    brief = Brief(
        topic="AI trends",
        target_length=2000,
        max_budget=3.00,
        max_time=600  # 10 minutes
    )
    state = AgentState(execution_id="test_001", brief=brief)
    
    # Execute Planner
    planner = Planner()
    planner.create_plan(state)
    
    original_cost = state.current_plan.estimated_total_cost
    original_steps = len(state.current_plan.steps)
    
    # Execute Strategy
    strategy = Strategy()
    strategy.optimize_plan(state)
    
    optimized_cost = state.current_plan.estimated_total_cost
    optimized_steps = len(state.current_plan.steps)
    
    # Verify optimization
    assert state.current_plan is not None
    assert optimized_cost <= brief.max_budget  # Within budget
    assert optimized_cost <= original_cost  # Cost reduced or same
    # Strategy might merge or remove steps
    assert optimized_steps <= original_steps

def test_orchestrator_executes_parallel_tasks():
    """Test Orchestrator handles parallel execution correctly."""
    # Setup plan with parallel step
    plan = Plan(steps=[
        PlanStep(
            step_id="step_1",
            workers=["web_search", "academic_search", "news_search"],
            execution_mode=ExecutionMode.PARALLEL
        )
    ])
    state = AgentState(execution_id="test_002", current_plan=plan)
    
    # Execute
    orchestrator = Orchestrator()
    orchestrator.execute_plan(state)
    
    # Verify all workers executed
    assert len(state.all_tasks) == 3
    assert all(task.status == TaskStatus.COMPLETED for task in state.all_tasks)
    
    # Verify results stored
    assert len(state.research_results) == 3
    assert any(r["worker"] == "web_search" for r in state.research_results)
```

**Run:**
```bash
pytest tests/integration/ -v
```

---

### 3. End-to-End Tests

**What:** Test complete workflow from start to finish

**When:** Testing entire system as user would use it

**Speed:** Slow (5-30s each)

**Example Scenarios:**
- Complete article generation
- Workflow with iteration
- Error recovery
- Full quality checks

**Example:**
```python
# tests/integration/test_end_to_end.py

def test_complete_article_generation():
    """Test full workflow: brief → article."""
    # Create brief (user perspective)
    brief = Brief(
        topic="Python programming basics",
        content_type=ContentType.ARTICLE,
        target_length=1000,
        research_depth=ResearchDepth.LIGHT,
        max_budget=2.00
    )
    
    # Execute complete workflow
    controller = Controller()
    output = controller.execute(brief)
    
    # Verify output structure
    assert isinstance(output, FinalOutput)
    assert output.status == "completed"
    
    # Verify article quality
    assert output.article is not None
    assert output.article.word_count >= 950  # ±5% tolerance
    assert output.article.word_count <= 1050
    assert len(output.article.content) > 0
    assert output.article.title is not None
    
    # Verify quality metrics
    assert output.quality.overall >= 0.70  # Decent quality
    assert len(output.sources) >= 3  # Minimum sources
    
    # Verify execution metrics
    assert output.metrics.total_cost <= brief.max_budget
    assert output.metrics.total_duration_seconds < 60  # Quick for light

def test_workflow_with_iteration():
    """Test workflow iterates when quality initially low."""
    # High quality threshold (likely to trigger iteration in mock)
    brief = Brief(
        topic="Complex technical topic",
        min_quality_score=0.90  # High bar
    )
    
    controller = Controller()
    output = controller.execute(brief)
    
    # Should complete (even if iterations needed)
    assert output.status in ["completed", "partial"]
    
    # Check if iteration occurred
    if output.metrics.iteration_count > 1:
        # If iterated, quality should improve
        assert output.quality.overall > 0.70

def test_workflow_handles_worker_failure_gracefully():
    """Test system continues when optional worker fails."""
    brief = Brief(topic="Test topic")
    
    # Mock a worker to fail
    with patch('src.workers.quality.seo_optimizer.SEOOptimizer.execute') as mock:
        mock.return_value = WorkerOutput(
            task_id="test",
            worker_id="seo_optimizer",
            success=False,
            error="Mock failure"
        )
        
        controller = Controller()
        output = controller.execute(brief)
        
        # Should still complete (SEO is optional)
        assert output.status in ["completed", "partial"]
        
        # Should have warning about failed worker
        assert any("seo" in w.lower() for w in output.warnings)
```

**Run:**
```bash
pytest tests/integration/test_end_to_end.py -v
```

---

## 📁 Test Structure

### Directory Organization
```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
│
├── unit/                          # Unit tests (70%)
│   ├── __init__.py
│   │
│   ├── schemas/                   # Schema tests
│   │   ├── test_brief.py
│   │   ├── test_plan.py
│   │   ├── test_task.py
│   │   ├── test_state.py
│   │   ├── test_worker_io.py
│   │   └── test_result.py
│   │
│   ├── meta_agent/                # Agent tests
│   │   ├── test_controller.py
│   │   ├── test_state_manager.py
│   │   ├── test_planner.py
│   │   ├── test_strategy.py
│   │   ├── test_orchestrator.py
│   │   ├── test_supervisor.py
│   │   └── test_merger.py
│   │
│   ├── workers/                   # Worker tests
│   │   ├── test_base_worker.py
│   │   ├── test_registry.py
│   │   ├── research/
│   │   │   ├── test_web_search.py
│   │   │   └── test_academic_search.py
│   │   └── quality/
│   │       └── test_fact_checker.py
│   │
│   └── utils/                     # Utility tests
│       ├── test_logger.py
│       └── test_config.py
│
├── integration/                   # Integration tests (25%)
│   ├── __init__.py
│   ├── test_workflow.py          # Multi-agent workflows
│   ├── test_planning_workflow.py # Plan creation + optimization
│   ├── test_execution_workflow.py # Worker execution
│   └── test_end_to_end.py        # Complete workflows
│
├── fixtures/                      # Test data
│   ├── sample_briefs.json        # Example briefs
│   ├── sample_plans.json         # Example plans
│   ├── sample_outputs.json       # Expected outputs
│   └── mock_api_responses.json   # Mock API data
│
└── performance/                   # Performance tests (optional)
    └── test_benchmarks.py
```

---

### Test File Naming Convention
```
Source file:          src/meta_agent/planner.py
Test file:            tests/unit/meta_agent/test_planner.py

Source file:          src/workers/research/web_search.py
Test file:            tests/unit/workers/research/test_web_search.py

Pattern:              test_<module_name>.py
Function prefix:      test_<what_it_tests>
```

---

## ✍️ Writing Good Tests

### Test Structure: AAA Pattern

**AAA = Arrange, Act, Assert**
```python
def test_planner_creates_plan_within_budget():
    # ARRANGE - Setup test data
    brief = Brief(
        topic="AI trends",
        max_budget=3.00
    )
    state = AgentState(execution_id="test_001", brief=brief)
    planner = Planner()
    
    # ACT - Execute the code being tested
    planner.create_plan(state)
    
    # ASSERT - Verify the results
    assert state.current_plan is not None
    assert state.current_plan.estimated_total_cost <= 3.00
```

---

### Good Test Names

**Pattern:** `test_<what>_<condition>_<expected_result>`
```python
# ✅ GOOD - Clear what's being tested
def test_brief_with_invalid_length_raises_validation_error():
    pass

def test_planner_creates_at_least_three_steps():
    pass

def test_supervisor_returns_continue_when_quality_below_threshold():
    pass

# ❌ BAD - Unclear what's being tested
def test_brief():
    pass

def test_plan():
    pass

def test_quality():
    pass
```

---

### Good Test Documentation
```python
def test_workflow_iterates_until_quality_threshold_met():
    """Test workflow re-plans and executes again if quality low.
    
    Given: A brief with high quality threshold (0.90)
    When: First execution produces quality 0.65
    Then: System should re-plan and execute again
    And: Continue until quality >= 0.90 or max iterations
    """
    # Test implementation
```

---

### Testing Edge Cases
```python
def test_brief_validation_edge_cases():
    """Test Brief handles edge cases correctly."""
    
    # Minimum valid values
    brief = Brief(
        topic="A",  # 1 character (minimum)
        target_length=500,  # Minimum length
        max_budget=0.50  # Minimum budget
    )
    assert brief.topic == "A"
    
    # Maximum valid values
    brief = Brief(
        topic="x" * 500,  # 500 characters (maximum)
        target_length=10000,  # Maximum length
        max_budget=50.00  # Maximum budget
    )
    assert len(brief.topic) == 500
    
    # Boundary violations
    with pytest.raises(ValidationError):
        Brief(topic="x" * 501)  # One over max
    
    with pytest.raises(ValidationError):
        Brief(target_length=499)  # One under min
```

---

### Testing Error Handling
```python
def test_worker_handles_api_timeout():
    """Test worker handles timeout gracefully."""
    worker = WebSearchWorker()
    
    # Mock API to raise timeout
    with patch('src.workers.research.web_search.tavily_client') as mock:
        mock.search.side_effect = TimeoutError("API timeout")
        
        # Execute
        output = worker.execute(WorkerInput(
            task_id="test",
            worker_id="web_search",
            context={"query": "test"}
        ))
        
        # Should return failure, not crash
        assert output.success is False
        assert "timeout" in output.error.lower()

def test_orchestrator_retries_failed_worker():
    """Test Orchestrator retries failed workers up to 3 times."""
    # Mock worker to fail twice, then succeed
    mock_outputs = [
        WorkerOutput(success=False, error="Attempt 1 failed"),
        WorkerOutput(success=False, error="Attempt 2 failed"),
        WorkerOutput(success=True, result={"data": "success"})
    ]
    
    with patch.object(WebSearchWorker, 'execute', side_effect=mock_outputs):
        orchestrator = Orchestrator()
        # Execute and verify retry logic
        # ...
        assert final_output.success is True
```

---

## 🎭 Testing Patterns

### Pattern 1: Parameterized Tests

**Test multiple inputs with same logic:**
```python
import pytest

@pytest.mark.parametrize("topic,expected_complexity", [
    ("What is Python?", 0.2),           # Simple
    ("AI in healthcare", 0.6),          # Medium
    ("Quantum computing theory", 0.9),  # Complex
])
def test_planner_assesses_topic_complexity(topic, expected_complexity):
    """Test Planner correctly assesses different topic complexities."""
    brief = Brief(topic=topic, content_type=ContentType.ARTICLE)
    planner = Planner()
    complexity = planner._assess_complexity(brief)
    
    # Allow ±0.1 tolerance
    assert abs(complexity - expected_complexity) <= 0.1

@pytest.mark.parametrize("content_type,min_words,max_words", [
    (ContentType.ARTICLE, 1500, 3000),
    (ContentType.BLOG_POST, 1000, 2000),
    (ContentType.RESEARCH_REPORT, 3000, 5000),
])
def test_planner_respects_content_type_length(content_type, min_words, max_words):
    """Test Planner creates appropriate length plans for content types."""
    brief = Brief(topic="Test", content_type=content_type)
    planner = Planner()
    plan = planner.create_plan(brief)
    
    # Verify plan targets appropriate length range
    assert plan.target_length >= min_words
    assert plan.target_length <= max_words
```

---

### Pattern 2: Fixture-Based Tests

**Reuse common setup:**
```python
# conftest.py
@pytest.fixture
def sample_brief():
    """Provide standard brief for testing."""
    return Brief(
        topic="AI in healthcare",
        content_type=ContentType.ARTICLE,
        target_length=2000,
        max_budget=5.00
    )

@pytest.fixture
def initialized_state(sample_brief):
    """Provide initialized state."""
    return AgentState(
        execution_id="test_001",
        brief=sample_brief,
        current_phase=WorkflowPhase.INITIALIZED
    )

# test_planner.py
def test_planner_uses_brief_requirements(sample_brief, initialized_state):
    """Test Planner incorporates brief requirements."""
    planner = Planner()
    planner.create_plan(initialized_state)
    
    plan = initialized_state.current_plan
    assert plan.estimated_total_cost <= sample_brief.max_budget

def test_strategy_optimizes_plan(sample_brief, initialized_state):
    """Test Strategy optimizes the plan."""
    # Setup
    planner = Planner()
    planner.create_plan(initialized_state)
    original_cost = initialized_state.current_plan.estimated_total_cost
    
    # Optimize
    strategy = Strategy()
    strategy.optimize_plan(initialized_state)
    
    # Verify
    assert initialized_state.current_plan.estimated_total_cost <= original_cost
```

---

### Pattern 3: Mock External Dependencies

**Isolate code from external services:**
```python
from unittest.mock import Mock, patch, MagicMock

def test_web_search_worker_with_mock_api():
    """Test WebSearchWorker with mocked Tavily API."""
    
    # Create mock response
    mock_response = {
        "results": [
            {
                "title": "Test Article",
                "url": "https://example.com",
                "content": "Test content",
                "score": 0.95
            }
        ]
    }
    
    # Mock the API client
    with patch('src.workers.research.web_search.tavily_client') as mock_client:
        mock_client.search.return_value = mock_response
        
        # Execute worker
        worker = WebSearchWorker()
        output = worker.execute(WorkerInput(
            task_id="test",
            worker_id="web_search",
            context={"query": "test query", "max_results": 10}
        ))
        
        # Verify results
        assert output.success is True
        assert len(output.result["sources"]) == 1
        assert output.result["sources"][0]["title"] == "Test Article"
        
        # Verify API called correctly
        mock_client.search.assert_called_once_with(
            query="test query",
            max_results=10
        )

def test_article_writer_with_mock_claude():
    """Test ArticleWriter with mocked Claude API."""
    
    mock_article = """# AI in Healthcare

Artificial intelligence is transforming healthcare..."""
    
    with patch('anthropic.Anthropic') as mock_anthropic:
        # Setup mock
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.return_value.content = [
            MagicMock(text=mock_article)
        ]
        
        # Execute
        worker = ArticleWriterWorker()
        output = worker.execute(WorkerInput(
            task_id="test",
            worker_id="article_writer",
            context={"outline": {...}, "sources": [...]}
        ))
        
        # Verify
        assert output.success is True
        assert "AI in Healthcare" in output.result["content"]
```

---

### Pattern 4: Test Exceptions and Errors
```python
def test_controller_handles_invalid_brief():
    """Test Controller rejects invalid brief."""
    # Brief with invalid data
    with pytest.raises(ValidationError) as exc_info:
        brief = Brief(
            topic="",  # Empty topic (invalid)
            content_type=ContentType.ARTICLE
        )
    
    assert "topic" in str(exc_info.value).lower()

def test_orchestrator_handles_all_workers_failed():
    """Test Orchestrator handles scenario where all workers fail."""
    # Setup plan with critical workers
    plan = Plan(steps=[
        PlanStep(
            step_id="step_1",
            workers=["article_writer"],  # Critical worker
            execution_mode=ExecutionMode.SEQUENTIAL
        )
    ])
    state = AgentState(execution_id="test", current_plan=plan)
    
    # Mock worker to always fail
    with patch('src.workers.writing.article_writer.ArticleWriterWorker.execute') as mock:
        mock.return_value = WorkerOutput(
            task_id="test",
            worker_id="article_writer",
            success=False,
            error="Persistent failure"
        )
        
        orchestrator = Orchestrator()
        
        # Should raise WorkflowError after retries exhausted
        with pytest.raises(WorkflowError) as exc_info:
            orchestrator.execute_plan(state)
        
        assert "article_writer" in str(exc_info.value)
```

---

## 🎪 Mocking & Fixtures

### What to Mock

**✅ Mock external services:**
- API calls (Claude, Tavily, ArXiv, etc.)
- Database connections
- File system operations
- Network requests
- External tools

**❌ Don't mock internal logic:**
- Pydantic models
- State management
- Business logic
- Calculations

---

### Mock Examples

**1. Mock API Response:**
```python
@patch('src.workers.research.web_search.tavily_client')
def test_web_search(mock_tavily):
    mock_tavily.search.return_value = {
        "results": [{"title": "Test", "url": "https://..."}]
    }
    # Test code...
```

**2. Mock Multiple Calls:**
```python
@patch('anthropic.Anthropic')
def test_multiple_api_calls(mock_anthropic):
    # Setup different responses for sequential calls
    mock_anthropic.return_value.messages.create.side_effect = [
        MagicMock(content=[MagicMock(text="Response 1")]),
        MagicMock(content=[MagicMock(text="Response 2")]),
    ]
    # Test code...
```

**3. Mock with Exception:**
```python
@patch('src.workers.research.web_search.tavily_client')
def test_handles_timeout(mock_tavily):
    mock_tavily.search.side_effect = TimeoutError("API timeout")
    # Test error handling...
```

---

### Useful Fixtures
```python
# conftest.py - Shared across all tests

import pytest
from src.schemas.brief import Brief, ContentType
from src.schemas.state import AgentState
from src.schemas.worker import WorkerOutput

@pytest.fixture
def simple_brief():
    """Brief for simple topic."""
    return Brief(
        topic="What is Python?",
        content_type=ContentType.BLOG_POST,
        target_length=1000,
        research_depth=ResearchDepth.LIGHT
    )

@pytest.fixture
def complex_brief():
    """Brief for complex topic."""
    return Brief(
        topic="Quantum computing applications in cryptography",
        content_type=ContentType.RESEARCH_REPORT,
        target_length=4000,
        min_sources=15,
        min_quality_score=0.90
    )

@pytest.fixture
def mock_successful_worker_output():
    """Standard successful worker output."""
    return WorkerOutput(
        task_id="test_001",
        worker_id="test_worker",
        success=True,
        result={"data": "test data"},
        cost=0.02,
        tokens_used=100,
        execution_time_seconds=1.5
    )

@pytest.fixture
def mock_failed_worker_output():
    """Standard failed worker output."""
    return WorkerOutput(
        task_id="test_001",
        worker_id="test_worker",
        success=False,
        error="Test error",
        cost=0.00,
        tokens_used=0,
        execution_time_seconds=0.5
    )

@pytest.fixture
def temp_state_file(tmp_path):
    """Temporary file for state persistence tests."""
    state_file = tmp_path / "test_state.json"
    yield state_file
    # Cleanup happens automatically with tmp_path
```

---

## 🏃 Running Tests

### Basic Commands
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/schemas/test_brief.py

# Run specific test function
pytest tests/unit/schemas/test_brief.py::test_brief_validates_topic

# Run tests matching pattern
pytest -k "brief"  # Runs all tests with "brief" in name

# Run tests in directory
pytest tests/unit/
pytest tests/integration/
```

---

### Advanced Options
```bash
# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run with coverage HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Run tests in parallel (faster)
pip install pytest-xdist
pytest -n auto  # Use all CPU cores

# Run only failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff

# Stop after first failure
pytest -x

# Stop after N failures
pytest --maxfail=3

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Run tests marked as "slow"
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

---

### Test Markers

**Define custom markers in `pytest.ini`:**
```ini
# pytest.ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    api: marks tests that call real APIs (skip in CI)
```

**Use markers in tests:**
```python
import pytest

@pytest.mark.slow
def test_complete_workflow():
    """Full workflow test (slow)."""
    pass

@pytest.mark.integration
def test_agent_coordination():
    """Integration test."""
    pass

@pytest.mark.api
@pytest.mark.skip(reason="Requires API key")
def test_real_api_call():
    """Test with real API (skip in CI)."""
    pass
```

**Run by marker:**
```bash
# Run only integration tests
pytest -m integration

# Run all except slow tests
pytest -m "not slow"

# Run integration OR e2e tests
pytest -m "integration or e2e"

# Run integration AND NOT slow
pytest -m "integration and not slow"
```

---

### Watch Mode (Development)
```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run tests on file change
ptw

# With options
ptw -- -v --cov=src
```

---

## 📊 Coverage & Quality

### Coverage Reports
```bash
# Generate coverage report
pytest --cov=src --cov-report=term

# Sample output:
# Name                                 Stmts   Miss  Cover
# --------------------------------------------------------
# src/schemas/brief.py                    45      2    96%
# src/schemas/plan.py                     38      1    97%
# src/meta_agent/controller.py           120     15    88%
# src/meta_agent/planner.py               95      8    92%
# --------------------------------------------------------
# TOTAL                                 1850    145    92%
```

**Coverage Targets:**
- Overall: **80%+** ✅
- Critical paths: **95%+** ✅
- Utilities: **90%+** ✅

---

### Checking Coverage Thresholds
```bash
# Fail if coverage below 80%
pytest --cov=src --cov-fail-under=80

# Check specific module
pytest --cov=src.meta_agent --cov-fail-under=85
```

---

### HTML Coverage Report
```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html
```

**Report shows:**
- Coverage % per file
- Which lines are covered (green)
- Which lines are missed (red)
- Branch coverage

---

### Coverage Configuration

**`.coveragerc` file:**
```ini
[run]
source = src
omit =
    */tests/*
    */venv/*
    */__init__.py
    */examples/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

**`.github/workflows/test.yml`:**
```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.12]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with flake8
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src/ --count --max-complexity=10 --max-line-length=88 --statistics
    
    - name: Type check with mypy
      run: |
        mypy src/
    
    - name: Run tests with coverage
      run: |
        pytest tests/ --cov=src --cov-report=xml --cov-report=term-missing
    
    - name: Check coverage threshold
      run: |
        pytest tests/ --cov=src --cov-fail-under=80
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

---

### Pre-commit Hooks

**`.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
  
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.12
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=88']
  
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args:
          - tests/unit/
          - --maxfail=1
```

**Install:**
```bash
pip install pre-commit
pre-commit install

# Now tests run automatically before each commit
```

---

## 📚 Testing Best Practices Summary

### Do's ✅

1. **Write tests first** (or immediately after code)
2. **Keep tests fast** (mock external services)
3. **Test behavior, not implementation**
4. **One concept per test**
5. **Use descriptive test names**
6. **Use fixtures for common setup**
7. **Test edge cases and errors**
8. **Run tests frequently** (every save)
9. **Keep tests simple and readable**
10. **Aim for 80%+ coverage**

### Don'ts ❌

1. **Don't skip writing tests** ("I'll add them later" = never)
2. **Don't test implementation details** (test what, not how)
3. **Don't make tests dependent** on each other
4. **Don't use real API calls** in unit tests
5. **Don't write overly complex tests** (tests should be simple)
6. **Don't ignore failing tests** (fix or remove)
7. **Don't commit without running tests**
8. **Don't aim for 100% coverage** (diminishing returns after 85%)
9. **Don't test framework code** (trust pytest, pydantic, etc.)
10. **Don't forget to test error cases**

---

## 🎯 Current Testing Status

### Sprint 1 (Complete) ✅

**Unit Tests:**
- ✅ All schemas (6 files, 24 tests)
- ✅ All meta agents (7 agents, 28 tests)
- ✅ Worker base classes (2 files, 8 tests)
- ✅ Mock workers (5 files, 15 tests)

**Integration Tests:**
- ✅ Planning workflow (4 tests)
- ✅ State transitions (4 tests)
- ✅ Basic orchestration (4 tests)

**E2E Tests:**
- ✅ Simple workflow (1 test)
- ✅ Workflow with mock data (2 tests)

**Total: 63 tests, 85% coverage** ✅

---

### Sprint 2 (Planned) 📋

**New Tests Needed:**
- Real worker tests with API mocks
- Integration tests with actual workflows
- Performance benchmarks
- Error recovery scenarios

**Target: 120 tests, 85%+ coverage**

---

## 🔗 Quick Reference

### Common Commands
```bash
# Development workflow
pytest tests/unit/ -v           # Fast feedback
pytest tests/integration/ -v    # Before commit
pytest                          # Full suite

# Coverage
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Specific tests
pytest -k "planner"            # All planner tests
pytest tests/unit/test_brief.py::test_validation  # One test

# Debug
pytest -s                       # Show prints
pytest -l                       # Show locals on failure
pytest --pdb                    # Drop to debugger on failure

# Performance
pytest -n auto                  # Parallel execution
pytest --durations=10          # Show 10 slowest tests
```

---

### Test Template
```python
def test_<what>_<condition>_<expected>():
    """Test <component> <does what> when <condition>.
    
    Given: <initial state>
    When: <action>
    Then: <expected result>
    """
    # ARRANGE
    # Setup test data
    
    # ACT
    # Execute code being tested
    
    # ASSERT
    # Verify results
```

---

## 📖 Additional Resources

**Pytest Documentation:**
- Official Docs: https://docs.pytest.org/
- Fixtures Guide: https://docs.pytest.org/en/stable/fixture.html
- Parametrize: https://docs.pytest.org/en/stable/parametrize.html

**Testing Best Practices:**
- Python Testing Best Practices: https://realpython.com/pytest-python-testing/
- Test-Driven Development: https://www.obeythetestinggoat.com/
- Google Testing Blog: https://testing.googleblog.com/

**Mocking:**
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- pytest-mock: https://pytest-mock.readthedocs.io/

---

## 🔗 Related Documentation

- **[Development Guide](./09_DEVELOPMENT.md)** - Setup and coding standards
- **[Architecture](./02_ARCHITECTURE.md)** - System design
- **[Workflow](./06_WORKFLOW.md)** - How components interact

---

**Document Version**: 1.0  
**Last Updated**: November 25, 2024  
**Target Audience**: Developers, QA Engineers

---

END OF TESTING GUIDE