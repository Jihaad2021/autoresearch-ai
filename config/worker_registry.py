"""
Worker Registry - Defines all available workers for the system.
Each worker is a specialized agent that performs specific tasks.
"""

from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class WorkerCategory(str, Enum):
    """Worker categories."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    WRITING = "writing"
    QUALITY = "quality"


class WorkerCapability(str, Enum):
    """Worker capabilities."""
    WEB_SEARCH = "web_search"
    ACADEMIC_SEARCH = "academic_search"
    SOCIAL_MEDIA = "social_media"
    NEWS_SEARCH = "news_search"
    WEB_SCRAPING = "web_scraping"
    DATA_EXTRACTION = "data_extraction"
    SYNTHESIS = "synthesis"
    SUMMARIZATION = "summarization"
    FACT_CHECK = "fact_check"
    CONTENT_GENERATION = "content_generation"
    EDITING = "editing"
    SEO_OPTIMIZATION = "seo_optimization"
    CITATION_MANAGEMENT = "citation_management"


class WorkerDefinition(BaseModel):
    """Definition of a worker."""
    
    id: str = Field(..., description="Unique worker ID")
    name: str = Field(..., description="Human-readable worker name")
    category: WorkerCategory = Field(..., description="Worker category")
    description: str = Field(..., description="What this worker does")
    capabilities: List[WorkerCapability] = Field(default_factory=list, description="Worker capabilities")
    
    # Input/Output
    required_inputs: List[str] = Field(default_factory=list, description="Required input fields")
    optional_inputs: List[str] = Field(default_factory=list, description="Optional input fields")
    output_format: str = Field(..., description="Expected output format")
    
    # Execution
    can_run_parallel: bool = Field(default=False, description="Can run in parallel with others")
    estimated_cost: float = Field(default=0.01, ge=0.0, description="Estimated cost in USD")
    estimated_time_seconds: int = Field(default=30, ge=1, description="Estimated time in seconds")
    
    # Configuration
    default_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    default_max_tokens: int = Field(default=2000, ge=1)
    
    # Tools needed
    tools_required: List[str] = Field(default_factory=list, description="Tools this worker needs")
    
    class Config:
        use_enum_values = True


# =============================================================================
# RESEARCH WORKERS (5 workers)
# =============================================================================

RESEARCH_WORKERS = [
    WorkerDefinition(
        id="web_search_worker",
        name="Web Search Worker",
        category=WorkerCategory.RESEARCH,
        description="Search the web for current information using search APIs (Tavily, Serper, etc.)",
        capabilities=[WorkerCapability.WEB_SEARCH],
        required_inputs=["query", "max_results"],
        optional_inputs=["time_range", "domain_filter"],
        output_format="List of search results with title, url, snippet, relevance_score",
        can_run_parallel=True,
        estimated_cost=0.02,
        estimated_time_seconds=15,
        default_temperature=0.3,
        default_max_tokens=500,
        tools_required=["tavily_search", "serper_search"]
    ),
    
    WorkerDefinition(
        id="academic_search_worker",
        name="Academic Search Worker",
        category=WorkerCategory.RESEARCH,
        description="Search academic databases (ArXiv, PubMed, etc.) for scholarly articles and papers",
        capabilities=[WorkerCapability.ACADEMIC_SEARCH],
        required_inputs=["query", "max_results"],
        optional_inputs=["year_range", "subject_filter"],
        output_format="List of academic papers with title, authors, abstract, publication_date, citation_count",
        can_run_parallel=True,
        estimated_cost=0.01,
        estimated_time_seconds=20,
        default_temperature=0.3,
        default_max_tokens=500,
        tools_required=["arxiv_search", "pubmed_search"]
    ),
    
    WorkerDefinition(
        id="news_search_worker",
        name="News Search Worker",
        category=WorkerCategory.RESEARCH,
        description="Search recent news articles from news APIs",
        capabilities=[WorkerCapability.NEWS_SEARCH],
        required_inputs=["query", "max_results"],
        optional_inputs=["time_range", "language", "country"],
        output_format="List of news articles with title, source, published_date, url, summary",
        can_run_parallel=True,
        estimated_cost=0.01,
        estimated_time_seconds=15,
        default_temperature=0.3,
        default_max_tokens=500,
        tools_required=["news_api"]
    ),
    
    WorkerDefinition(
        id="web_scraping_worker",
        name="Web Scraping Worker",
        category=WorkerCategory.RESEARCH,
        description="Scrape and extract content from specific web pages",
        capabilities=[WorkerCapability.WEB_SCRAPING, WorkerCapability.DATA_EXTRACTION],
        required_inputs=["urls"],
        optional_inputs=["extract_tables", "extract_images"],
        output_format="Extracted text content, metadata, and structured data from URLs",
        can_run_parallel=True,
        estimated_cost=0.03,
        estimated_time_seconds=25,
        default_temperature=0.3,
        default_max_tokens=1000,
        tools_required=["firecrawl", "beautifulsoup"]
    ),
    
    WorkerDefinition(
        id="social_media_worker",
        name="Social Media Worker",
        category=WorkerCategory.RESEARCH,
        description="Search and analyze social media trends and discussions",
        capabilities=[WorkerCapability.SOCIAL_MEDIA],
        required_inputs=["query", "platforms"],
        optional_inputs=["time_range", "engagement_threshold"],
        output_format="Social media posts/trends with engagement metrics and sentiment",
        can_run_parallel=True,
        estimated_cost=0.02,
        estimated_time_seconds=20,
        default_temperature=0.5,
        default_max_tokens=500,
        tools_required=["twitter_api", "reddit_api"]
    ),
]


# =============================================================================
# ANALYSIS WORKERS (4 workers)
# =============================================================================

ANALYSIS_WORKERS = [
    WorkerDefinition(
        id="content_synthesizer_worker",
        name="Content Synthesizer Worker",
        category=WorkerCategory.ANALYSIS,
        description="Synthesize information from multiple sources into coherent insights",
        capabilities=[WorkerCapability.SYNTHESIS],
        required_inputs=["sources", "focus_areas"],
        optional_inputs=["perspective"],
        output_format="Synthesized insights with key themes, connections, and takeaways",
        can_run_parallel=False,
        estimated_cost=0.05,
        estimated_time_seconds=45,
        default_temperature=0.7,
        default_max_tokens=3000,
        tools_required=["llm"]
    ),
    
    WorkerDefinition(
        id="summarization_worker",
        name="Summarization Worker",
        category=WorkerCategory.ANALYSIS,
        description="Create concise summaries of long-form content",
        capabilities=[WorkerCapability.SUMMARIZATION],
        required_inputs=["content"],
        optional_inputs=["summary_length", "focus_points"],
        output_format="Concise summary with key points and main ideas",
        can_run_parallel=True,
        estimated_cost=0.03,
        estimated_time_seconds=30,
        default_temperature=0.5,
        default_max_tokens=1000,
        tools_required=["llm"]
    ),
    
    WorkerDefinition(
        id="trend_analyzer_worker",
        name="Trend Analyzer Worker",
        category=WorkerCategory.ANALYSIS,
        description="Identify patterns, trends, and emerging themes from data",
        capabilities=[WorkerCapability.DATA_EXTRACTION, WorkerCapability.SYNTHESIS],
        required_inputs=["data_sources"],
        optional_inputs=["time_period", "focus_area"],
        output_format="Identified trends with supporting evidence and projections",
        can_run_parallel=False,
        estimated_cost=0.04,
        estimated_time_seconds=40,
        default_temperature=0.6,
        default_max_tokens=2000,
        tools_required=["llm"]
    ),
    
    WorkerDefinition(
        id="comparative_analyzer_worker",
        name="Comparative Analyzer Worker",
        category=WorkerCategory.ANALYSIS,
        description="Compare and contrast multiple items, concepts, or sources",
        capabilities=[WorkerCapability.SYNTHESIS],
        required_inputs=["items_to_compare", "comparison_criteria"],
        optional_inputs=["weighting"],
        output_format="Comparison matrix with similarities, differences, and recommendations",
        can_run_parallel=False,
        estimated_cost=0.04,
        estimated_time_seconds=40,
        default_temperature=0.6,
        default_max_tokens=2500,
        tools_required=["llm"]
    ),
]


# =============================================================================
# WRITING WORKERS (4 workers)
# =============================================================================

WRITING_WORKERS = [
    WorkerDefinition(
        id="article_writer_worker",
        name="Article Writer Worker",
        category=WorkerCategory.WRITING,
        description="Write comprehensive articles from research and analysis",
        capabilities=[WorkerCapability.CONTENT_GENERATION],
        required_inputs=["outline", "research_data", "tone"],
        optional_inputs=["target_length", "target_audience"],
        output_format="Complete article with introduction, body sections, and conclusion",
        can_run_parallel=False,
        estimated_cost=0.08,
        estimated_time_seconds=60,
        default_temperature=0.7,
        default_max_tokens=4000,
        tools_required=["llm"]
    ),
    
    WorkerDefinition(
        id="section_writer_worker",
        name="Section Writer Worker",
        category=WorkerCategory.WRITING,
        description="Write specific sections or parts of content",
        capabilities=[WorkerCapability.CONTENT_GENERATION],
        required_inputs=["section_topic", "section_context", "target_length"],
        optional_inputs=["tone", "key_points"],
        output_format="Well-written section with proper structure and flow",
        can_run_parallel=True,
        estimated_cost=0.04,
        estimated_time_seconds=40,
        default_temperature=0.7,
        default_max_tokens=2000,
        tools_required=["llm"]
    ),
    
    WorkerDefinition(
        id="introduction_writer_worker",
        name="Introduction Writer Worker",
        category=WorkerCategory.WRITING,
        description="Write compelling introductions that hook readers",
        capabilities=[WorkerCapability.CONTENT_GENERATION],
        required_inputs=["topic", "key_points", "tone"],
        optional_inputs=["target_length"],
        output_format="Engaging introduction with hook and preview",
        can_run_parallel=True,
        estimated_cost=0.02,
        estimated_time_seconds=25,
        default_temperature=0.8,
        default_max_tokens=800,
        tools_required=["llm"]
    ),
    
    WorkerDefinition(
        id="conclusion_writer_worker",
        name="Conclusion Writer Worker",
        category=WorkerCategory.WRITING,
        description="Write effective conclusions that summarize and provide closure",
        capabilities=[WorkerCapability.CONTENT_GENERATION],
        required_inputs=["article_content", "key_takeaways"],
        optional_inputs=["call_to_action"],
        output_format="Conclusion with summary and final thoughts",
        can_run_parallel=True,
        estimated_cost=0.02,
        estimated_time_seconds=25,
        default_temperature=0.7,
        default_max_tokens=800,
        tools_required=["llm"]
    ),
]


# =============================================================================
# QUALITY WORKERS (4 workers)
# =============================================================================

QUALITY_WORKERS = [
    WorkerDefinition(
        id="fact_checker_worker",
        name="Fact Checker Worker",
        category=WorkerCategory.QUALITY,
        description="Verify factual claims against sources and check accuracy",
        capabilities=[WorkerCapability.FACT_CHECK],
        required_inputs=["content", "sources"],
        optional_inputs=["strict_mode"],
        output_format="Fact-check report with verified/unverified claims and confidence scores",
        can_run_parallel=True,
        estimated_cost=0.05,
        estimated_time_seconds=50,
        default_temperature=0.3,
        default_max_tokens=2000,
        tools_required=["llm", "web_search"]
    ),
    
    WorkerDefinition(
        id="editor_worker",
        name="Editor Worker",
        category=WorkerCategory.QUALITY,
        description="Edit content for grammar, clarity, and style",
        capabilities=[WorkerCapability.EDITING],
        required_inputs=["content"],
        optional_inputs=["style_guide", "focus_areas"],
        output_format="Edited content with tracked changes and improvement suggestions",
        can_run_parallel=True,
        estimated_cost=0.04,
        estimated_time_seconds=40,
        default_temperature=0.5,
        default_max_tokens=3000,
        tools_required=["llm"]
    ),
    
    WorkerDefinition(
        id="seo_optimizer_worker",
        name="SEO Optimizer Worker",
        category=WorkerCategory.QUALITY,
        description="Optimize content for search engines",
        capabilities=[WorkerCapability.SEO_OPTIMIZATION],
        required_inputs=["content", "target_keywords"],
        optional_inputs=["competitor_analysis"],
        output_format="SEO optimization report with keyword density, meta suggestions, and improvements",
        can_run_parallel=True,
        estimated_cost=0.03,
        estimated_time_seconds=35,
        default_temperature=0.5,
        default_max_tokens=1500,
        tools_required=["llm"]
    ),
    
    WorkerDefinition(
        id="citation_manager_worker",
        name="Citation Manager Worker",
        category=WorkerCategory.QUALITY,
        description="Manage, format, and verify citations and references",
        capabilities=[WorkerCapability.CITATION_MANAGEMENT],
        required_inputs=["content", "sources"],
        optional_inputs=["citation_style"],
        output_format="Content with properly formatted citations and bibliography",
        can_run_parallel=True,
        estimated_cost=0.02,
        estimated_time_seconds=30,
        default_temperature=0.3,
        default_max_tokens=1500,
        tools_required=["llm"]
    ),
]


# =============================================================================
# WORKER REGISTRY
# =============================================================================

class WorkerRegistry:
    """Central registry for all workers."""
    
    def __init__(self):
        """Initialize worker registry."""
        self.workers: Dict[str, WorkerDefinition] = {}
        self._register_all_workers()
    
    def _register_all_workers(self) -> None:
        """Register all workers."""
        all_workers = (
            RESEARCH_WORKERS +
            ANALYSIS_WORKERS +
            WRITING_WORKERS +
            QUALITY_WORKERS
        )
        
        for worker in all_workers:
            self.workers[worker.id] = worker
    
    def get_worker(self, worker_id: str) -> Optional[WorkerDefinition]:
        """Get worker by ID."""
        return self.workers.get(worker_id)
    
    def get_workers_by_category(self, category: WorkerCategory) -> List[WorkerDefinition]:
        """Get all workers in a category."""
        return [w for w in self.workers.values() if w.category == category]
    
    def get_workers_by_capability(self, capability: WorkerCapability) -> List[WorkerDefinition]:
        """Get all workers with a specific capability."""
        return [w for w in self.workers.values() if capability in w.capabilities]
    
    def get_parallel_workers(self) -> List[WorkerDefinition]:
        """Get all workers that can run in parallel."""
        return [w for w in self.workers.values() if w.can_run_parallel]
    
    def list_all_workers(self) -> List[WorkerDefinition]:
        """List all registered workers."""
        return list(self.workers.values())
    
    def get_worker_count(self) -> int:
        """Get total number of registered workers."""
        return len(self.workers)
    
    def get_worker_ids(self) -> List[str]:
        """Get all worker IDs."""
        return list(self.workers.keys())
    
    def estimate_total_cost(self, worker_ids: List[str]) -> float:
        """Estimate total cost for a list of workers."""
        return sum(
            self.workers[wid].estimated_cost 
            for wid in worker_ids 
            if wid in self.workers
        )
    
    def estimate_total_time(self, worker_ids: List[str], parallel: bool = False) -> int:
        """
        Estimate total time for a list of workers.
        
        Args:
            worker_ids: List of worker IDs
            parallel: If True, parallel-capable workers run simultaneously
            
        Returns:
            Estimated time in seconds
        """
        if not parallel:
            # Sequential execution
            return sum(
                self.workers[wid].estimated_time_seconds
                for wid in worker_ids
                if wid in self.workers
            )
        
        # Parallel execution (max of parallel workers, sum of sequential)
        parallel_workers = [wid for wid in worker_ids if self.workers.get(wid, None) and self.workers[wid].can_run_parallel]
        sequential_workers = [wid for wid in worker_ids if wid not in parallel_workers]
        
        if parallel_workers:
            parallel_time = max([self.workers[wid].estimated_time_seconds for wid in parallel_workers])
        else:
            parallel_time = 0

        # Calculate sequential time (sum of sequential workers)
        if sequential_workers:
            sequential_time = sum([self.workers[wid].estimated_time_seconds for wid in sequential_workers])
        else:
            sequential_time = 0        
        
        return parallel_time + sequential_time


# Global registry instance
worker_registry = WorkerRegistry()


# Convenience functions
def get_worker_registry() -> WorkerRegistry:
    """Get worker registry instance."""
    return worker_registry


def get_worker(worker_id: str) -> Optional[WorkerDefinition]:
    """Get worker by ID."""
    return worker_registry.get_worker(worker_id)


def list_workers() -> List[WorkerDefinition]:
    """List all workers."""
    return worker_registry.list_all_workers()