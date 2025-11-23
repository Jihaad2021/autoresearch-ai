"""
Task Schema - Individual task structure.
Represents a single task assigned to a worker.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of a task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(str, Enum):
    """Priority level of a task."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """
    Individual task for a worker.
    
    Orchestrator creates tasks and dispatches them to workers.
    """
    
    # Identity
    task_id: str = Field(..., description="Unique task ID")
    worker_id: str = Field(..., description="Worker assigned to this task")
    step_id: str = Field(..., description="Plan step this task belongs to")
    plan_id: str = Field(..., description="Plan this task belongs to")
    
    # Task Data
    input_data: Dict[str, Any] = Field(..., description="Input data for the worker")
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context from previous tasks"
    )
    
    # Configuration
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    timeout_seconds: int = Field(default=300, ge=10, description="Task timeout")
    max_retries: int = Field(default=3, ge=0, description="Max retry attempts")
    retry_count: int = Field(default=0, ge=0, description="Current retry count")
    
    # Status
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    duration_seconds: Optional[float] = Field(default=None)
    
    # Results
    output: Optional[Any] = Field(default=None, description="Task output")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    # Metrics
    cost: Optional[float] = Field(default=None, description="Actual cost incurred")
    tokens_used: Optional[int] = Field(default=None, description="Tokens used (if LLM)")
    
    class Config:
        use_enum_values = True
    
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries
    
    def mark_started(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()
    
    def mark_completed(self, output: Any, cost: float = 0.0) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.output = output
        self.cost = cost
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
    
    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error
        if self.started_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()


class TaskResult(BaseModel):
    """
    Result of a completed task.
    
    Returned by workers to Orchestrator.
    """
    
    task_id: str = Field(..., description="Task that was executed")
    worker_id: str = Field(..., description="Worker that executed it")
    
    # Result
    success: bool = Field(..., description="Whether task succeeded")
    output: Optional[Any] = Field(default=None, description="Task output")
    error: Optional[str] = Field(default=None, description="Error if failed")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Metrics
    duration_seconds: float = Field(..., description="Execution time")
    cost: float = Field(default=0.0, ge=0.0, description="Cost incurred")
    tokens_used: Optional[int] = Field(default=None)
    
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class TaskBatch(BaseModel):
    """
    Batch of tasks for parallel execution.
    
    Orchestrator groups tasks for parallel execution.
    """
    
    batch_id: str = Field(..., description="Unique batch ID")
    tasks: List[Task] = Field(..., description="Tasks in this batch")
    
    # Execution
    execute_parallel: bool = Field(default=True, description="Execute in parallel?")
    
    # Status
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    def get_completed_tasks(self) -> List[Task]:
        """Get completed tasks."""
        return [t for t in self.tasks if t.status == TaskStatus.COMPLETED]
    
    def get_failed_tasks(self) -> List[Task]:
        """Get failed tasks."""
        return [t for t in self.tasks if t.status == TaskStatus.FAILED]
    
    def is_complete(self) -> bool:
        """Check if all tasks are done."""
        return all(
            t.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            for t in self.tasks
        )