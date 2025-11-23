"""
Worker Schema - Worker input/output structures.
Standardized format for worker execution.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class WorkerInput(BaseModel):
    """
    Standardized input for workers.
    
    Orchestrator creates this and passes to workers.
    """
    
    # Identity
    task_id: str = Field(..., description="Task ID")
    worker_id: str = Field(..., description="Worker ID")
    
    # Data
    data: Dict[str, Any] = Field(..., description="Input data for the worker")
    
    # Context
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context from previous steps"
    )
    previous_results: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Results from dependent tasks"
    )
    
    # Configuration
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Worker-specific configuration"
    )
    
    # LLM Settings (override defaults if needed)
    temperature: Optional[float] = Field(default=None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    
    # Constraints
    timeout_seconds: int = Field(default=300, ge=10)
    max_cost: Optional[float] = Field(default=None, ge=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkerOutput(BaseModel):
    """
    Standardized output from workers.
    
    Workers return this to Orchestrator.
    """
    
    # Identity
    task_id: str = Field(..., description="Task ID that was executed")
    worker_id: str = Field(..., description="Worker that executed it")
    
    # Result
    success: bool = Field(..., description="Whether execution succeeded")
    data: Optional[Any] = Field(default=None, description="Output data")
    
    # Error (if failed)
    error_message: Optional[str] = Field(default=None)
    error_type: Optional[str] = Field(default=None)
    error_details: Optional[Dict[str, Any]] = Field(default=None)
    
    # Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (sources, citations, etc.)"
    )
    
    # Quality Indicators
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence in the output (0-1)"
    )
    completeness_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How complete the output is (0-1)"
    )
    
    # Metrics
    duration_seconds: float = Field(..., description="Execution time")
    cost: float = Field(default=0.0, ge=0.0, description="Cost incurred")
    tokens_used: Optional[int] = Field(default=None)
    tokens_input: Optional[int] = Field(default=None)
    tokens_output: Optional[int] = Field(default=None)
    
    # Sources (if applicable)
    sources_used: List[str] = Field(
        default_factory=list,
        description="URLs or sources consulted"
    )
    citations: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Citations in structured format"
    )
    
    # Warnings
    warnings: List[str] = Field(
        default_factory=list,
        description="Non-fatal warnings"
    )
    
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class WorkerConfig(BaseModel):
    """
    Configuration for a worker instance.
    
    Combines WorkerDefinition with runtime settings.
    """
    
    worker_id: str = Field(..., description="Worker ID")
    
    # LLM Settings
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1)
    model: str = Field(default="claude-sonnet-4-20250514")
    
    # Execution Settings
    timeout_seconds: int = Field(default=300, ge=10)
    max_retries: int = Field(default=3, ge=0)
    
    # Tools
    enabled_tools: List[str] = Field(
        default_factory=list,
        description="Tools this worker can use"
    )
    tool_configs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration for each tool"
    )
    
    # Custom Settings
    custom_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Worker-specific custom configuration"
    )


class WorkerMetrics(BaseModel):
    """
    Metrics for worker performance tracking.
    
    Used for monitoring and optimization.
    """
    
    worker_id: str = Field(..., description="Worker ID")
    
    # Execution Stats
    total_executions: int = Field(default=0, ge=0)
    successful_executions: int = Field(default=0, ge=0)
    failed_executions: int = Field(default=0, ge=0)
    
    # Performance
    average_duration_seconds: float = Field(default=0.0, ge=0.0)
    min_duration_seconds: Optional[float] = Field(default=None)
    max_duration_seconds: Optional[float] = Field(default=None)
    
    # Cost
    total_cost: float = Field(default=0.0, ge=0.0)
    average_cost: float = Field(default=0.0, ge=0.0)
    
    # Tokens
    total_tokens_used: int = Field(default=0, ge=0)
    average_tokens_used: float = Field(default=0.0, ge=0.0)
    
    # Quality
    average_confidence_score: Optional[float] = Field(default=None)
    
    # Timing
    first_execution: Optional[datetime] = Field(default=None)
    last_execution: Optional[datetime] = Field(default=None)
    
    def record_execution(
        self,
        success: bool,
        duration: float,
        cost: float,
        tokens: int = 0,
        confidence: Optional[float] = None
    ) -> None:
        """Record an execution."""
        self.total_executions += 1
        
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        
        # Update averages
        self.average_duration_seconds = (
            (self.average_duration_seconds * (self.total_executions - 1) + duration)
            / self.total_executions
        )
        
        self.total_cost += cost
        self.average_cost = self.total_cost / self.total_executions
        
        self.total_tokens_used += tokens
        self.average_tokens_used = self.total_tokens_used / self.total_executions
        
        # Update min/max duration
        if self.min_duration_seconds is None or duration < self.min_duration_seconds:
            self.min_duration_seconds = duration
        if self.max_duration_seconds is None or duration > self.max_duration_seconds:
            self.max_duration_seconds = duration
        
        # Update confidence
        if confidence is not None:
            if self.average_confidence_score is None:
                self.average_confidence_score = confidence
            else:
                self.average_confidence_score = (
                    (self.average_confidence_score * (self.total_executions - 1) + confidence)
                    / self.total_executions
                )
        
        # Update timestamps
        now = datetime.utcnow()
        if self.first_execution is None:
            self.first_execution = now
        self.last_execution = now