"""Test Orchestrator Agent."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meta_agent.orchestrator import OrchestratorAgent, execute_plan
from src.meta_agent.schemas import (
    Brief,
    ContentType,
    AgentState,
    Plan,
    PlanStep,
    ExecutionMode,
    StepStatus,
)


def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    orchestrator = OrchestratorAgent()
    assert orchestrator is not None
    assert orchestrator.registry is not None
    assert orchestrator.execution_count == 0
    print("✅ Orchestrator initialized")


def test_execute_simple_plan():
    """Test executing a simple plan."""
    orchestrator = OrchestratorAgent()
    
    brief = Brief(
        topic="Test Topic",
        content_type=ContentType.ARTICLE,
    )
    
    state = AgentState(brief=brief)
    
    # Create simple plan
    steps = [
        PlanStep(
            step_id="step_1",
            phase="research",
            description="Research",
            worker_ids=["web_search_worker"],
            execution_mode=ExecutionMode.PARALLEL,
            estimated_cost=0.02,
            estimated_time_seconds=15,
        ),
        PlanStep(
            step_id="step_2",
            phase="writing",
            description="Writing",
            worker_ids=["article_writer_worker"],
            execution_mode=ExecutionMode.SEQUENTIAL,
            depends_on=["step_1"],
            estimated_cost=0.08,
            estimated_time_seconds=60,
        )
    ]
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=steps,
        total_steps=2,
        estimated_total_cost=0.10,
        estimated_total_time=75,
    )
    
    # Execute
    updated_state = orchestrator.execute_plan(state, plan)
    
    # Check execution
    assert updated_state is not None
    assert len(updated_state.all_tasks) > 0
    assert len(updated_state.completed_tasks) > 0
    assert updated_state.research_results is not None
    assert updated_state.writing_results is not None
    
    # Check steps marked complete
    assert all(s.status == StepStatus.COMPLETED for s in plan.steps)
    
    print("✅ Simple plan executed")
    print(f"   Tasks: {len(updated_state.all_tasks)}")
    print(f"   Completed: {len(updated_state.completed_tasks)}")
    print(f"   Cost: ${updated_state.total_cost:.2f}")


def test_parallel_execution():
    """Test parallel worker execution."""
    orchestrator = OrchestratorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    step = PlanStep(
        step_id="step_1",
        phase="research",
        description="Research",
        worker_ids=["web_search_worker", "news_search_worker", "academic_search_worker"],
        execution_mode=ExecutionMode.PARALLEL,
        estimated_cost=0.05,
        estimated_time_seconds=20,
    )
    
    # CREATE MOCK PLAN
    plan = Plan(
        plan_id="plan_test",
        brief_id="brief_1",
        steps=[step],
        total_steps=1,
        estimated_total_cost=0.05,
        estimated_total_time=20,
    )
    
    # PASS PLAN to _execute_step
    result = orchestrator._execute_step(state, step, plan)
    
    assert result is not None
    assert result["phase"] == "research"
    assert result["total_workers"] == 3
    assert "all_sources" in result
    
    print("✅ Parallel execution works")
    print(f"   Workers: {result['total_workers']}")
    print(f"   Successful: {result['successful_workers']}")
    print(f"   Sources: {result['total_sources']}")


def test_sequential_execution():
    """Test sequential worker execution."""
    orchestrator = OrchestratorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    step = PlanStep(
        step_id="step_1",
        phase="writing",
        description="Writing",
        worker_ids=["introduction_writer_worker", "article_writer_worker"],
        execution_mode=ExecutionMode.SEQUENTIAL,
        estimated_cost=0.12,
        estimated_time_seconds=90,
    )
    # CREATE MOCK PLAN
    plan = Plan(
        plan_id="plan_test",
        brief_id="brief_1",
        steps=[step],
        total_steps=1,
        estimated_total_cost=0.12,
        estimated_total_time=90,
    )
        
    result = orchestrator._execute_step(state, step, plan)
    
    assert result is not None
    assert result["phase"] == "writing"
    assert result["total_workers"] == 2
    
    print("✅ Sequential execution works")
    print(f"   Workers: {result['total_workers']}")


def test_dependency_checking():
    """Test dependency checking."""
    orchestrator = OrchestratorAgent()
    
    step1 = PlanStep(
        step_id="step_1",
        phase="research",
        description="Research",
        worker_ids=["web_search_worker"],
        execution_mode=ExecutionMode.PARALLEL,
        estimated_cost=0.02,
        estimated_time_seconds=15,
        status=StepStatus.COMPLETED,
    )
    
    step2 = PlanStep(
        step_id="step_2",
        phase="writing",
        description="Writing",
        worker_ids=["article_writer_worker"],
        execution_mode=ExecutionMode.SEQUENTIAL,
        depends_on=["step_1"],
        estimated_cost=0.08,
        estimated_time_seconds=60,
    )
    
    # Should pass (dependency met)
    assert orchestrator._check_dependencies(step2, [step1, step2]) == True
    
    # Should fail (dependency not met)
    step1.status = StepStatus.PENDING
    assert orchestrator._check_dependencies(step2, [step1, step2]) == False
    
    print("✅ Dependency checking works")


def test_result_aggregation():
    """Test result aggregation."""
    orchestrator = OrchestratorAgent()
    
    results = [
        {
            "status": "success",
            "worker_id": "web_search_worker",
            "sources": ["Source 1", "Source 2"],
            "confidence": 0.85,
        },
        {
            "status": "success",
            "worker_id": "news_search_worker",
            "sources": ["Source 3", "Source 4"],
            "confidence": 0.90,
        }
    ]
    
    aggregated = orchestrator._aggregate_results(results, "research")
    
    assert aggregated["phase"] == "research"
    assert aggregated["total_workers"] == 2
    assert aggregated["successful_workers"] == 2
    assert aggregated["total_sources"] == 4
    assert len(aggregated["all_sources"]) == 4
    
    print("✅ Result aggregation works")
    print(f"   Total sources: {aggregated['total_sources']}")


def test_create_task_batch():
    """Test task batch creation."""
    orchestrator = OrchestratorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    worker_ids = ["web_search_worker", "news_search_worker"]
    
    batch = orchestrator.create_task_batch(
        worker_ids,
        "research",
        state,
        "step_1",
        "plan_1"
    )
    
    assert batch is not None
    # Use len(tasks) instead
    assert len(batch.tasks) == 2  # ← CHANGED
    assert all(t.worker_id in worker_ids for t in batch.tasks)
    
    print("✅ Task batch creation works")
    print(f"   Batch ID: {batch.batch_id}")
    print(f"   Tasks: {len(batch.tasks)}")  # ← CHANGED

def test_state_updates():
    """Test state updates with results."""
    orchestrator = OrchestratorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Mock research results
    research_results = {
        "phase": "research",
        "all_sources": ["Source 1", "Source 2"],
        "total_sources": 2,
    }
    
    step = PlanStep(
        step_id="step_1",
        phase="research",
        description="Research",
        worker_ids=["web_search_worker"],
        execution_mode=ExecutionMode.PARALLEL,
        estimated_cost=0.02,
        estimated_time_seconds=15,
    )
    
    updated_state = orchestrator._update_state_with_results(state, step, research_results)
    
    assert updated_state.research_results is not None
    assert updated_state.research_results["total_sources"] == 2
    
    print("✅ State updates work")


def test_helper_function():
    """Test execute_plan helper."""
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Create minimal valid plan with at least 1 step
    step = PlanStep(
        step_id="step_1",
        phase="writing",
        description="Writing",
        worker_ids=["article_writer_worker"],
        execution_mode=ExecutionMode.SEQUENTIAL,
        estimated_cost=0.08,
        estimated_time_seconds=60,
    )
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=[step],  # ← ADD step
        total_steps=1,  # ← Must be >= 1
        estimated_total_cost=0.08,
        estimated_total_time=60,  # ← Must be >= 1
    )
    
    # Use helper function
    updated_state = execute_plan(state, plan)
    
    assert updated_state is not None
    assert len(updated_state.all_tasks) > 0
    
    print("✅ Helper function works")


if __name__ == "__main__":
    test_orchestrator_initialization()
    test_execute_simple_plan()
    test_parallel_execution()
    test_sequential_execution()
    test_dependency_checking()
    test_result_aggregation()
    test_create_task_batch()
    test_state_updates()
    test_helper_function()
    print("\n✅ All Orchestrator tests passed!")