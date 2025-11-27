"""
Orchestrator Agent - Executes plan by dispatching tasks to workers.

The Orchestrator is responsible for:
1. Executing plan steps in correct order
2. Dispatching tasks to appropriate workers
3. Handling parallel vs sequential execution
4. Collecting and aggregating worker results
5. Handling worker failures and retries
6. Tracking execution progress
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from src.meta_agent.schemas import (
    Plan,
    PlanStep,
    ExecutionMode,
    StepStatus,
    Task,
    TaskStatus,
    TaskPriority,
    TaskResult,
    TaskBatch,
    AgentState,
)
from config.worker_registry import get_worker_registry


class OrchestratorAgent:
    """
    Orchestrator Agent - Executes execution plans.
    
    The Orchestrator takes an execution plan and coordinates
    worker execution to complete all tasks.
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.registry = get_worker_registry()
        self.execution_count = 0
    
    def execute_plan(self, state: AgentState, plan: Plan) -> AgentState:
        """
        Execute the complete plan.
        
        Args:
            state: Current workflow state
            plan: Execution plan
            
        Returns:
            Updated state with execution results
        """
        print(f"\n{'='*60}")
        print(f"⚙️  Orchestrator: Executing plan")
        print(f"{'='*60}")
        print(f"Plan ID: {plan.plan_id}")
        print(f"Total steps: {plan.total_steps}")
        print(f"{'='*60}\n")
        
        self.execution_count += 1
        execution_start = time.time()
        
        # Execute each step
        for i, step in enumerate(plan.steps, 1):
            print(f"📍 Step {i}/{plan.total_steps}: {step.phase}")
            print(f"   Workers: {len(step.worker_ids)}")
            print(f"   Mode: {step.execution_mode}")
            
            # Check dependencies
            if not self._check_dependencies(step, plan.steps):
                print(f"   ⚠️  Dependencies not met, skipping")
                step.status = StepStatus.FAILED
                continue
            
            # Execute step
            # Execute step
            step_result = self._execute_step(state, step, plan)
            
            # Update state with results
            state = self._update_state_with_results(state, step, step_result)
            
            # Mark step complete
            step.status = StepStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            
            print(f"   ✅ Step completed")
            print()
        
        # Calculate execution time
        execution_time = time.time() - execution_start
        
        print(f"{'='*60}")
        print(f"✅ Orchestrator: Plan execution complete")
        print(f"   Total time: {execution_time:.1f}s")
        print(f"   Steps completed: {sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)}/{plan.total_steps}")
        print(f"{'='*60}\n")
        
        # Record in state
        state.add_agent_action(
            agent_name="Orchestrator",
            action="execute_plan",
            details={
                "plan_id": plan.plan_id,
                "steps_completed": sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED),
                "execution_time": execution_time,
            }
        )
        
        return state
    
    def _check_dependencies(self, step: PlanStep, all_steps: List[PlanStep]) -> bool:
        """
        Check if step dependencies are met.
        
        Args:
            step: Step to check
            all_steps: All steps in plan
            
        Returns:
            True if dependencies met
        """
        if not step.depends_on:
            return True
        
        # Check all dependencies completed
        for dep_id in step.depends_on:
            dep_step = next((s for s in all_steps if s.step_id == dep_id), None)
            if not dep_step or dep_step.status != StepStatus.COMPLETED:
                return False
        
        return True
    
    def _execute_step(self, state: AgentState, step: PlanStep, plan: Plan) -> Dict[str, Any]:
        """
        Execute a single step.
        
        Args:
            state: Current state
            step: Step to execute
            
        Returns:
            Step execution results
        """
        step.status = StepStatus.IN_PROGRESS
        step.started_at = datetime.utcnow()
        
        if step.execution_mode == ExecutionMode.PARALLEL:
            return self._execute_parallel(state, step, plan)
        else:
            return self._execute_sequential(state, step, plan)
    
    def _execute_parallel(self, state: AgentState, step: PlanStep, plan: Plan) -> Dict[str, Any]:
        """
        Execute workers in parallel.
        
        Args:
            state: Current state
            step: Step to execute
            
        Returns:
            Aggregated results
        """
        print(f"   ⚡ Executing {len(step.worker_ids)} workers in parallel")
        
        # In Sprint 1: Mock parallel execution
        # In Sprint 2+: Use asyncio or threading for real parallelization
        
        results = []
        for worker_id in step.worker_ids:
            result = self._execute_worker(state, worker_id, step.phase, step.step_id, plan.plan_id)
            results.append(result)
        
        # Aggregate results
        aggregated = self._aggregate_results(results, step.phase)
        
        return aggregated
    
    def _execute_sequential(self, state: AgentState, step: PlanStep, plan: Plan) -> Dict[str, Any]:
        """
        Execute workers sequentially.
        
        Args:
            state: Current state
            step: Step to execute
            
        Returns:
            Aggregated results
        """
        print(f"   → Executing {len(step.worker_ids)} workers sequentially")
        
        results = []
        for worker_id in step.worker_ids:
            result = self._execute_worker(state, worker_id, step.phase, step.step_id, plan.plan_id)
            results.append(result)
        
        # Aggregate results
        aggregated = self._aggregate_results(results, step.phase)
        
        return aggregated
    
    def _execute_worker(
        self,
        state: AgentState,
        worker_id: str,
        phase: str,
        step_id: str,
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Execute a single worker.
        
        Args:
            state: Current state
            worker_id: Worker to execute
            phase: Current phase
            step_id: Current step ID
            plan_id: Current plan ID
            
        Returns:
            Worker result
        """
        worker_def = self.registry.get_worker(worker_id)
        if not worker_def:
            print(f"      ❌ Worker not found: {worker_id}")
            return {"status": "failed", "error": f"Worker {worker_id} not found"}
        
        print(f"      🔧 {worker_id}")
        
        # Simulate execution time
        time.sleep(0.1)
        
        # Create mock result based on phase
        result = self._create_mock_result(state, worker_def, phase)
        
        # Track cost
        state.add_cost(worker_id, worker_def.estimated_cost)
        
        # Create task record
        task = Task(
            task_id=f"task_{worker_id}_{int(time.time())}",
            step_id=step_id,  # ← ADD THIS
            plan_id=plan_id,  # ← ADD THIS
            worker_id=worker_id,
            input_data={"phase": phase, "brief": state.brief.topic},
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.MEDIUM,
        )
        
        # Add to state
        state.all_tasks.append(task)
        state.completed_tasks.append(task)
        
        return result
    
    def _create_mock_result(
        self,
        state: AgentState,
        worker_def: Any,
        phase: str
        ) -> Dict[str, Any]:
        
        """
        Create mock result for Sprint 1.
        
        Args:
            state: Current state
            worker_def: Worker definition
            phase: Current phase
            
        Returns:
            Mock result
        """
        topic = state.brief.topic
        
        if phase == "research":
            return {
                "status": "success",
                "worker_id": worker_def.id,  # ← CHANGED: worker_id → id
                "sources": [
                    f"Source 1 about {topic}",
                    f"Source 2 about {topic}",
                    f"Source 3 about {topic}",
                ],
                "summary": f"Research findings about {topic}...",
                "confidence": 0.85,
            }
        
        elif phase == "analysis":
            return {
                "status": "success",
                "worker_id": worker_def.id,  # ← CHANGED
                "key_insights": [
                    f"Insight 1 about {topic}",
                    f"Insight 2 about {topic}",
                ],
                "themes": ["theme1", "theme2"],
                "confidence": 0.88,
            }
        
        elif phase == "writing":
            return {
                "status": "success",
                "worker_id": worker_def.id,  # ← CHANGED
                "content": f"Article content about {topic}...",
                "word_count": state.brief.target_length or 2000,
                "sections": ["Introduction", "Main Content", "Conclusion"],
            }
        
        elif phase == "quality":
            return {
                "status": "success",
                "worker_id": worker_def.id,  # ← CHANGED
                "quality_score": 88.0,
                "issues_found": 2,
                "suggestions": [
                    "Add more examples",
                    "Improve transitions"
                ],
            }
        
        else:
            return {
                "status": "success",
                "worker_id": worker_def.id,  # ← CHANGED
                "result": f"Result from {phase}",
            }
    
    def _aggregate_results(self, results: List[Dict[str, Any]], phase: str) -> Dict[str, Any]:
        """
        Aggregate results from multiple workers.
        
        Args:
            results: List of worker results
            phase: Current phase
            
        Returns:
            Aggregated result
        """
        # Simple aggregation for Sprint 1
        # In Sprint 2+: Intelligent synthesis
        
        successful = [r for r in results if r.get("status") == "success"]
        
        aggregated = {
            "phase": phase,
            "total_workers": len(results),
            "successful_workers": len(successful),
            "results": results,
        }
        
        # Phase-specific aggregation
        if phase == "research":
            all_sources = []
            for r in successful:
                all_sources.extend(r.get("sources", []))
            aggregated["all_sources"] = all_sources
            aggregated["total_sources"] = len(all_sources)
        
        elif phase == "quality":
            scores = [r.get("quality_score", 0) for r in successful]
            aggregated["average_quality"] = sum(scores) / len(scores) if scores else 0
        
        return aggregated
    
    def _update_state_with_results(
        self,
        state: AgentState,
        step: PlanStep,
        results: Dict[str, Any]
    ) -> AgentState:
        """
        Update state with step results.
        
        Args:
            state: Current state
            step: Completed step
            results: Step results
            
        Returns:
            Updated state
        """
        phase = step.phase
        
        # Store results in appropriate state field
        if phase == "research":
            state.research_results = results
        elif phase == "analysis":
            state.analysis_results = results
        elif phase == "writing":
            state.writing_results = results
        elif phase == "quality":
            state.quality_results = results
            # Update quality score
            if "average_quality" in results:
                state.quality_score = results["average_quality"]
        
        return state
    
    def create_task_batch(
        self,
        worker_ids: List[str],
        phase: str,
        state: AgentState,
        step_id: str,
        plan_id: str
    ) -> TaskBatch:
        """
        Create a batch of tasks for workers.
        
        Args:
            worker_ids: Workers to create tasks for
            phase: Current phase
            state: Current state
            step_id: Step ID
            plan_id: Plan ID
            
        Returns:
            Task batch
        """
        tasks = []
        
        for worker_id in worker_ids:
            task = Task(
                task_id=f"task_{worker_id}_{int(time.time())}",
                step_id=step_id,  # ← ADD THIS
                plan_id=plan_id,  # ← ADD THIS
                worker_id=worker_id,
                input_data={
                    "phase": phase,
                    "brief": state.brief.model_dump(),
                },
                status=TaskStatus.PENDING,
                priority=TaskPriority.MEDIUM,
            )
            tasks.append(task)
        
        batch = TaskBatch(
            batch_id=f"batch_{phase}_{int(time.time())}",
            tasks=tasks,
            tasks_count=len(tasks),
        )
        
        return batch


# Global instance
orchestrator = OrchestratorAgent()


# Helper functions
def get_orchestrator() -> OrchestratorAgent:
    """Get the orchestrator instance."""
    return orchestrator


def execute_plan(state: AgentState, plan: Plan) -> AgentState:
    """
    Execute execution plan.
    
    Args:
        state: Current workflow state
        plan: Execution plan
        
    Returns:
        Updated state
    """
    return orchestrator.execute_plan(state, plan)