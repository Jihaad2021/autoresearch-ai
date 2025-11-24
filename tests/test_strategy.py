"""Test Strategy Agent."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meta_agent.strategy import StrategyAgent, optimize_plan
from src.meta_agent.schemas import (
    Brief,
    ContentType,
    AgentState,
    Plan,
    PlanStep,
    ExecutionMode,
    StepStatus,
)


def test_strategy_initialization():
    """Test strategy initialization."""
    strategy = StrategyAgent()
    assert strategy is not None
    assert strategy.registry is not None
    print("✅ Strategy initialized")


def test_optimize_parallelization():
    """Test parallelization optimization."""
    strategy = StrategyAgent()
    
    # Create plan with sequential steps that can be parallelized
    step = PlanStep(
        step_id="step_1",
        phase="research",
        description="Research",
        worker_ids=["web_search_worker", "news_search_worker"],
        execution_mode=ExecutionMode.SEQUENTIAL,  # Not optimal!
        estimated_cost=0.03,
        estimated_time_seconds=30,  # 15 + 15 (sequential)
    )
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=[step],
        total_steps=1,
        estimated_total_cost=0.03,
        estimated_total_time=30,
    )
    
    # Optimize
    optimized = strategy._optimize_parallelization(plan)
    
    # Should be parallel now
    assert optimized.steps[0].execution_mode == ExecutionMode.PARALLEL
    # Time should be max(15, 15) = 15, not 30
    assert optimized.steps[0].estimated_time_seconds == 15
    
    print("✅ Parallelization optimization works")
    print(f"   Original time: 30s → Optimized time: {optimized.steps[0].estimated_time_seconds}s")


def test_optimize_for_cost():
    """Test cost optimization."""
    strategy = StrategyAgent()
    
    # Create plan that exceeds budget
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
            phase="quality",
            description="Quality",
            worker_ids=["fact_checker_worker", "editor_worker", "seo_optimizer_worker"],
            execution_mode=ExecutionMode.PARALLEL,
            estimated_cost=0.12,  # 0.05 + 0.04 + 0.03
            estimated_time_seconds=50,
        )
    ]
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=steps,
        total_steps=2,
        estimated_total_cost=0.14,
        estimated_total_time=65,
    )
    
    # Optimize with budget constraint
    max_budget = 0.10
    optimized = strategy._optimize_for_cost(plan, max_budget)
    
    # Should have removed workers
    assert optimized.estimated_total_cost <= max_budget
    quality_step = [s for s in optimized.steps if s.phase == "quality"][0]
    assert len(quality_step.worker_ids) < 3
    
    print("✅ Cost optimization works")
    print(f"   Original cost: $0.14 → Optimized cost: ${optimized.estimated_total_cost:.2f}")
    print(f"   Budget: ${max_budget:.2f}")


def test_optimize_for_time():
    """Test time optimization."""
    strategy = StrategyAgent()
    
    # Create plan with sequential execution
    step = PlanStep(
        step_id="step_1",
        phase="research",
        description="Research",
        worker_ids=["web_search_worker", "news_search_worker"],
        execution_mode=ExecutionMode.SEQUENTIAL,
        estimated_cost=0.03,
        estimated_time_seconds=30,
    )
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=[step],
        total_steps=1,
        estimated_total_cost=0.03,
        estimated_total_time=30,
    )
    
    # Optimize with time constraint
    max_time = 20
    optimized = strategy._optimize_for_time(plan, max_time)
    
    # Should be faster
    assert optimized.estimated_total_time <= max_time
    
    print("✅ Time optimization works")
    print(f"   Original time: 30s → Optimized time: {optimized.estimated_total_time}s")
    print(f"   Time limit: {max_time}s")

def test_full_optimization():
    """Test full plan optimization."""
    strategy = StrategyAgent()
    
    brief = Brief(
        topic="Test",
        content_type=ContentType.ARTICLE,
        max_budget=0.15,
        max_time_seconds=150,
    )
    
    state = AgentState(brief=brief)
    
    # Create unoptimized plan
    steps = [
        PlanStep(
            step_id="step_1",
            phase="research",
            description="Research",
            worker_ids=["web_search_worker", "news_search_worker"],
            execution_mode=ExecutionMode.SEQUENTIAL,
            estimated_cost=0.03,
            estimated_time_seconds=30,
        ),
        PlanStep(
            step_id="step_2",
            phase="writing",
            description="Writing",
            worker_ids=["article_writer_worker"],
            execution_mode=ExecutionMode.SEQUENTIAL,
            estimated_cost=0.08,
            estimated_time_seconds=60,
        ),
        PlanStep(
            step_id="step_3",
            phase="quality",
            description="Quality",
            worker_ids=["fact_checker_worker", "editor_worker"],
            execution_mode=ExecutionMode.SEQUENTIAL,
            estimated_cost=0.09,
            estimated_time_seconds=90,
        )
    ]
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=steps,
        total_steps=3,
        estimated_total_cost=0.20,
        estimated_total_time=180,
    )
    
    # DEBUG: Print before optimization
    print(f"\n🔍 DEBUG - Before optimization:")
    print(f"   plan.estimated_total_cost = ${plan.estimated_total_cost:.2f}")
    print(f"   plan ID: {id(plan)}")
    
    # Optimize
    optimized = strategy.optimize_plan(state, plan)
    
    # DEBUG: Print after optimization
    print(f"\n🔍 DEBUG - After optimization:")
    print(f"   plan.estimated_total_cost = ${plan.estimated_total_cost:.2f}")
    print(f"   optimized.estimated_total_cost = ${optimized.estimated_total_cost:.2f}")
    print(f"   plan ID: {id(plan)}")
    print(f"   optimized ID: {id(optimized)}")
    print(f"   Same object? {plan is optimized}")
    
    # Check optimizations were attempted
    assert optimized is not None
    assert optimized.optimization_notes is not None
    
    # Check that cost was reduced (or stayed same if already optimal)
    print(f"\n🔍 Checking: ${optimized.estimated_total_cost:.2f} <= ${plan.estimated_total_cost:.2f}")
    assert optimized.estimated_total_cost <= plan.estimated_total_cost, \
        f"Optimized cost ${optimized.estimated_total_cost:.2f} should be <= original ${plan.estimated_total_cost:.2f}"
    
    # Check that time was reduced (or stayed same)
    assert optimized.estimated_total_time <= plan.estimated_total_time
    
    print("✅ Full optimization works")
    print(f"   Original: ${plan.estimated_total_cost:.2f}, {plan.estimated_total_time}s")
    print(f"   Optimized: ${optimized.estimated_total_cost:.2f}, {optimized.estimated_total_time}s")
    print(f"   Constraints: ${brief.max_budget:.2f}, {brief.max_time_seconds}s")

def test_impossible_constraints():
    """Test optimization with impossible constraints."""
    strategy = StrategyAgent()
    
    brief = Brief(
        topic="Test",
        content_type=ContentType.ARTICLE,
        max_budget=0.01,  # Impossible budget!
        max_time_seconds=60,  # Minimum allowed time (validation)
    )
    
    state = AgentState(brief=brief)
    
    # Create minimal plan
    steps = [
        PlanStep(
            step_id="step_1",
            phase="writing",
            description="Writing",
            worker_ids=["article_writer_worker"],
            execution_mode=ExecutionMode.SEQUENTIAL,
            estimated_cost=0.08,
            estimated_time_seconds=60,
        )
    ]
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=steps,
        total_steps=1,
        estimated_total_cost=0.08,
        estimated_total_time=60,
    )
    
    # Optimize
    optimized = strategy.optimize_plan(state, plan)
    
    # Cannot meet impossible constraints, but should try
    assert optimized is not None
    print("✅ Handles impossible constraints gracefully")
    print(f"   Requested budget: ${brief.max_budget:.2f}, Achieved: ${optimized.estimated_total_cost:.2f}")
    print(f"   Requested time: {brief.max_time_seconds}s, Achieved: {optimized.estimated_total_time}s")
    print(f"   Note: Budget constraint impossible with minimum viable plan")

def test_analyze_plan_efficiency():
    """Test plan efficiency analysis."""
    strategy = StrategyAgent()
    
    steps = [
        PlanStep(
            step_id="step_1",
            phase="research",
            description="Research",
            worker_ids=["web_search_worker", "news_search_worker"],
            execution_mode=ExecutionMode.PARALLEL,
            estimated_cost=0.03,
            estimated_time_seconds=15,
        ),
        PlanStep(
            step_id="step_2",
            phase="writing",
            description="Writing",
            worker_ids=["article_writer_worker"],
            execution_mode=ExecutionMode.SEQUENTIAL,
            estimated_cost=0.08,
            estimated_time_seconds=60,
        )
    ]
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=steps,
        total_steps=2,
        parallel_steps=1,
        estimated_total_cost=0.11,
        estimated_total_time=75,
    )
    
    metrics = strategy.analyze_plan_efficiency(plan)
    
    assert "total_steps" in metrics
    assert "parallelization_ratio" in metrics
    assert "cost_efficiency" in metrics
    assert "time_efficiency" in metrics
    assert metrics["total_steps"] == 2
    assert metrics["parallel_steps"] == 1
    
    print("✅ Efficiency analysis works")
    print(f"   Parallelization ratio: {metrics['parallelization_ratio']:.1%}")
    print(f"   Cost efficiency: {metrics['cost_efficiency']:.2f}")


def test_recommend_improvements():
    """Test improvement recommendations."""
    strategy = StrategyAgent()
    
    brief = Brief(
        topic="Test",
        content_type=ContentType.ARTICLE,
        max_budget=0.20,
        max_time_seconds=200,
    )
    
    state = AgentState(brief=brief)
    
    # Create plan with issues
    steps = [
        PlanStep(
            step_id="step_1",
            phase="research",
            description="Research",
            worker_ids=["web_search_worker", "news_search_worker"],
            execution_mode=ExecutionMode.SEQUENTIAL,  # Can be parallel!
            estimated_cost=0.03,
            estimated_time_seconds=30,
        )
    ]
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=steps,
        total_steps=1,
        estimated_total_cost=0.03,
        estimated_total_time=30,
    )
    
    recommendations = strategy.recommend_improvements(plan, state)
    
    assert len(recommendations) > 0
    assert any("parallel" in r.lower() for r in recommendations)
    
    print("✅ Recommendations work")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")


def test_optimization_notes():
    """Test optimization notes generation."""
    strategy = StrategyAgent()
    
    # Original plan
    original = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=[],
        total_steps=1,
        parallel_steps=0,
        estimated_total_cost=0.20,
        estimated_total_time=100,
    )
    
    # Optimized plan
    optimized = Plan(
        plan_id="plan_2",
        brief_id="brief_1",
        steps=[],
        total_steps=1,
        parallel_steps=1,
        estimated_total_cost=0.15,
        estimated_total_time=80,
    )
    
    notes = strategy._generate_optimization_notes(original, optimized)
    
    assert notes is not None
    assert "0.05" in notes  # Cost saved
    assert "20" in notes    # Time saved
    
    print("✅ Optimization notes work")
    print(f"   Notes: {notes}")


def test_helper_function():
    """Test optimize_plan helper."""
    brief = Brief(
        topic="Test",
        content_type=ContentType.ARTICLE,
        max_budget=0.10,
    )
    
    state = AgentState(brief=brief)
    
    # Create valid minimal plan with at least 1 step
    step = PlanStep(
        step_id="step_1",
        phase="writing",
        description="Writing",
        worker_ids=["article_writer_worker"],
        execution_mode=ExecutionMode.SEQUENTIAL,
        estimated_cost=0.05,
        estimated_time_seconds=50,
    )
    
    plan = Plan(
        plan_id="plan_1",
        brief_id="brief_1",
        steps=[step],
        total_steps=1,
        estimated_total_cost=0.05,
        estimated_total_time=50,
    )
    
    optimized = optimize_plan(state, plan)
    
    assert optimized is not None
    assert optimized.estimated_total_cost <= brief.max_budget
    
    print("✅ Helper function works")


if __name__ == "__main__":
    test_strategy_initialization()
    test_optimize_parallelization()
    test_optimize_for_cost()
    test_optimize_for_time()
    test_full_optimization()
    test_impossible_constraints()
    test_analyze_plan_efficiency()
    test_recommend_improvements()
    test_optimization_notes()
    test_helper_function()
    print("\n✅ All Strategy tests passed!")