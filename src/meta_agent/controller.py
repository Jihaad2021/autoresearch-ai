"""
Controller Agent - Main entry point and workflow coordinator.

The Controller is the top-level agent that:
1. Receives user brief
2. Initializes workflow state
3. Coordinates all other agents (Planner, Strategy, Orchestrator, etc.)
4. Handles errors and edge cases
5. Returns final output to user
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Optional
from datetime import datetime
import uuid

from src.meta_agent.schemas import (
    Brief,
    AgentState,
    FinalOutput,
    ArticleResult,
    QualityScore,
    ExecutionMetrics,
    ErrorResult,
    WorkflowPhase,
)
from config.settings import get_settings


class ControllerAgent:
    """
    Controller Agent - Main workflow coordinator.
    
    This is the entry point for the entire system. The Controller
    receives a user brief and orchestrates all other agents to
    produce the final output.
    """
    
    def __init__(self):
        """Initialize controller."""
        self.settings = get_settings()
        self.request_count = 0
    
    def execute(self, brief: Brief) -> FinalOutput:
        """
        Main execution method - orchestrates entire workflow.
        
        Args:
            brief: User's brief/request
            
        Returns:
            FinalOutput with generated article and metadata
            
        Raises:
            Exception: If workflow fails
        """
        # Generate request ID
        request_id = self._generate_request_id()
        
        try:
            # Log start
            print(f"\n{'='*60}")
            print(f"🚀 Controller: Starting workflow for request {request_id}")
            print(f"   Topic: {brief.topic}")
            print(f"   Type: {brief.content_type}")
            print(f"{'='*60}\n")
            
            # Initialize workflow state
            state = self._initialize_state(brief, request_id)
            
            # Execute workflow (mock for Sprint 1)
            final_output = self._execute_workflow(state)
            
            # Log completion
            print(f"\n{'='*60}")
            print(f"✅ Controller: Workflow completed successfully")
            print(f"   Quality Score: {final_output.quality.overall_score}/100")
            print(f"   Cost: ${final_output.metrics.total_cost:.2f}")
            print(f"   Time: {final_output.metrics.total_duration_seconds:.1f}s")
            print(f"{'='*60}\n")
            
            return final_output
            
        except Exception as e:
            # Handle errors
            print(f"\n{'='*60}")
            print(f"❌ Controller: Workflow failed")
            print(f"   Error: {str(e)}")
            print(f"{'='*60}\n")
            
            # Return error result
            error_result = ErrorResult(
                request_id=request_id,
                error_type=type(e).__name__,
                error_message=str(e),
                failed_at_phase=WorkflowPhase.INITIALIZED,
            )
            
            raise Exception(f"Workflow failed: {error_result.error_message}")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID."""
        self.request_count += 1
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"req_{timestamp}_{self.request_count}"
    
    def _initialize_state(self, brief: Brief, request_id: str) -> AgentState:
        """
        Initialize workflow state.
        
        Args:
            brief: User brief
            request_id: Unique request ID
            
        Returns:
            Initialized AgentState
        """
        # Set request_id in brief if not set
        if not brief.request_id:
            brief.request_id = request_id
        
        # Create initial state
        state = AgentState(
            brief=brief,
            current_phase=WorkflowPhase.INITIALIZED,
            iteration=1,
            max_iterations=self.settings.max_iterations,
        )
        
        # Log state initialization
        state.add_agent_action(
            agent_name="Controller",
            action="initialize_state",
            details={
                "request_id": request_id,
                "topic": brief.topic,
                "content_type": brief.content_type,
            }
        )
        
        print(f"📋 Controller: Initialized state")
        print(f"   Request ID: {request_id}")
        print(f"   Max iterations: {state.max_iterations}")
        
        return state
    
    def _execute_workflow(self, state: AgentState) -> FinalOutput:
        """
        Execute the complete workflow.
        
        In Sprint 1 (Mock Mode), this is a simplified mock workflow.
        In Sprint 2+, this will orchestrate real agents.
        
        Args:
            state: Current workflow state
            
        Returns:
            Final output
        """
        print(f"\n🔄 Controller: Executing workflow (MOCK MODE)")
        
        # Mock workflow for Sprint 1
        # In real implementation, this will call:
        # - Planner → Strategy → Orchestrator → Supervisor → Merger
        
        # Simulate phases
        self._mock_planning_phase(state)
        self._mock_execution_phase(state)
        self._mock_evaluation_phase(state)
        self._mock_merging_phase(state)
        
        # Create final output
        final_output = self._create_final_output(state)
        
        return final_output
    
    def _mock_planning_phase(self, state: AgentState) -> None:
        """Mock planning phase."""
        print(f"   📝 Phase: Planning")
        state.current_phase = WorkflowPhase.PLANNING
        
        state.add_agent_action(
            agent_name="Controller",
            action="mock_planning",
            details={"status": "completed"}
        )
    
    def _mock_execution_phase(self, state: AgentState) -> None:
        """Mock execution phase."""
        print(f"   ⚙️  Phase: Executing")
        state.current_phase = WorkflowPhase.EXECUTING
        
        # Mock some results
        state.research_results = {
            "sources_found": 15,
            "sources": ["Source 1", "Source 2", "Source 3"]
        }
        
        state.writing_results = {
            "article": f"Mock article about {state.brief.topic}...",
            "word_count": 2000,
        }
        
        state.add_agent_action(
            agent_name="Controller",
            action="mock_execution",
            details={"tasks_completed": 5}
        )
    
    def _mock_evaluation_phase(self, state: AgentState) -> None:
        """Mock evaluation phase."""
        print(f"   🔍 Phase: Evaluating")
        state.current_phase = WorkflowPhase.EVALUATING
        
        # Mock quality scores
        state.quality_score = 88.0
        state.completeness_score = 90.0
        state.should_continue = False  # Good enough!
        
        state.add_agent_action(
            agent_name="Controller",
            action="mock_evaluation",
            details={
                "quality_score": state.quality_score,
                "decision": "complete"
            }
        )
    
    def _mock_merging_phase(self, state: AgentState) -> None:
        """Mock merging phase."""
        print(f"   🔗 Phase: Merging")
        state.current_phase = WorkflowPhase.MERGING
        
        state.add_agent_action(
            agent_name="Controller",
            action="mock_merging",
            details={"status": "completed"}
        )
        
        # Mark as completed
        state.mark_completed()
    
    def _create_final_output(self, state: AgentState) -> FinalOutput:
        """
        Create final output from state.
        
        Args:
            state: Final workflow state
            
        Returns:
            FinalOutput with all results
        """
        print(f"   📦 Creating final output")
        
        # Create article result
        article = ArticleResult(
            title=f"Understanding {state.brief.topic}",
            content=self._generate_mock_article(state.brief),
            summary=f"A comprehensive overview of {state.brief.topic}.",
            sections=[
                {
                    "title": "Introduction",
                    "content": "Introduction section..."
                },
                {
                    "title": "Main Content",
                    "content": "Main content section..."
                },
                {
                    "title": "Conclusion",
                    "content": "Conclusion section..."
                }
            ],
            word_count=state.brief.target_length or 2000,
            reading_time_minutes=(state.brief.target_length or 2000) // 200,
            keywords=state.brief.keywords or ["AI", "technology", "trends"],
            meta_description=f"Learn about {state.brief.topic} in this comprehensive article.",
        )
        
        # Create quality score
        quality = QualityScore(
            overall_score=state.quality_score or 88.0,
            factual_accuracy=92.0,
            completeness=state.completeness_score or 90.0,
            clarity=87.0,
            coherence=89.0,
            grammar=95.0,
            seo_score=84.0,
            strengths=[
                "Well-structured content",
                "Good use of examples",
                "Clear writing style"
            ],
            suggestions=[
                "Could add more recent statistics",
                "Consider adding more subheadings"
            ]
        )
        
        # Create metrics
        metrics = ExecutionMetrics(
            total_duration_seconds=state.total_duration_seconds or 95.0,
            phase_durations={
                "planning": 10.0,
                "research": 30.0,
                "analysis": 15.0,
                "writing": 25.0,
                "quality": 15.0
            },
            total_cost=0.15,
            cost_breakdown={
                "research_workers": 0.05,
                "writing_workers": 0.08,
                "quality_workers": 0.02
            },
            workers_used=[
                "web_search_worker",
                "news_search_worker",
                "content_synthesizer_worker",
                "article_writer_worker",
                "fact_checker_worker"
            ],
            total_tasks=5,
            successful_tasks=5,
            failed_tasks=0,
            total_tokens=5000,
            input_tokens=2000,
            output_tokens=3000,
            iterations=state.iteration,
            re_planning_count=0
        )
        
        # Create final output
        final_output = FinalOutput(
            request_id=state.brief.request_id or "unknown",
            brief_topic=state.brief.topic,
            article=article,
            quality=quality,
            sources=[],  # Mock: no sources in Sprint 1
            source_count=len(state.research_results.get("sources", [])) if state.research_results else 0,
            metrics=metrics,
            system_notes=[
                "Generated in mock mode (Sprint 1)",
                "Real implementation coming in Sprint 2"
            ],
            warnings=[]
        )
        
        return final_output
    
    def _generate_mock_article(self, brief: Brief) -> str:
        """
        Generate mock article content.
        
        Args:
            brief: User brief
            
        Returns:
            Mock article text
        """
        return f"""# Understanding {brief.topic}

                ## Introduction

                {brief.topic} has become an increasingly important subject in recent years. This article provides a comprehensive overview of the key concepts, current trends, and future implications.

                ## Background

                The development of {brief.topic} can be traced back to several key innovations and research breakthroughs. Understanding this context is essential for grasping its current significance.

                ## Current State

                Today, {brief.topic} is characterized by rapid advancement and widespread adoption across various industries. Recent studies have shown significant progress in multiple areas.

                ## Key Concepts

                Several fundamental concepts underpin our understanding of {brief.topic}:

                1. **Core Principles**: The foundational ideas that guide development
                2. **Practical Applications**: Real-world use cases and implementations
                3. **Technical Challenges**: Obstacles that researchers and practitioners face
                4. **Future Directions**: Emerging trends and potential breakthroughs

                ## Impact and Implications

                The impact of {brief.topic} extends far beyond its immediate domain. It has implications for technology, business, society, and individual users.

                ## Challenges and Considerations

                While promising, {brief.topic} also presents several challenges that must be addressed:

                - Technical limitations
                - Ethical considerations
                - Regulatory frameworks
                - Resource requirements

                ## Future Outlook

                Looking ahead, experts predict continued growth and evolution in {brief.topic}. Key areas of development include enhanced capabilities, broader accessibility, and novel applications.

                ## Conclusion

                {brief.topic} represents a significant area of development with far-reaching implications. As research and implementation continue to advance, we can expect to see ongoing innovation and new applications emerge.

                This comprehensive overview has covered the essential aspects of {brief.topic}, from foundational concepts to future directions. Understanding these elements is crucial for anyone looking to engage with this important field.

                ---

                *Note: This is a mock article generated for demonstration purposes (Sprint 1). Real implementation with actual research and AI-generated content coming in Sprint 2.*
                """


# Global instance
controller = ControllerAgent()


# Helper functions
def get_controller() -> ControllerAgent:
    """Get the controller instance."""
    return controller


def process_brief(brief: Brief) -> FinalOutput:
    """
    Process a user brief and return final output.
    
    This is the main entry point for the system.
    
    Args:
        brief: User's brief/request
        
    Returns:
        FinalOutput with generated content
        
    Example:
        >>> from src.meta_agent.schemas import Brief, ContentType
        >>> brief = Brief(
        ...     topic="AI trends 2024",
        ...     content_type=ContentType.ARTICLE
        ... )
        >>> output = process_brief(brief)
        >>> print(output.article.title)
    """
    return controller.execute(brief)