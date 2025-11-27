"""
Planner Agent - Analyzes brief and creates execution plan.

The Planner is responsible for:
1. Analyzing the user's brief
2. Determining complexity and requirements
3. Selecting appropriate workers from the registry
4. Creating a step-by-step execution plan
5. Defining dependencies between steps
6. Estimating total cost and time
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from src.meta_agent.schemas import (
    Brief,
    BriefAnalysis,
    Plan,
    PlanStep,
    ExecutionMode,
    StepStatus,
    AgentState,
)
from config.worker_registry import get_worker_registry


class PlannerAgent:
    """
    Planner Agent - Creates execution plans.
    
    The Planner analyzes the user's brief and creates a detailed
    execution plan by selecting appropriate workers and organizing
    them into steps.
    """
    
    def __init__(self):
        """Initialize planner."""
        self.registry = get_worker_registry()
        self.plan_count = 0
    
    def create_plan(self, state: AgentState) -> Plan:
        """
        Create execution plan from brief.
        
        Args:
            state: Current workflow state
            
        Returns:
            Execution plan
        """
        print(f"\n{'='*60}")
        print(f"📝 Planner: Creating execution plan")
        print(f"{'='*60}")
        
        brief = state.brief
        
        # Step 1: Analyze brief
        analysis = self._analyze_brief(brief)
        
        # Step 2: Select workers
        selected_workers = self._select_workers(brief, analysis)
        
        # Step 3: Create steps
        steps = self._create_steps(selected_workers, brief)
        
        # Step 4: Calculate estimates
        total_cost = sum(step.estimated_cost for step in steps)
        total_time = sum(step.estimated_time_seconds for step in steps)
        
        # Step 5: Create plan
        plan = Plan(
            plan_id=self._generate_plan_id(),
            brief_id=brief.request_id or "unknown",
            steps=steps,
            total_steps=len(steps),
            parallel_steps=sum(1 for s in steps if s.execution_mode == ExecutionMode.PARALLEL),
            estimated_total_cost=total_cost,
            estimated_total_time=total_time,
        )
        
        # Record analysis in state
        state.brief_analysis = analysis
        
        # Log plan
        print(f"\n📋 Plan created successfully")
        print(f"   Plan ID: {plan.plan_id}")
        print(f"   Total steps: {plan.total_steps}")
        print(f"   Parallel steps: {plan.parallel_steps}")
        print(f"   Estimated cost: ${plan.estimated_total_cost:.2f}")
        print(f"   Estimated time: {plan.estimated_total_time}s")
        print(f"\n   Steps:")
        for i, step in enumerate(steps, 1):
            mode = "⚡" if step.execution_mode == ExecutionMode.PARALLEL else "→"
            print(f"   {i}. {mode} {step.phase}: {len(step.worker_ids)} workers")
        
        print(f"{'='*60}\n")
        
        return plan
    
    def create_replan(
        self,
        state: AgentState,
        feedback: str
    ) -> Plan:
        """
        Create a revised plan based on supervisor feedback.
        
        Args:
            state: Current workflow state
            feedback: Feedback from supervisor
            
        Returns:
            Revised execution plan
        """
        print(f"\n{'='*60}")
        print(f"🔄 Planner: Creating revised plan")
        print(f"   Feedback: {feedback}")
        print(f"{'='*60}")
        
        # For Sprint 1, just create a new plan
        # In Sprint 2+, this will intelligently modify based on feedback
        plan = self.create_plan(state)
        
        plan.optimization_notes = f"Re-planned based on feedback: {feedback}"
        
        return plan
    
    def _analyze_brief(self, brief: Brief) -> BriefAnalysis:
        """
        Analyze brief to determine complexity and requirements.
        
        Args:
            brief: User brief
            
        Returns:
            Brief analysis
        """
        print(f"🔍 Analyzing brief...")
        
        # Mock complexity analysis (Sprint 1)
        # In Sprint 2+, this will use LLM
        
        # Simple heuristics
        topic_length = len(brief.topic)
        has_key_points = len(brief.key_points) > 0
        has_sources = len(brief.sources_to_include) > 0
        target_length = brief.target_length or 2000
        
        # Calculate complexity (0-1)
        complexity = 0.5  # Base
        if topic_length > 50:
            complexity += 0.1
        if has_key_points:
            complexity += 0.1
        if has_sources:
            complexity += 0.1
        if target_length > 3000:
            complexity += 0.2
        complexity = min(complexity, 1.0)
        
        # Determine research depth
        if complexity > 0.7:
            research_depth = 15
        elif complexity > 0.5:
            research_depth = 10
        else:
            research_depth = 5
        
        # Determine if multi-hop needed
        requires_multi_hop = complexity > 0.7 or len(brief.key_points) > 3
        
        analysis = BriefAnalysis(
            brief_id=brief.request_id or "unknown",
            complexity_score=complexity,
            estimated_research_depth=research_depth,
            requires_multi_hop=requires_multi_hop,
            sub_topics=brief.key_points[:3] if brief.key_points else [],
            required_capabilities=[
                "web_search",
                "content_generation",
                "fact_check"
            ],
            recommended_workers=[
                "web_search_worker",
                "article_writer_worker",
                "fact_checker_worker"
            ],
            recommended_approach="Standard research → write → verify workflow",
            estimated_cost=0.15,
            estimated_time_seconds=120,
        )
        
        print(f"   Complexity: {complexity:.2f}")
        print(f"   Research depth: {research_depth} sources")
        print(f"   Multi-hop: {requires_multi_hop}")
        
        return analysis
    
    def _select_workers(
        self,
        brief: Brief,
        analysis: BriefAnalysis
    ) -> Dict[str, List[str]]:
        """
        Select appropriate workers based on brief and analysis.
        
        Args:
            brief: User brief
            analysis: Brief analysis
            
        Returns:
            Dict mapping phase to list of worker IDs
        """
        print(f"👷 Selecting workers...")
        
        # Mock worker selection (Sprint 1)
        # In Sprint 2+, this will use LLM to intelligently select
        
        selected = {
            "research": [],
            "analysis": [],
            "writing": [],
            "quality": []
        }
        
        # Research phase
        selected["research"].append("web_search_worker")
        if brief.content_type == "research_paper":
            selected["research"].append("academic_search_worker")
        if analysis.complexity_score > 0.6:
            selected["research"].append("news_search_worker")
        
        # Analysis phase
        if analysis.requires_multi_hop or len(selected["research"]) > 1:
            selected["analysis"].append("content_synthesizer_worker")
        else:
            selected["analysis"].append("summarization_worker")
        
        # Writing phase
        if brief.target_length and brief.target_length > 3000:
            # Large article: use multiple writers
            selected["writing"].append("introduction_writer_worker")
            selected["writing"].append("article_writer_worker")
            selected["writing"].append("conclusion_writer_worker")
        else:
            # Normal article: single writer
            selected["writing"].append("article_writer_worker")
        
        # Quality phase
        if brief.enable_fact_checking:
            selected["quality"].append("fact_checker_worker")
        selected["quality"].append("editor_worker")
        if brief.enable_seo_optimization:
            selected["quality"].append("seo_optimizer_worker")
        
        # Log selection
        for phase, workers in selected.items():
            if workers:
                print(f"   {phase.capitalize()}: {len(workers)} workers")
        
        return selected
    
    def _create_steps(
        self,
        selected_workers: Dict[str, List[str]],
        brief: Brief
    ) -> List[PlanStep]:
        """
        Create execution steps from selected workers.
        
        Args:
            selected_workers: Workers organized by phase
            brief: User brief
            
        Returns:
            List of execution steps
        """
        steps = []
        step_counter = 1
        
        # Research step (parallel)
        if selected_workers["research"]:
            research_step = self._create_step(
                step_id=f"step_{step_counter}",
                phase="research",
                worker_ids=selected_workers["research"],
                execution_mode=ExecutionMode.PARALLEL,
                description="Gather information from multiple sources",
            )
            steps.append(research_step)
            step_counter += 1
        
        # Analysis step (sequential, depends on research)
        if selected_workers["analysis"]:
            analysis_step = self._create_step(
                step_id=f"step_{step_counter}",
                phase="analysis",
                worker_ids=selected_workers["analysis"],
                execution_mode=ExecutionMode.SEQUENTIAL,
                description="Analyze and synthesize research findings",
                depends_on=[steps[-1].step_id] if steps else []
            )
            steps.append(analysis_step)
            step_counter += 1
        
        # Writing step (depends on analysis or research)
        if selected_workers["writing"]:
            # If multiple writers, can run in parallel
            execution_mode = (
                ExecutionMode.PARALLEL
                if len(selected_workers["writing"]) > 1
                else ExecutionMode.SEQUENTIAL
            )
            
            writing_step = self._create_step(
                step_id=f"step_{step_counter}",
                phase="writing",
                worker_ids=selected_workers["writing"],
                execution_mode=execution_mode,
                description="Generate article content",
                depends_on=[steps[-1].step_id] if steps else []
            )
            steps.append(writing_step)
            step_counter += 1
        
        # Quality step (parallel, depends on writing)
        if selected_workers["quality"]:
            quality_step = self._create_step(
                step_id=f"step_{step_counter}",
                phase="quality",
                worker_ids=selected_workers["quality"],
                execution_mode=ExecutionMode.PARALLEL,
                description="Quality assurance and verification",
                depends_on=[steps[-1].step_id] if steps else []
            )
            steps.append(quality_step)
        
        return steps
    
    def _create_step(
        self,
        step_id: str,
        phase: str,
        worker_ids: List[str],
        execution_mode: ExecutionMode,
        description: str,
        depends_on: Optional[List[str]] = None
    ) -> PlanStep:
        """
        Create a single plan step.
        
        Args:
            step_id: Unique step ID
            phase: Phase name
            worker_ids: Workers in this step
            execution_mode: Parallel or sequential
            description: Step description
            depends_on: Dependencies
            
        Returns:
            Plan step
        """
        # Calculate estimates from workers
        total_cost = 0.0
        total_time = 0
        
        for worker_id in worker_ids:
            worker_def = self.registry.get_worker(worker_id)
            if worker_def:
                total_cost += worker_def.estimated_cost
                total_time += worker_def.estimated_time_seconds
        
        # If parallel, time is max not sum
        if execution_mode == ExecutionMode.PARALLEL and len(worker_ids) > 1:
            times = []
            for worker_id in worker_ids:
                worker_def = self.registry.get_worker(worker_id)
                if worker_def:
                    times.append(worker_def.estimated_time_seconds)
            total_time = max(times) if times else total_time
        
        return PlanStep(
            step_id=step_id,
            phase=phase,
            description=description,
            worker_ids=worker_ids,
            execution_mode=execution_mode,
            depends_on=depends_on or [],
            estimated_cost=total_cost,
            estimated_time_seconds=total_time,
            status=StepStatus.PENDING,
        )
    
    def _generate_plan_id(self) -> str:
        """Generate unique plan ID."""
        self.plan_count += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"plan_{timestamp}_{self.plan_count}"


# Global instance
planner = PlannerAgent()


# Helper functions
def get_planner() -> PlannerAgent:
    """Get the planner instance."""
    return planner


def create_plan(state: AgentState) -> Plan:
    """
    Create execution plan from state.
    
    Args:
        state: Current workflow state
        
    Returns:
        Execution plan
    """
    return planner.create_plan(state)