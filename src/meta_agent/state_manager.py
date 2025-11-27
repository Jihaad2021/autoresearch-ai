"""
State Manager Agent - Manages workflow state throughout execution.

The State Manager is responsible for:
1. Initializing workflow state
2. Tracking phase transitions
3. Recording agent actions
4. Managing iteration count
5. Providing state snapshots
6. Validating state changes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Optional, List, Dict, Any
from datetime import datetime
import copy

from src.meta_agent.schemas import (
    AgentState,
    Brief,
    WorkflowPhase,
    StateHistory,
    Plan,
)


class StateManagerAgent:
    """
    State Manager Agent - Tracks and manages workflow state.
    
    This agent maintains the complete state of the system throughout
    the workflow execution. It provides methods to update state,
    track history, and ensure state consistency.
    """
    
    def __init__(self):
        """Initialize state manager."""
        self.current_state: Optional[AgentState] = None
        self.state_history: List[StateHistory] = []
        self.snapshot_count = 0
    
    def initialize_state(self, brief: Brief, max_iterations: int = 3) -> AgentState:
        """
        Initialize a new workflow state.
        
        Args:
            brief: User brief
            max_iterations: Maximum iterations allowed
            
        Returns:
            Initialized AgentState
        """
        print(f"📋 State Manager: Initializing state")
        
        state = AgentState(
            brief=brief,
            current_phase=WorkflowPhase.INITIALIZED,
            iteration=1,
            max_iterations=max_iterations,
        )
        
        # Record initialization
        state.add_agent_action(
            agent_name="StateManager",
            action="initialize_state",
            details={
                "topic": brief.topic,
                "max_iterations": max_iterations,
            }
        )
        
        self.current_state = state
        
        # Create snapshot
        self._create_snapshot(state, "State initialized")
        
        print(f"   ✅ State initialized")
        print(f"   Topic: {brief.topic}")
        print(f"   Max iterations: {max_iterations}")
        
        return state
    
    def update_phase(
        self,
        state: AgentState,
        new_phase: WorkflowPhase,
        details: Optional[Dict[str, Any]] = None
    ) -> AgentState:
        """
        Update workflow phase.
        
        Args:
            state: Current state
            new_phase: New phase to transition to
            details: Optional details about the transition
            
        Returns:
            Updated state
        """
        old_phase = state.current_phase
        
        print(f"🔄 State Manager: Phase transition")
        print(f"   {old_phase} → {new_phase}")
        
        # Validate transition
        if not self._is_valid_transition(old_phase, new_phase):
            print(f"   ⚠️  Warning: Unusual phase transition")
        
        # Update phase
        state.current_phase = new_phase
        
        # Record action
        state.add_agent_action(
            agent_name="StateManager",
            action="update_phase",
            details={
                "old_phase": old_phase,
                "new_phase": new_phase,
                **(details or {})
            }
        )
        
        # Update current state
        self.current_state = state
        
        # Create snapshot
        self._create_snapshot(state, f"Phase: {new_phase}")
        
        return state
    
    def increment_iteration(self, state: AgentState) -> AgentState:
        """
        Increment iteration count.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        old_iteration = state.iteration
        state.increment_iteration()
        
        print(f"🔢 State Manager: Iteration incremented")
        print(f"   {old_iteration} → {state.iteration}")
        
        # Record action
        state.add_agent_action(
            agent_name="StateManager",
            action="increment_iteration",
            details={
                "old_iteration": old_iteration,
                "new_iteration": state.iteration,
            }
        )
        
        # Update current state
        self.current_state = state
        
        return state
    
    def add_cost(
        self,
        state: AgentState,
        worker_id: str,
        cost: float
    ) -> AgentState:
        """
        Add cost for a worker execution.
        
        Args:
            state: Current state
            worker_id: Worker ID
            cost: Cost incurred
            
        Returns:
            Updated state
        """
        state.add_cost(worker_id, cost)
        
        print(f"💰 State Manager: Cost added")
        print(f"   Worker: {worker_id}")
        print(f"   Cost: ${cost:.4f}")
        print(f"   Total: ${state.total_cost:.4f}")
        
        # Update current state
        self.current_state = state
        
        return state
    
    def add_error(self, state: AgentState, error: str) -> AgentState:
        """
        Add an error to state.
        
        Args:
            state: Current state
            error: Error message
            
        Returns:
            Updated state
        """
        state.add_error(error)
        
        print(f"❌ State Manager: Error recorded")
        print(f"   Error: {error}")
        
        # Update current state
        self.current_state = state
        
        return state
    
    def record_plan(self, state: AgentState, plan: Plan) -> AgentState:
        """
        Record execution plan in state.
        
        Args:
            state: Current state
            plan: Execution plan
            
        Returns:
            Updated state
        """
        # If there's an existing plan, save to history
        if state.plan is not None:
            state.previous_plans.append(state.plan)
        
        # Set new plan
        state.plan = plan
        
        print(f"📝 State Manager: Plan recorded")
        print(f"   Total steps: {plan.total_steps}")
        print(f"   Estimated cost: ${plan.estimated_total_cost:.2f}")
        print(f"   Estimated time: {plan.estimated_total_time}s")
        
        # Record action
        state.add_agent_action(
            agent_name="StateManager",
            action="record_plan",
            details={
                "plan_id": plan.plan_id,
                "total_steps": plan.total_steps,
                "estimated_cost": plan.estimated_total_cost,
            }
        )
        
        # Update current state
        self.current_state = state
        
        # Create snapshot
        self._create_snapshot(state, "Plan recorded")
        
        return state
    
    def get_current_state(self) -> Optional[AgentState]:
        """
        Get current workflow state.
        
        Returns:
            Current state or None if not initialized
        """
        return self.current_state
    
    def get_state_history(self) -> List[StateHistory]:
        """
        Get state history snapshots.
        
        Returns:
            List of state snapshots
        """
        return self.state_history
    
    def get_state_summary(self, state: AgentState) -> Dict[str, Any]:
        """
        Get summary of current state.
        
        Args:
            state: State to summarize
            
        Returns:
            Summary dict
        """
        return {
            "request_id": state.brief.request_id,
            "topic": state.brief.topic,
            "current_phase": state.current_phase,
            "iteration": state.iteration,
            "max_iterations": state.max_iterations,
            "total_cost": state.total_cost,
            "total_tasks": len(state.all_tasks),
            "completed_tasks": len(state.completed_tasks),
            "failed_tasks": len(state.failed_tasks),
            "error_count": len(state.errors),
            "has_plan": state.plan is not None,
            "quality_score": state.quality_score,
            "should_continue": state.should_continue,
        }
    
    def can_continue_iteration(self, state: AgentState) -> bool:
        """
        Check if workflow can continue to next iteration.
        
        Args:
            state: Current state
            
        Returns:
            True if can continue, False otherwise
        """
        can_continue = state.can_continue()
        
        print(f"🔍 State Manager: Checking if can continue")
        print(f"   Current iteration: {state.iteration}/{state.max_iterations}")
        print(f"   Can continue: {can_continue}")
        
        return can_continue
    
    def mark_completed(self, state: AgentState) -> AgentState:
        """
        Mark workflow as completed.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        state.mark_completed()
        
        print(f"✅ State Manager: Workflow marked as completed")
        print(f"   Total duration: {state.total_duration_seconds:.1f}s")
        print(f"   Total cost: ${state.total_cost:.2f}")
        
        # Record action
        state.add_agent_action(
            agent_name="StateManager",
            action="mark_completed",
            details={
                "duration": state.total_duration_seconds,
                "cost": state.total_cost,
            }
        )
        
        # Update current state
        self.current_state = state
        
        # Create final snapshot
        self._create_snapshot(state, "Workflow completed")
        
        return state
    
    def mark_failed(self, state: AgentState, reason: str) -> AgentState:
        """
        Mark workflow as failed.
        
        Args:
            state: Current state
            reason: Failure reason
            
        Returns:
            Updated state
        """
        state.mark_failed(reason)
        
        print(f"❌ State Manager: Workflow marked as failed")
        print(f"   Reason: {reason}")
        
        # Update current state
        self.current_state = state
        
        # Create final snapshot
        self._create_snapshot(state, f"Failed: {reason}")
        
        return state
    
    def _is_valid_transition(
        self,
        old_phase: WorkflowPhase,
        new_phase: WorkflowPhase
    ) -> bool:
        """
        Check if phase transition is valid.
        
        Args:
            old_phase: Current phase
            new_phase: Target phase
            
        Returns:
            True if valid transition
        """
        # Define valid transitions
        valid_transitions = {
            WorkflowPhase.INITIALIZED: [WorkflowPhase.PLANNING],
            WorkflowPhase.PLANNING: [WorkflowPhase.STRATEGY, WorkflowPhase.FAILED],
            WorkflowPhase.STRATEGY: [WorkflowPhase.EXECUTING, WorkflowPhase.FAILED],
            WorkflowPhase.EXECUTING: [WorkflowPhase.EVALUATING, WorkflowPhase.FAILED],
            WorkflowPhase.EVALUATING: [
                WorkflowPhase.RE_PLANNING,
                WorkflowPhase.MERGING,
                WorkflowPhase.FAILED
            ],
            WorkflowPhase.RE_PLANNING: [WorkflowPhase.STRATEGY, WorkflowPhase.FAILED],
            WorkflowPhase.MERGING: [WorkflowPhase.COMPLETED, WorkflowPhase.FAILED],
            WorkflowPhase.COMPLETED: [],
            WorkflowPhase.FAILED: [],
        }
        
        allowed = valid_transitions.get(old_phase, [])
        return new_phase in allowed
    
    def _create_snapshot(self, state: AgentState, notes: str) -> None:
        """
        Create a snapshot of current state.
        
        Args:
            state: State to snapshot
            notes: Notes about this snapshot
        """
        self.snapshot_count += 1
        
        snapshot = StateHistory(
            snapshot_id=f"snapshot_{self.snapshot_count}",
            state=copy.deepcopy(state),
            phase=state.current_phase,
            iteration=state.iteration,
            notes=notes,
        )
        
        self.state_history.append(snapshot)
    
    def print_state_summary(self, state: AgentState) -> None:
        """
        Print summary of current state.
        
        Args:
            state: State to print
        """
        summary = self.get_state_summary(state)
        
        print(f"\n{'='*60}")
        print(f"STATE SUMMARY")
        print(f"{'='*60}")
        print(f"Request ID:       {summary['request_id']}")
        print(f"Topic:            {summary['topic']}")
        print(f"Phase:            {summary['current_phase']}")
        print(f"Iteration:        {summary['iteration']}/{summary['max_iterations']}")
        print(f"Total Cost:       ${summary['total_cost']:.2f}")
        print(f"Tasks:            {summary['completed_tasks']}/{summary['total_tasks']} completed")
        print(f"Errors:           {summary['error_count']}")
        print(f"Has Plan:         {summary['has_plan']}")
        print(f"Quality Score:    {summary['quality_score']}")
        print(f"Should Continue:  {summary['should_continue']}")
        print(f"{'='*60}\n")


# Global instance
state_manager = StateManagerAgent()


# Helper functions
def get_state_manager() -> StateManagerAgent:
    """Get the state manager instance."""
    return state_manager


def initialize_state(brief: Brief, max_iterations: int = 3) -> AgentState:
    """
    Initialize workflow state.
    
    Args:
        brief: User brief
        max_iterations: Maximum iterations
        
    Returns:
        Initialized state
    """
    return state_manager.initialize_state(brief, max_iterations)