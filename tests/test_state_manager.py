"""Test State Manager Agent."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meta_agent.state_manager import StateManagerAgent, initialize_state
from src.meta_agent.schemas import (
    Brief,
    ContentType,
    WorkflowPhase,
    Plan,
    PlanStep,
    ExecutionMode,
)


def test_state_manager_initialization():
    """Test state manager initialization."""
    manager = StateManagerAgent()
    assert manager is not None
    assert manager.current_state is None
    assert len(manager.state_history) == 0
    print("✅ State manager initialized")


def test_initialize_state():
    """Test state initialization."""
    manager = StateManagerAgent()
    
    brief = Brief(
        topic="AI Ethics",
        content_type=ContentType.ARTICLE,
    )
    
    state = manager.initialize_state(brief, max_iterations=3)
    
    assert state is not None
    assert state.brief.topic == "AI Ethics"
    assert state.current_phase == WorkflowPhase.INITIALIZED
    assert state.iteration == 1
    assert state.max_iterations == 3
    assert len(state.agent_history) == 1
    assert len(manager.state_history) == 1  # Snapshot created
    
    print("✅ State initialized correctly")
    print(f"   Topic: {state.brief.topic}")
    print(f"   Phase: {state.current_phase}")
    print(f"   Iteration: {state.iteration}/{state.max_iterations}")


def test_update_phase():
    """Test phase update."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    # Update to planning phase
    state = manager.update_phase(state, WorkflowPhase.PLANNING)
    
    assert state.current_phase == WorkflowPhase.PLANNING
    assert len(state.agent_history) == 2  # Init + update
    assert len(manager.state_history) == 2  # 2 snapshots
    
    print("✅ Phase updated successfully")
    print(f"   New phase: {state.current_phase}")


def test_increment_iteration():
    """Test iteration increment."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    assert state.iteration == 1
    
    state = manager.increment_iteration(state)
    assert state.iteration == 2
    
    state = manager.increment_iteration(state)
    assert state.iteration == 3
    
    print("✅ Iteration incremented")
    print(f"   Current iteration: {state.iteration}")


def test_add_cost():
    """Test cost tracking."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    assert state.total_cost == 0.0
    
    state = manager.add_cost(state, "web_search_worker", 0.02)
    assert state.total_cost == 0.02
    
    state = manager.add_cost(state, "article_writer_worker", 0.08)
    assert state.total_cost == 0.10
    
    assert state.cost_by_worker["web_search_worker"] == 0.02
    assert state.cost_by_worker["article_writer_worker"] == 0.08
    
    print("✅ Cost tracking works")
    print(f"   Total cost: ${state.total_cost:.2f}")


def test_add_error():
    """Test error recording."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    assert len(state.errors) == 0
    
    state = manager.add_error(state, "Test error 1")
    assert len(state.errors) == 1
    
    state = manager.add_error(state, "Test error 2")
    assert len(state.errors) == 2
    
    print("✅ Error recording works")
    print(f"   Errors: {len(state.errors)}")


def test_record_plan():
    """Test plan recording."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    # Create mock plan
    step = PlanStep(
        step_id="step_1",
        phase="research",
        description="Research phase",
        worker_ids=["web_search_worker"],
        execution_mode=ExecutionMode.PARALLEL,
        estimated_cost=0.02,
        estimated_time_seconds=15,
    )
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=[step],
        total_steps=1,
        estimated_total_cost=0.02,
        estimated_total_time=15,
    )
    
    state = manager.record_plan(state, plan)
    
    assert state.plan is not None
    assert state.plan.plan_id == "plan_1"
    assert len(state.previous_plans) == 0  # No previous plans
    
    # Add another plan
    plan2 = Plan(
        plan_id="plan_2",
        brief_id="brief_1",
        steps=[step],
        total_steps=1,
        estimated_total_cost=0.03,
        estimated_total_time=20,
    )
    
    state = manager.record_plan(state, plan2)
    assert state.plan.plan_id == "plan_2"
    assert len(state.previous_plans) == 1  # Previous plan saved
    
    print("✅ Plan recording works")
    print(f"   Current plan: {state.plan.plan_id}")
    print(f"   Previous plans: {len(state.previous_plans)}")


def test_get_state_summary():
    """Test state summary."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    summary = manager.get_state_summary(state)
    
    assert summary["topic"] == "Test"
    assert summary["current_phase"] == WorkflowPhase.INITIALIZED
    assert summary["iteration"] == 1
    assert summary["total_cost"] == 0.0
    
    print("✅ State summary generated")
    print(f"   Keys: {list(summary.keys())}")


def test_can_continue_iteration():
    """Test iteration check."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief, max_iterations=3)
    
    assert manager.can_continue_iteration(state) == True  # 1 < 3
    
    state = manager.increment_iteration(state)
    assert manager.can_continue_iteration(state) == True  # 2 < 3
    
    state = manager.increment_iteration(state)
    assert manager.can_continue_iteration(state) == False  # 3 == 3
    
    print("✅ Iteration check works")


def test_mark_completed():
    """Test marking as completed."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    state = manager.mark_completed(state)
    
    assert state.current_phase == WorkflowPhase.COMPLETED
    assert state.completed_at is not None
    assert state.total_duration_seconds is not None
    
    print("✅ Mark completed works")
    print(f"   Phase: {state.current_phase}")


def test_mark_failed():
    """Test marking as failed."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    state = manager.mark_failed(state, "Test failure")
    
    assert state.current_phase == WorkflowPhase.FAILED
    assert len(state.errors) > 0
    
    print("✅ Mark failed works")
    print(f"   Phase: {state.current_phase}")


def test_state_history():
    """Test state history snapshots."""
    manager = StateManagerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = manager.initialize_state(brief)
    
    assert len(manager.state_history) == 1  # Initial snapshot
    
    state = manager.update_phase(state, WorkflowPhase.PLANNING)
    assert len(manager.state_history) == 2  # After phase update
    
    history = manager.get_state_history()
    assert len(history) == 2
    assert history[0].notes == "State initialized"
    assert history[1].notes == f"Phase: {WorkflowPhase.PLANNING}"
    
    print("✅ State history tracking works")
    print(f"   Snapshots: {len(history)}")


def test_helper_function():
    """Test initialize_state helper."""
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = initialize_state(brief, max_iterations=5)
    
    assert state is not None
    assert state.max_iterations == 5
    
    print("✅ Helper function works")


if __name__ == "__main__":
    test_state_manager_initialization()
    test_initialize_state()
    test_update_phase()
    test_increment_iteration()
    test_add_cost()
    test_add_error()
    test_record_plan()
    test_get_state_summary()
    test_can_continue_iteration()
    test_mark_completed()
    test_mark_failed()
    test_state_history()
    test_helper_function()
    print("\n✅ All State Manager tests passed!")