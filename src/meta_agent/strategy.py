"""
Strategy Agent - Optimizes execution plan for cost and time.

The Strategy Agent is responsible for:
1. Analyzing execution plans
2. Optimizing parallel vs sequential execution
3. Applying budget and time constraints
4. Balancing cost vs quality trade-offs
5. Providing optimization recommendations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import copy
from typing import List, Dict, Any, Tuple
from datetime import datetime

from src.meta_agent.schemas import (
    Plan,
    PlanStep,
    ExecutionMode,
    AgentState,
)
from config.worker_registry import get_worker_registry


class StrategyAgent:
    """
    Strategy Agent - Optimizes execution strategy.
    
    The Strategy Agent analyzes execution plans and optimizes them
    for cost, time, and quality based on user constraints.
    """
    
    def __init__(self):
        """Initialize strategy agent."""
        self.registry = get_worker_registry()
    
    def optimize_plan(self, state: AgentState, plan: Plan) -> Plan:
        """
        Optimize execution plan.
        
        Args:
            state: Current workflow state
            plan: Plan to optimize
            
        Returns:
            Optimized plan
        """
        print(f"\n{'='*60}")
        print(f"⚙️  Strategy: Optimizing execution plan")
        print(f"{'='*60}")
        
        brief = state.brief
        
        # Get constraints
        max_budget = brief.max_budget or float('inf')
        max_time = brief.max_time_seconds or float('inf')
        
        print(f"📊 Constraints:")
        print(f"   Max budget: ${max_budget:.2f}")
        print(f"   Max time: {max_time}s")
        print(f"\n📈 Original plan:")
        print(f"   Estimated cost: ${plan.estimated_total_cost:.2f}")
        print(f"   Estimated time: {plan.estimated_total_time}s")
        
        # Optimization strategies
        optimized_plan = copy.deepcopy(plan)
        
        # 1. Optimize for parallel execution
        optimized_plan = self._optimize_parallelization(optimized_plan)
        
        # 2. Check budget constraint
        if optimized_plan.estimated_total_cost > max_budget:
            print(f"\n⚠️  Budget exceeded! Optimizing for cost...")
            optimized_plan = self._optimize_for_cost(optimized_plan, max_budget)
        
        # 3. Check time constraint
        if optimized_plan.estimated_total_time > max_time:
            print(f"\n⚠️  Time exceeded! Optimizing for time...")
            optimized_plan = self._optimize_for_time(optimized_plan, max_time)
        
        # 4. Add optimization notes
        optimization_notes = self._generate_optimization_notes(plan, optimized_plan)
        optimized_plan.optimization_notes = optimization_notes
        
        # Log results
        print(f"\n✅ Optimized plan:")
        print(f"   Estimated cost: ${optimized_plan.estimated_total_cost:.2f}")
        print(f"   Estimated time: {optimized_plan.estimated_total_time}s")
        print(f"   Savings: ${plan.estimated_total_cost - optimized_plan.estimated_total_cost:.2f}")
        print(f"   Time saved: {plan.estimated_total_time - optimized_plan.estimated_total_time}s")
        
        if optimized_plan.optimization_notes:
            print(f"\n📝 Optimization notes:")
            print(f"   {optimized_plan.optimization_notes}")
        
        print(f"{'='*60}\n")
        
        return optimized_plan
    
    def _optimize_parallelization(self, plan: Plan) -> Plan:
        """
        Optimize parallel execution where possible.
        
        Args:
            plan: Original plan
            
        Returns:
            Optimized plan
        """
        print(f"\n🔄 Optimizing parallelization...")
        
        # For each step, check if workers can run in parallel
        for step in plan.steps:
            if len(step.worker_ids) > 1:
                # Check if all workers can run in parallel
                can_parallelize = all(
                    self.registry.get_worker(wid).can_run_parallel
                    for wid in step.worker_ids
                )
                
                if can_parallelize and step.execution_mode == ExecutionMode.SEQUENTIAL:
                    print(f"   Converting {step.phase} to parallel execution")
                    step.execution_mode = ExecutionMode.PARALLEL
                    
                    # Recalculate time (max instead of sum)
                    times = [
                        self.registry.get_worker(wid).estimated_time_seconds
                        for wid in step.worker_ids
                    ]
                    step.estimated_time_seconds = max(times) if times else step.estimated_time_seconds
        
        # Recalculate total time
        plan.estimated_total_time = sum(
            step.estimated_time_seconds for step in plan.steps
        )
        
        return plan
    def _optimize_for_cost(self, plan: Plan, max_budget: float) -> Plan:
        """
        Optimize plan to meet budget constraint.
        
        Args:
            plan: Original plan
            max_budget: Maximum budget allowed
            
        Returns:
            Optimized plan
        """
        print(f"   Target budget: ${max_budget:.2f}")
        print(f"   Current cost: ${plan.estimated_total_cost:.2f}")
        
        # Strategy: Remove least essential workers
        # Priority: quality > writing > analysis > research
        
        # Calculate current total cost
        current_cost = sum(step.estimated_cost for step in plan.steps)
        plan.estimated_total_cost = current_cost
        
        # Keep removing workers until within budget
        while plan.estimated_total_cost > max_budget:
            removed = False
            
            # Try to remove from quality phase first
            for step in plan.steps:
                if step.phase == "quality" and len(step.worker_ids) > 1:
                    # Remove one quality worker
                    removed_worker = step.worker_ids.pop()
                    worker_def = self.registry.get_worker(removed_worker)
                    
                    print(f"   Removed worker: {removed_worker}")
                    print(f"   Saved: ${worker_def.estimated_cost:.2f}")
                    
                    # Recalculate step cost
                    step.estimated_cost -= worker_def.estimated_cost
                    
                    # Recalculate total cost
                    current_cost = sum(s.estimated_cost for s in plan.steps)
                    plan.estimated_total_cost = current_cost
                    
                    print(f"   New total cost: ${plan.estimated_total_cost:.2f}")
                    
                    removed = True
                    break  # Exit inner loop to recalculate
            
            # If still over budget and nothing removed, try research phase
            if not removed and plan.estimated_total_cost > max_budget:
                for step in plan.steps:
                    if step.phase == "research" and len(step.worker_ids) > 1:
                        removed_worker = step.worker_ids.pop()
                        worker_def = self.registry.get_worker(removed_worker)
                        
                        print(f"   Removed worker: {removed_worker}")
                        print(f"   Saved: ${worker_def.estimated_cost:.2f}")
                        
                        step.estimated_cost -= worker_def.estimated_cost
                        current_cost = sum(s.estimated_cost for s in plan.steps)
                        plan.estimated_total_cost = current_cost
                        
                        print(f"   New total cost: ${plan.estimated_total_cost:.2f}")
                        
                        removed = True
                        break
            
            # If nothing can be removed, exit to avoid infinite loop
            if not removed:
                print(f"   ⚠️  Cannot reduce cost further")
                break
        
        if plan.estimated_total_cost <= max_budget:
            print(f"   ✅ Within budget!")
        
        return plan
    
    def _optimize_for_time(self, plan: Plan, max_time: int) -> Plan:
        """
        Optimize plan to meet time constraint.
        
        Args:
            plan: Original plan
            max_time: Maximum time allowed (seconds)
            
        Returns:
            Optimized plan
        """
        print(f"   Target time: {max_time}s")
        print(f"   Current time: {plan.estimated_total_time}s")
        
        # Strategy: Enable more parallel execution
        # For Sprint 1, mock optimization
        
        # Try to parallelize more steps
        for step in plan.steps:
            if step.execution_mode == ExecutionMode.SEQUENTIAL:
                # Check if can be parallelized
                if len(step.worker_ids) > 0:
                    workers = [self.registry.get_worker(wid) for wid in step.worker_ids]
                    if all(w.can_run_parallel for w in workers if w):
                        step.execution_mode = ExecutionMode.PARALLEL
                        
                        # Recalculate time
                        times = [w.estimated_time_seconds for w in workers if w]
                        step.estimated_time_seconds = max(times) if times else step.estimated_time_seconds
                        
                        print(f"   Parallelized {step.phase}")
        
        # Recalculate total time
        plan.estimated_total_time = sum(
            step.estimated_time_seconds for step in plan.steps
        )
        
        return plan
    
    def _generate_optimization_notes(self, original: Plan, optimized: Plan) -> str:
        """
        Generate notes about optimizations applied.
        
        Args:
            original: Original plan
            optimized: Optimized plan
            
        Returns:
            Optimization notes
        """
        notes = []
        
        # Cost savings
        cost_saved = original.estimated_total_cost - optimized.estimated_total_cost
        if cost_saved > 0:
            notes.append(f"Reduced cost by ${cost_saved:.2f}")
        
        # Time savings
        time_saved = original.estimated_total_time - optimized.estimated_total_time
        if time_saved > 0:
            notes.append(f"Reduced time by {time_saved}s")
        
        # Parallelization
        original_parallel = original.parallel_steps
        optimized_parallel = optimized.parallel_steps
        if optimized_parallel > original_parallel:
            diff = optimized_parallel - original_parallel
            notes.append(f"Enabled parallel execution for {diff} additional steps")
        
        # Worker changes
        original_workers = sum(len(s.worker_ids) for s in original.steps)
        optimized_workers = sum(len(s.worker_ids) for s in optimized.steps)
        if optimized_workers < original_workers:
            diff = original_workers - optimized_workers
            notes.append(f"Removed {diff} non-essential workers")
        
        if not notes:
            return "Plan already optimal for given constraints"
        
        return "; ".join(notes)
    
    def analyze_plan_efficiency(self, plan: Plan) -> Dict[str, Any]:
        """
        Analyze plan efficiency metrics.
        
        Args:
            plan: Plan to analyze
            
        Returns:
            Efficiency metrics
        """
        print(f"\n📊 Strategy: Analyzing plan efficiency")
        
        # Calculate metrics
        total_workers = sum(len(step.worker_ids) for step in plan.steps)
        parallel_steps = sum(1 for s in plan.steps if s.execution_mode == ExecutionMode.PARALLEL)
        sequential_steps = plan.total_steps - parallel_steps
        
        # Calculate parallelization ratio
        parallelization_ratio = parallel_steps / plan.total_steps if plan.total_steps > 0 else 0
        
        # Calculate cost efficiency (workers per dollar)
        cost_efficiency = total_workers / plan.estimated_total_cost if plan.estimated_total_cost > 0 else 0
        
        # Calculate time efficiency (workers per second)
        time_efficiency = total_workers / plan.estimated_total_time if plan.estimated_total_time > 0 else 0
        
        metrics = {
            "total_steps": plan.total_steps,
            "parallel_steps": parallel_steps,
            "sequential_steps": sequential_steps,
            "total_workers": total_workers,
            "parallelization_ratio": parallelization_ratio,
            "estimated_cost": plan.estimated_total_cost,
            "estimated_time": plan.estimated_total_time,
            "cost_efficiency": cost_efficiency,
            "time_efficiency": time_efficiency,
        }
        
        print(f"   Total steps: {metrics['total_steps']}")
        print(f"   Parallel: {metrics['parallel_steps']}, Sequential: {metrics['sequential_steps']}")
        print(f"   Parallelization ratio: {metrics['parallelization_ratio']:.1%}")
        print(f"   Cost efficiency: {metrics['cost_efficiency']:.2f} workers/$")
        print(f"   Time efficiency: {metrics['time_efficiency']:.3f} workers/s")
        
        return metrics
    
    def recommend_improvements(self, plan: Plan, state: AgentState) -> List[str]:
        """
        Recommend improvements for the plan.
        
        Args:
            plan: Plan to analyze
            state: Current state
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check parallelization
        sequential_count = sum(
            1 for s in plan.steps 
            if s.execution_mode == ExecutionMode.SEQUENTIAL and len(s.worker_ids) > 1
        )
        if sequential_count > 0:
            recommendations.append(
                f"Consider parallelizing {sequential_count} sequential steps with multiple workers"
            )
        
        # Check cost
        brief = state.brief
        if brief.max_budget and plan.estimated_total_cost > brief.max_budget * 0.9:
            recommendations.append(
                "Plan is close to budget limit. Consider removing non-essential quality checks."
            )
        
        # Check time
        if brief.max_time_seconds and plan.estimated_total_time > brief.max_time_seconds * 0.9:
            recommendations.append(
                "Plan is close to time limit. Consider enabling more parallel execution."
            )
        
        # Check worker redundancy
        research_workers = sum(
            len(s.worker_ids) for s in plan.steps if s.phase == "research"
        )
        if research_workers > 3:
            recommendations.append(
                "Multiple research workers may produce redundant results. Consider reducing."
            )
        
        return recommendations


# Global instance
strategy = StrategyAgent()

# Helper functions
def get_strategy() -> StrategyAgent:
    """Get the strategy instance."""
    return strategy


def optimize_plan(state: AgentState, plan: Plan) -> Plan:
    """
    Optimize execution plan.
    
    This is a helper function that calls the instance method.
    
    Args:
        state: Current workflow state
        plan: Plan to optimize
        
    Returns:
        Optimized plan
    """
    return strategy.optimize_plan(state, plan)