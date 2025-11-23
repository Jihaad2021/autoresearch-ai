"""
Plan Schema - Execution plan structure.
Represents the step-by-step plan created by the Planner.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    """Execution mode for a step."""
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"


class StepStatus(str, Enum):
    """Status of a step in the plan."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PlanStep(BaseModel):
    """
    Single step in the execution plan.
    
    A step represents a phase of work (e.g., research, writing).
    """
    
    step_id: str = Field(..., description="Unique step ID")
    phase: str = Field(..., description="Phase name (research, analysis, writing, quality)")
    description: str = Field(..., description="What this step does")
    
    # Workers
    worker_ids: List[str] = Field(..., description="Workers to execute in this step")
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.SEQUENTIAL,
        description="Parallel or sequential"
    )
    
    # Dependencies
    depends_on: List[str] = Field(
        default_factory=list,
        description="Step IDs that must complete first"
    )
    
    # Estimates
    estimated_cost: float = Field(default=0.0, ge=0.0)
    estimated_time_seconds: int = Field(default=30, ge=1)
    
    # Status
    status: StepStatus = Field(default=StepStatus.PENDING)
    actual_cost: Optional[float] = Field(default=None)
    actual_time_seconds: Optional[int] = Field(default=None)
    
    # Results
    output: Optional[Dict[str, Any]] = Field(default=None, description="Step output")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    class Config:
        use_enum_values = True


class Plan(BaseModel):
    """
    Complete execution plan.
    
    Created by Planner, executed by Orchestrator.
    """
    
    plan_id: str = Field(..., description="Unique plan ID")
    brief_id: str = Field(..., description="Reference to brief")
    
    # Steps
    steps: List[PlanStep] = Field(..., description="Ordered list of steps")
    
    # Metadata
    total_steps: int = Field(..., description="Total number of steps", ge=1)
    parallel_steps: int = Field(default=0, description="Number of parallel steps", ge=0)
    
    # Estimates
    estimated_total_cost: float = Field(..., description="Total estimated cost", ge=0.0)
    estimated_total_time: int = Field(..., description="Total estimated time (seconds)", ge=1)
    
    # Optimization
    optimization_notes: Optional[str] = Field(
        default=None,
        description="Notes from Strategy Agent"
    )
    
    # Status
    status: StepStatus = Field(default=StepStatus.PENDING)
    current_step_index: int = Field(default=0, ge=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    def get_current_step(self) -> Optional[PlanStep]:
        """Get the current step being executed."""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def get_completed_steps(self) -> List[PlanStep]:
        """Get all completed steps."""
        return [s for s in self.steps if s.status == StepStatus.COMPLETED]
    
    def get_pending_steps(self) -> List[PlanStep]:
        """Get all pending steps."""
        return [s for s in self.steps if s.status == StepStatus.PENDING]
    
    def is_complete(self) -> bool:
        """Check if all steps are completed."""
        return all(s.status == StepStatus.COMPLETED for s in self.steps)
    
    def get_total_actual_cost(self) -> float:
        """Get total actual cost of completed steps."""
        return sum(s.actual_cost or 0.0 for s in self.steps)
    
    def get_total_actual_time(self) -> int:
        """Get total actual time of completed steps."""
        return sum(s.actual_time_seconds or 0 for s in self.steps)


class PlanRevision(BaseModel):
    """
    Revision to an existing plan.
    
    Created by Supervisor when requesting re-planning.
    """
    
    original_plan_id: str = Field(..., description="ID of plan being revised")
    revision_reason: str = Field(..., description="Why revision is needed")
    feedback: str = Field(..., description="Feedback from Supervisor")
    
    # What to change
    steps_to_add: List[PlanStep] = Field(default_factory=list)
    steps_to_remove: List[str] = Field(default_factory=list, description="Step IDs to remove")
    steps_to_modify: List[PlanStep] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)