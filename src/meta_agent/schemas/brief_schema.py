"""
Brief Schema - User input structure.
Represents the user's request/brief for content generation.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ContentType(str, Enum):
    """Type of content to generate."""
    ARTICLE = "article"
    REPORT = "report"
    ANALYSIS = "analysis"
    SUMMARY = "summary"
    BLOG_POST = "blog_post"
    RESEARCH_PAPER = "research_paper"


class ToneStyle(str, Enum):
    """Tone/style of the content."""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ACADEMIC = "academic"
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"
    PERSUASIVE = "persuasive"


class Brief(BaseModel):
    """
    User's brief/request for content generation.
    
    This is the input that starts the entire workflow.
    """
    
    # Core Information
    topic: str = Field(..., description="Main topic or subject", min_length=3)
    content_type: ContentType = Field(default=ContentType.ARTICLE, description="Type of content to generate")
    
    # Requirements
    target_length: Optional[int] = Field(
        default=2000,
        description="Target word count",
        ge=100,
        le=10000
    )
    tone: ToneStyle = Field(default=ToneStyle.PROFESSIONAL, description="Desired tone/style")
    target_audience: Optional[str] = Field(
        default="general",
        description="Target audience (e.g., 'general', 'experts', 'students')"
    )
    
    # Additional Context
    key_points: List[str] = Field(
        default_factory=list,
        description="Specific points to cover"
    )
    sources_to_include: List[str] = Field(
        default_factory=list,
        description="Specific sources or URLs to use"
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="SEO keywords to target"
    )
    
    # Constraints
    max_budget: Optional[float] = Field(
        default=1.0,
        description="Maximum budget in USD",
        ge=0.0
    )
    max_time_seconds: Optional[int] = Field(
        default=600,
        description="Maximum time allowed in seconds",
        ge=60
    )
    
    # Preferences
    enable_fact_checking: bool = Field(default=True, description="Enable fact-checking")
    enable_seo_optimization: bool = Field(default=True, description="Enable SEO optimization")
    citation_style: Optional[str] = Field(default="APA", description="Citation style (APA, MLA, Chicago)")
    
    # Metadata
    user_id: Optional[str] = Field(default=None, description="User ID (if authenticated)")
    request_id: Optional[str] = Field(default=None, description="Unique request ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str) -> str:
        """Validate topic is not empty."""
        if not v or v.strip() == "":
            raise ValueError("Topic cannot be empty")
        return v.strip()
    
    @field_validator("key_points")
    @classmethod
    def validate_key_points(cls, v: List[str]) -> List[str]:
        """Remove empty key points."""
        return [kp.strip() for kp in v if kp.strip()]
    
    class Config:
        use_enum_values = True


class BriefAnalysis(BaseModel):
    """
    Analysis of the brief by the Planner.
    
    Planner analyzes the brief to understand complexity and requirements.
    """
    
    brief_id: str = Field(..., description="Reference to original brief")
    
    # Complexity Assessment
    complexity_score: float = Field(..., description="Complexity score (0-1)", ge=0.0, le=1.0)
    estimated_research_depth: int = Field(..., description="How many sources needed", ge=1, le=50)
    requires_multi_hop: bool = Field(default=False, description="Needs multi-hop reasoning?")
    
    # Breakdown
    sub_topics: List[str] = Field(default_factory=list, description="Identified sub-topics")
    required_capabilities: List[str] = Field(
        default_factory=list,
        description="Worker capabilities needed"
    )
    
    # Recommendations
    recommended_workers: List[str] = Field(
        default_factory=list,
        description="Recommended worker IDs"
    )
    recommended_approach: str = Field(..., description="High-level approach")
    
    # Estimates
    estimated_cost: float = Field(..., description="Estimated cost in USD", ge=0.0)
    estimated_time_seconds: int = Field(..., description="Estimated time", ge=1)
    
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)