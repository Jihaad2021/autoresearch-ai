"""
Result Schema - Final output structures.
The final deliverable returned to the user.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Source(BaseModel):
    """
    A source/citation used in the content.
    """
    
    source_id: str = Field(..., description="Unique source ID")
    title: str = Field(..., description="Source title")
    url: Optional[str] = Field(default=None, description="Source URL")
    author: Optional[str] = Field(default=None, description="Author")
    publication_date: Optional[str] = Field(default=None, description="Publication date")
    source_type: str = Field(
        default="web",
        description="Type: web, academic, news, social, etc."
    )
    relevance_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relevance score"
    )
    excerpt: Optional[str] = Field(default=None, description="Relevant excerpt")


class QualityScore(BaseModel):
    """
    Quality assessment scores.
    """
    
    # Overall
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall quality (0-100)")
    
    # Dimensions
    factual_accuracy: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    completeness: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    clarity: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    coherence: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    grammar: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    seo_score: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    # Details
    issues_found: List[str] = Field(default_factory=list, description="Issues identified")
    strengths: List[str] = Field(default_factory=list, description="Strengths identified")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Improvement suggestions"
    )


class ExecutionMetrics(BaseModel):
    """
    Metrics about the execution.
    """
    
    # Timing
    total_duration_seconds: float = Field(..., ge=0.0, description="Total execution time")
    phase_durations: Dict[str, float] = Field(
        default_factory=dict,
        description="Duration by phase"
    )
    
    # Cost
    total_cost: float = Field(..., ge=0.0, description="Total cost in USD")
    cost_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="Cost by worker/phase"
    )
    
    # Workers
    workers_used: List[str] = Field(default_factory=list, description="Workers used")
    total_tasks: int = Field(default=0, ge=0, description="Total tasks executed")
    successful_tasks: int = Field(default=0, ge=0)
    failed_tasks: int = Field(default=0, ge=0)
    
    # Tokens
    total_tokens: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    
    # Iterations
    iterations: int = Field(default=1, ge=1, description="Number of iterations")
    re_planning_count: int = Field(default=0, ge=0, description="Times re-planned")


class ArticleResult(BaseModel):
    """
    The main article content.
    """
    
    # Content
    title: str = Field(..., description="Article title")
    content: str = Field(..., description="Full article content")
    summary: Optional[str] = Field(default=None, description="Brief summary")
    
    # Structure
    sections: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Sections with titles and content"
    )
    
    # Metadata
    word_count: int = Field(..., ge=0, description="Word count")
    reading_time_minutes: int = Field(..., ge=0, description="Estimated reading time")
    
    # SEO
    keywords: List[str] = Field(default_factory=list, description="Keywords used")
    meta_description: Optional[str] = Field(
        default=None,
        description="SEO meta description"
    )
    
    # Citations
    citations: List[Source] = Field(default_factory=list, description="Citations/sources")
    bibliography: Optional[str] = Field(
        default=None,
        description="Formatted bibliography"
    )


class FinalOutput(BaseModel):
    """
    Complete final output returned to user.
    
    This is what the user receives after the workflow completes.
    """
    
    # Request Info
    request_id: str = Field(..., description="Original request ID")
    brief_topic: str = Field(..., description="Original topic")
    
    # Main Content
    article: ArticleResult = Field(..., description="The generated article")
    
    # Quality
    quality: QualityScore = Field(..., description="Quality assessment")
    
    # Sources
    sources: List[Source] = Field(..., description="All sources used")
    source_count: int = Field(..., ge=0, description="Number of sources")
    
    # Execution Info
    metrics: ExecutionMetrics = Field(..., description="Execution metrics")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0", description="Output format version")
    
    # Additional Files (optional)
    attachments: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional files (markdown, pdf, etc.)"
    )
    
    # System Info
    system_notes: List[str] = Field(
        default_factory=list,
        description="Notes from the system"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Warnings to user"
    )
    
    def get_formatted_output(self) -> str:
        """Get formatted output for display."""
        output = f"""
# {self.article.title}

{self.article.content}

---

## Sources ({self.source_count})
"""
        for i, source in enumerate(self.sources, 1):
            output += f"\n{i}. {source.title}"
            if source.url:
                output += f" - {source.url}"
        
        output += f"""

---

## Metrics
- Word Count: {self.article.word_count}
- Reading Time: {self.article.reading_time_minutes} minutes
- Quality Score: {self.quality.overall_score:.1f}/100
- Cost: ${self.metrics.total_cost:.2f}
- Time: {self.metrics.total_duration_seconds:.1f} seconds
"""
        return output


class ErrorResult(BaseModel):
    """
    Result when workflow fails.
    """
    
    request_id: str = Field(..., description="Original request ID")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    
    # Partial Results (if any)
    partial_output: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Any partial results before failure"
    )
    
    # Debug Info
    failed_at_phase: str = Field(..., description="Phase where it failed")
    error_details: Optional[Dict[str, Any]] = Field(default=None)
    
    # What was attempted
    attempted_iterations: int = Field(default=0, ge=0)
    completed_tasks: int = Field(default=0, ge=0)
    
    failed_at: datetime = Field(default_factory=datetime.utcnow)