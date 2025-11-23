"""Test all schemas."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meta_agent.schemas import (
    Brief,
    ContentType,
    ToneStyle,
    Plan,
    PlanStep,
    ExecutionMode,
    Task,
    TaskStatus,
    AgentState,
    WorkflowPhase,
    WorkerInput,
    WorkerOutput,
    FinalOutput,
    ArticleResult,
    QualityScore,
    ExecutionMetrics,
)


def test_brief_schema():
    """Test Brief schema."""
    brief = Brief(
        topic="AI trends 2024",
        content_type=ContentType.ARTICLE,
        target_length=2000,
        tone=ToneStyle.PROFESSIONAL,
    )
    
    assert brief.topic == "AI trends 2024"
    assert brief.content_type == "article"
    assert brief.target_length == 2000
    print("✅ Brief schema works")


def test_plan_schema():
    """Test Plan schema."""
    step = PlanStep(
        step_id="step_1",
        phase="research",
        description="Research AI trends",
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
    
    assert len(plan.steps) == 1
    assert plan.get_current_step() == step
    print("✅ Plan schema works")


def test_task_schema():
    """Test Task schema."""
    task = Task(
        task_id="task_1",
        worker_id="web_search_worker",
        step_id="step_1",
        plan_id="plan_1",
        input_data={"query": "AI trends", "max_results": 10},
    )
    
    assert task.status == TaskStatus.PENDING
    assert task.can_retry()
    
    task.mark_started()
    assert task.status == TaskStatus.RUNNING
    
    task.mark_completed(output={"results": []}, cost=0.02)
    assert task.status == TaskStatus.COMPLETED
    print("✅ Task schema works")


def test_state_schema():
    """Test AgentState schema."""
    brief = Brief(
        topic="Test topic",
        content_type=ContentType.ARTICLE,
    )
    
    state = AgentState(brief=brief)
    
    assert state.current_phase == WorkflowPhase.INITIALIZED
    assert state.iteration == 1
    
    state.add_agent_action("Planner", "create_plan", {"steps": 3})
    assert len(state.agent_history) == 1
    
    state.add_cost("web_search_worker", 0.02)
    assert state.total_cost == 0.02
    print("✅ AgentState schema works")


def test_worker_schema():
    """Test Worker schemas."""
    worker_input = WorkerInput(
        task_id="task_1",
        worker_id="web_search_worker",
        data={"query": "AI trends", "max_results": 10},
    )
    
    assert worker_input.task_id == "task_1"
    
    worker_output = WorkerOutput(
        task_id="task_1",
        worker_id="web_search_worker",
        success=True,
        data={"results": []},
        duration_seconds=15.0,
        cost=0.02,
    )
    
    assert worker_output.success is True
    print("✅ Worker schemas work")


def test_result_schema():
    """Test Result schemas."""
    article = ArticleResult(
        title="AI Trends 2024",
        content="Full article content here...",
        word_count=2000,
        reading_time_minutes=10,
    )
    
    quality = QualityScore(
        overall_score=85.0,
        factual_accuracy=90.0,
        completeness=88.0,
    )
    
    metrics = ExecutionMetrics(
        total_duration_seconds=120.0,
        total_cost=0.15,
        total_tasks=5,
        successful_tasks=5,
    )
    
    final_output = FinalOutput(
        request_id="req_1",
        brief_topic="AI trends 2024",
        article=article,
        quality=quality,
        sources=[],
        source_count=0,
        metrics=metrics,
    )
    
    assert final_output.article.word_count == 2000
    assert final_output.quality.overall_score == 85.0
    print("✅ Result schemas work")


if __name__ == "__main__":
    test_brief_schema()
    test_plan_schema()
    test_task_schema()
    test_state_schema()
    test_worker_schema()
    test_result_schema()
    print("\n✅ All schema tests passed!")