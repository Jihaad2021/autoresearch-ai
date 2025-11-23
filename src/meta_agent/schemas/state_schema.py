"""
State Schema - System state for LangGraph.
Represents the complete state of the agent system during execution.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

from .brief_schema import Brief, BriefAnalysis
from .plan_schema import Plan
from .task_schema import Task, TaskResult


class WorkflowPhase(str, Enum):
    """Current phase of the workflow."""
    INITIALIZED = "initialized"
    PLANNING = "planning"
    STRATEGY = "strategy"
    EXECUTING = "executing"
    EVALUATING = "evaluating"
    RE_PLANNING = "re_planning"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(BaseModel):
    """
    Complete state of the agent system.
    
    This is the main state object that flows through LangGraph.
    Each agent reads from and writes to this state.
    """
    
    # =========================================================================
    # CORE DATA
    # =========================================================================
    
    # User Input
    brief: Brief = Field(..., description="Original user brief")
    brief_analysis: Optional[BriefAnalysis] = Field(
        default=None,
        description="Analysis by Planner"
    )
    
    # Execution Plan
    plan: Optional[Plan] = Field(default=None, description="Current execution plan")
    previous_plans: List[Plan] = Field(
        default_factory=list,
        description="Previous plans (for re-planning)"
    )
    
    # =========================================================================
    # WORKFLOW STATUS
    # =========================================================================
    
    # Phase
    current_phase: WorkflowPhase = Field(
        default=WorkflowPhase.INITIALIZED,
        description="Current workflow phase"
    )
    
    # Iteration
    iteration: int = Field(default=1, ge=1, description="Current iteration number")
    max_iterations: int = Field(default=3, ge=1, description="Max iterations allowed")
    
    # =========================================================================
    # EXECUTION DATA
    # =========================================================================
    
    # Tasks
    all_tasks: List[Task] = Field(
        default_factory=list,
        description="All tasks created"
    )
    completed_tasks: List[TaskResult] = Field(
        default_factory=list,
        description="Completed task results"
    )
    failed_tasks: List[Task] = Field(
        default_factory=list,
        description="Failed tasks"
    )
    
    # Intermediate Results
    research_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from research workers"
    )
    analysis_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from analysis workers"
    )
    writing_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from writing workers"
    )
    quality_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="Results from quality workers"
    )
    
    # =========================================================================
    # EVALUATION & FEEDBACK
    # =========================================================================
    
    # Supervisor Evaluation
    quality_score: Optional[float] = Field(
        default=None,
        description="Quality score from Supervisor (0-100)"
    )
    completeness_score: Optional[float] = Field(
        default=None,
        description="Completeness score (0-100)"
    )
    supervisor_feedback: Optional[str] = Field(
        default=None,
        description="Feedback from Supervisor"
    )
    should_continue: bool = Field(
        default=True,
        description="Whether to continue or complete"
    )
    
    # =========================================================================
    # FINAL OUTPUT
    # =========================================================================
    
    final_output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Final merged output"
    )
    
    # =========================================================================
    # METADATA & METRICS
    # =========================================================================
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    total_duration_seconds: Optional[float] = Field(default=None)
    
    # Cost
    total_cost: float = Field(default=0.0, ge=0.0, description="Total cost so far")
    cost_by_worker: Dict[str, float] = Field(
        default_factory=dict,
        description="Cost breakdown by worker"
    )
    
    # Tokens
    total_tokens_used: int = Field(default=0, ge=0)
    
    # Errors
    errors: List[str] = Field(default_factory=list, description="All errors encountered")
    
    # Agent History (for debugging/transparency)
    agent_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="History of which agent did what"
    )
    
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def add_agent_action(self, agent_name: str, action: str, details: Dict[str, Any] = None) -> None:
        """Record an agent action."""
        self.agent_history.append({
            "agent": agent_name,
            "action": action,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
            "phase": self.current_phase
        })
    
    def increment_iteration(self) -> None:
        """Increment iteration counter."""
        self.iteration += 1
    
    def can_continue(self) -> bool:
        """Check if can continue iterating."""
        return self.iteration < self.max_iterations
    
    def add_cost(self, worker_id: str, cost: float) -> None:
        """Add cost for a worker."""
        self.total_cost += cost
        if worker_id in self.cost_by_worker:
            self.cost_by_worker[worker_id] += cost
        else:
            self.cost_by_worker[worker_id] = cost
    
    def add_error(self, error: str) -> None:
        """Add an error."""
        self.errors.append(f"[{datetime.utcnow().isoformat()}] {error}")
    
    def mark_completed(self) -> None:
        """Mark workflow as completed."""
        self.current_phase = WorkflowPhase.COMPLETED
        self.completed_at = datetime.utcnow()
        if self.started_at:
            self.total_duration_seconds = (
                self.completed_at - self.started_at
            ).total_seconds()
    
    def mark_failed(self, reason: str) -> None:
        """Mark workflow as failed."""
        self.current_phase = WorkflowPhase.FAILED
        self.add_error(f"Workflow failed: {reason}")
        self.completed_at = datetime.utcnow()


class StateHistory(BaseModel):
    """
    Historical snapshot of state.
    
    Used for debugging and analysis.
    """
    
    snapshot_id: str = Field(..., description="Unique snapshot ID")
    state: AgentState = Field(..., description="State at this point")
    phase: WorkflowPhase = Field(..., description="Phase when captured")
    iteration: int = Field(..., description="Iteration when captured")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    notes: Optional[str] = Field(default=None, description="Notes about this snapshot")