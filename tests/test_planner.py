"""Test Planner Agent."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meta_agent.planner import PlannerAgent, create_plan
from src.meta_agent.schemas import (
    Brief,
    ContentType,
    ToneStyle,
    AgentState,
    ExecutionMode,
)


def test_planner_initialization():
    """Test planner initialization."""
    planner = PlannerAgent()
    assert planner is not None
    assert planner.registry is not None
    assert planner.plan_count == 0
    print("✅ Planner initialized")


def test_analyze_brief():
    """Test brief analysis."""
    planner = PlannerAgent()
    
    brief = Brief(
        topic="Artificial Intelligence in Healthcare",
        content_type=ContentType.ARTICLE,
        target_length=2000,
        key_points=["diagnosis", "treatment", "ethics"],
    )
    
    analysis = planner._analyze_brief(brief)
    
    assert analysis is not None
    assert 0 <= analysis.complexity_score <= 1
    assert analysis.estimated_research_depth > 0
    assert len(analysis.required_capabilities) > 0
    
    print("✅ Brief analysis works")
    print(f"   Complexity: {analysis.complexity_score:.2f}")
    print(f"   Research depth: {analysis.estimated_research_depth}")
    print(f"   Multi-hop: {analysis.requires_multi_hop}")


def test_select_workers():
    """Test worker selection."""
    planner = PlannerAgent()
    
    brief = Brief(
        topic="Machine Learning",
        content_type=ContentType.ARTICLE,
        enable_fact_checking=True,
        enable_seo_optimization=True,
    )
    
    analysis = planner._analyze_brief(brief)
    selected = planner._select_workers(brief, analysis)
    
    assert "research" in selected
    assert "writing" in selected
    assert "quality" in selected
    assert len(selected["research"]) > 0
    assert len(selected["writing"]) > 0
    
    print("✅ Worker selection works")
    print(f"   Research workers: {len(selected['research'])}")
    print(f"   Analysis workers: {len(selected['analysis'])}")
    print(f"   Writing workers: {len(selected['writing'])}")
    print(f"   Quality workers: {len(selected['quality'])}")


def test_create_steps():
    """Test step creation."""
    planner = PlannerAgent()
    
    brief = Brief(
        topic="Test",
        content_type=ContentType.ARTICLE,
    )
    
    selected_workers = {
        "research": ["web_search_worker", "news_search_worker"],
        "analysis": ["content_synthesizer_worker"],
        "writing": ["article_writer_worker"],
        "quality": ["fact_checker_worker", "editor_worker"],
    }
    
    steps = planner._create_steps(selected_workers, brief)
    
    assert len(steps) > 0
    assert all(isinstance(step.step_id, str) for step in steps)
    assert all(step.estimated_cost > 0 for step in steps)
    assert all(step.estimated_time_seconds > 0 for step in steps)
    
    # Check dependencies
    for i, step in enumerate(steps[1:], 1):
        if step.depends_on:
            assert steps[i-1].step_id in step.depends_on
    
    print("✅ Step creation works")
    print(f"   Total steps: {len(steps)}")
    for step in steps:
        print(f"   - {step.phase}: {len(step.worker_ids)} workers, {step.execution_mode}")


def test_create_plan_simple():
    """Test plan creation with simple brief."""
    planner = PlannerAgent()
    
    brief = Brief(
        topic="Python Programming Basics",
        content_type=ContentType.ARTICLE,
        target_length=1500,
    )
    
    state = AgentState(brief=brief)
    plan = planner.create_plan(state)
    
    assert plan is not None
    assert plan.plan_id.startswith("plan_")
    assert plan.total_steps > 0
    assert plan.estimated_total_cost > 0
    assert plan.estimated_total_time > 0
    assert len(plan.steps) == plan.total_steps
    
    print("✅ Simple plan created")
    print(f"   Plan ID: {plan.plan_id}")
    print(f"   Steps: {plan.total_steps}")
    print(f"   Cost: ${plan.estimated_total_cost:.2f}")
    print(f"   Time: {plan.estimated_total_time}s")


def test_create_plan_complex():
    """Test plan creation with complex brief."""
    planner = PlannerAgent()
    
    brief = Brief(
        topic="Advanced Machine Learning Techniques in Modern Healthcare Systems",
        content_type=ContentType.RESEARCH_PAPER,
        target_length=5000,
        key_points=[
            "Deep learning applications",
            "Clinical decision support",
            "Privacy and security",
            "Regulatory compliance"
        ],
        enable_fact_checking=True,
        enable_seo_optimization=True,
    )
    
    state = AgentState(brief=brief)
    plan = planner.create_plan(state)
    
    assert plan is not None
    assert plan.total_steps >= 3  # At least research, write, quality
    assert state.brief_analysis is not None
    assert state.brief_analysis.complexity_score > 0.5  # Should be complex
    
    # Check for parallel steps
    parallel_steps = [s for s in plan.steps if s.execution_mode == ExecutionMode.PARALLEL]
    assert len(parallel_steps) > 0  # Should have parallel steps
    
    print("✅ Complex plan created")
    print(f"   Complexity: {state.brief_analysis.complexity_score:.2f}")
    print(f"   Steps: {plan.total_steps}")
    print(f"   Parallel steps: {plan.parallel_steps}")
    print(f"   Cost: ${plan.estimated_total_cost:.2f}")
    print(f"   Time: {plan.estimated_total_time}s")


def test_create_replan():
    """Test re-planning."""
    planner = PlannerAgent()
    
    brief = Brief(
        topic="Test",
        content_type=ContentType.ARTICLE,
    )
    
    state = AgentState(brief=brief)
    
    # Create initial plan
    plan1 = planner.create_plan(state)
    
    # Create revised plan
    feedback = "Need more sources and better fact-checking"
    plan2 = planner.create_replan(state, feedback)
    
    assert plan2 is not None
    assert plan2.plan_id != plan1.plan_id
    assert feedback in (plan2.optimization_notes or "")
    
    print("✅ Re-planning works")
    print(f"   Original plan: {plan1.plan_id}")
    print(f"   Revised plan: {plan2.plan_id}")
    print(f"   Feedback applied: {feedback}")


def test_parallel_vs_sequential():
    """Test parallel vs sequential execution modes."""
    planner = PlannerAgent()
    
    brief = Brief(
        topic="Test",
        content_type=ContentType.ARTICLE,
    )
    
    state = AgentState(brief=brief)
    plan = planner.create_plan(state)
    
    # Research should be parallel
    research_steps = [s for s in plan.steps if s.phase == "research"]
    if research_steps:
        assert research_steps[0].execution_mode == ExecutionMode.PARALLEL
    
    # Analysis should be sequential (depends on research)
    analysis_steps = [s for s in plan.steps if s.phase == "analysis"]
    if analysis_steps:
        assert analysis_steps[0].execution_mode == ExecutionMode.SEQUENTIAL
        assert len(analysis_steps[0].depends_on) > 0
    
    print("✅ Execution modes correct")
    print(f"   Research: parallel")
    print(f"   Analysis: sequential with dependencies")


def test_helper_function():
    """Test create_plan helper."""
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    plan = create_plan(state)
    
    assert plan is not None
    assert plan.total_steps > 0
    
    print("✅ Helper function works")


if __name__ == "__main__":
    test_planner_initialization()
    test_analyze_brief()
    test_select_workers()
    test_create_steps()
    test_create_plan_simple()
    test_create_plan_complex()
    test_create_replan()
    test_parallel_vs_sequential()
    test_helper_function()
    print("\n✅ All Planner tests passed!")