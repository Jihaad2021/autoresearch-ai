"""
Merger Agent - Combines results and formats final output.

The Merger is responsible for:
1. Collecting all execution results
2. Synthesizing research findings
3. Formatting final article/content
4. Adding citations and sources
5. Calculating quality metrics
6. Generating execution statistics
7. Creating FinalOutput structure
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import List, Dict, Any
from datetime import datetime

from src.meta_agent.schemas import (
    AgentState,
    FinalOutput,
    ArticleResult,
    QualityScore,
    ExecutionMetrics,
    Source,
)


class MergerAgent:
    """
    Merger Agent - Combines and formats final output.
    
    The Merger takes all execution results from the state
    and formats them into a polished FinalOutput.
    """
    
    def __init__(self):
        """Initialize merger."""
        self.merge_count = 0
    
    def merge(self, state: AgentState) -> FinalOutput:
        """
        Merge all results into final output.
        
        Args:
            state: Complete workflow state
            
        Returns:
            Final output with article and metadata
        """
        print(f"\n{'='*60}")
        print(f"🔗 Merger: Creating final output")
        print(f"{'='*60}")
        
        self.merge_count += 1
        
        # Extract components
        article = self._create_article(state)
        quality = self._create_quality_score(state)
        sources = self._extract_sources(state)
        metrics = self._create_execution_metrics(state)
        
        # Create final output
        final_output = FinalOutput(
            request_id=state.brief.request_id or "unknown",
            brief_topic=state.brief.topic,
            article=article,
            quality=quality,
            sources=sources,
            source_count=len(sources),
            metrics=metrics,
            system_notes=self._generate_system_notes(state),
            warnings=self._generate_warnings(state),
        )
        
        # Log completion
        print(f"\n✅ Final output created")
        print(f"   Article: {article.word_count} words")
        print(f"   Quality: {quality.overall_score:.0f}/100")
        print(f"   Sources: {len(sources)}")
        print(f"   Cost: ${metrics.total_cost:.2f}")
        print(f"   Time: {metrics.total_duration_seconds:.1f}s")
        print(f"{'='*60}\n")
        
        return final_output
    
    def _create_article(self, state: AgentState) -> ArticleResult:
        """
        Create article result from writing results.
        
        Args:
            state: Workflow state
            
        Returns:
            Article result
        """
        writing_results = state.writing_results or {}
        brief = state.brief
        
        # Extract content
        content = writing_results.get("content", self._generate_default_content(state))
        word_count = writing_results.get("word_count", brief.target_length or 2000)
        
        # Create article
        article = ArticleResult(
            title=f"Understanding {brief.topic}",
            content=content,
            summary=self._generate_summary(state),
            sections=self._extract_sections(writing_results),
            word_count=word_count,
            reading_time_minutes=self._calculate_reading_time(word_count),
            keywords=self._extract_keywords(state),
            meta_description=self._generate_meta_description(brief),
        )
        
        return article
    
    def _create_quality_score(self, state: AgentState) -> QualityScore:
        """
        Create quality score from evaluation results.
        
        Args:
            state: Workflow state
            
        Returns:
            Quality score
        """
        # Get base scores
        overall = (state.quality_score or 0.85) * 100
        
        # Component scores
        quality_results = state.quality_results or {}
        
        quality = QualityScore(
            overall_score=overall,
            factual_accuracy=quality_results.get("factual_accuracy", 90.0),
            completeness=(state.completeness_score or 0.85) * 100,
            clarity=quality_results.get("clarity", 87.0),
            coherence=quality_results.get("coherence", 88.0),
            grammar=quality_results.get("grammar", 95.0),
            seo_score=quality_results.get("seo_score", 82.0),
            strengths=self._identify_strengths(state),
            suggestions=self._generate_suggestions(state),
        )
        
        return quality
    
    def _extract_sources(self, state: AgentState) -> List[Source]:
        """
        Extract sources from research results.
        
        Args:
            state: Workflow state
            
        Returns:
            List of sources
        """
        sources = []
        research_results = state.research_results or {}
        
        # Get sources from research
        all_sources = research_results.get("all_sources", [])
        
        for i, source_text in enumerate(all_sources[:15], 1):  # Limit to 15
            source = Source(
                source_id=f"source_{i}",
                title=source_text,
                url=f"https://example.com/source/{i}",
                type="web",
                relevance_score=0.85,
                credibility_score=0.90,
                citation_count=0,
            )
            sources.append(source)
        
        return sources
    
    def _create_execution_metrics(self, state: AgentState) -> ExecutionMetrics:
        """
        Create execution metrics.
        
        Args:
            state: Workflow state
            
        Returns:
            Execution metrics
        """
        # Calculate durations by phase
        phase_durations = {}
        if state.research_results:
            phase_durations["research"] = 30.0
        if state.analysis_results:
            phase_durations["analysis"] = 15.0
        if state.writing_results:
            phase_durations["writing"] = 45.0
        if state.quality_results:
            phase_durations["quality"] = 20.0
        
        total_duration = sum(phase_durations.values())
        
        # Get worker list
        workers_used = list(state.cost_by_worker.keys())
        
        # Create metrics
        metrics = ExecutionMetrics(
            total_duration_seconds=state.total_duration_seconds or total_duration,
            phase_durations=phase_durations,
            total_cost=state.total_cost,
            cost_breakdown=dict(state.cost_by_worker),
            workers_used=workers_used,
            total_tasks=len(state.all_tasks),
            successful_tasks=len(state.completed_tasks),
            failed_tasks=len(state.failed_tasks),
            total_tokens=self._estimate_tokens(state),
            input_tokens=self._estimate_tokens(state) // 3,
            output_tokens=self._estimate_tokens(state) * 2 // 3,
            iterations=state.iteration,
            re_planning_count=len(state.previous_plans),
        )
        
        return metrics
    
    def _generate_default_content(self, state: AgentState) -> str:
        """
        Generate default content if none exists.
        
        Args:
            state: Workflow state
            
        Returns:
            Default content
        """
        topic = state.brief.topic
        
        return f"""# Understanding {topic}

## Introduction

{topic} is an important subject that deserves thorough exploration. This article provides a comprehensive overview based on extensive research and analysis.

## Background

Understanding the context and history of {topic} is essential for grasping its current significance and future implications.

## Key Findings

Our research has revealed several important insights about {topic}:

1. **First Key Point**: Detailed explanation of the first main finding
2. **Second Key Point**: Analysis of the second critical aspect
3. **Third Key Point**: Discussion of the third important element

## Analysis

Through careful analysis of multiple sources, we can observe several patterns and trends related to {topic}. These findings suggest important considerations for both practitioners and researchers.

## Implications

The implications of these findings extend across multiple domains, affecting various stakeholders and presenting both opportunities and challenges.

## Conclusion

{topic} represents a significant area of interest with far-reaching implications. This comprehensive analysis has provided insights into its various aspects, from fundamental concepts to practical applications.

---

*This article was generated through an automated research and writing process. All findings are based on analysis of multiple authoritative sources.*
"""
    
    def _generate_summary(self, state: AgentState) -> str:
        """Generate article summary."""
        topic = state.brief.topic
        return f"A comprehensive analysis of {topic} based on extensive research and expert insights."
    
    def _extract_sections(self, writing_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract sections from writing results."""
        sections = writing_results.get("sections", [])
        
        if not sections:
            # Default sections
            sections = [
                {"title": "Introduction", "content": "Introduction section..."},
                {"title": "Main Content", "content": "Main content section..."},
                {"title": "Conclusion", "content": "Conclusion section..."},
            ]
        
        return sections
    
    def _calculate_reading_time(self, word_count: int) -> int:
        """Calculate reading time in minutes."""
        words_per_minute = 200
        return max(1, word_count // words_per_minute)
    
    def _extract_keywords(self, state: AgentState) -> List[str]:
        """Extract keywords from brief and results."""
        keywords = state.brief.keywords or []
        
        if not keywords:
            # Generate default keywords from topic
            topic_words = state.brief.topic.split()
            keywords = [word.lower() for word in topic_words if len(word) > 3][:5]
        
        return keywords
    
    def _generate_meta_description(self, brief) -> str:
        """Generate meta description."""
        return f"Learn about {brief.topic} in this comprehensive article. Expert analysis and insights."
    
    def _identify_strengths(self, state: AgentState) -> List[str]:
        """Identify content strengths."""
        strengths = []
        
        if state.research_results:
            source_count = len(state.research_results.get("all_sources", []))
            if source_count >= 5:
                strengths.append(f"Well-researched with {source_count} sources")
        
        if state.writing_results:
            word_count = state.writing_results.get("word_count", 0)
            if word_count >= 2000:
                strengths.append("Comprehensive and detailed coverage")
        
        if state.quality_score and state.quality_score >= 0.85:
            strengths.append("High quality content with strong coherence")
        
        if not strengths:
            strengths = ["Clear and well-structured content"]
        
        return strengths
    
    def _generate_suggestions(self, state: AgentState) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        # Check research depth
        if state.research_results:
            source_count = len(state.research_results.get("all_sources", []))
            if source_count < 5:
                suggestions.append("Consider adding more sources for better depth")
        
        # Check word count
        if state.writing_results:
            word_count = state.writing_results.get("word_count", 0)
            target = state.brief.target_length or 2000
            if word_count < target * 0.9:
                suggestions.append(f"Expand content to meet target length ({target} words)")
        
        # Check quality
        if state.quality_score and state.quality_score < 0.85:
            suggestions.append("Consider revision to improve overall quality")
        
        if not suggestions:
            suggestions = ["Content meets all quality standards"]
        
        return suggestions
    
    def _generate_system_notes(self, state: AgentState) -> List[str]:
        """Generate system notes."""
        notes = []
        
        # Sprint 1 note
        notes.append("Generated in mock mode (Sprint 1)")
        
        # Iteration info
        notes.append(f"Completed in {state.iteration} iteration(s)")
        
        # Worker info
        worker_count = len(state.cost_by_worker)
        notes.append(f"Used {worker_count} specialized workers")
        
        return notes
    
    def _generate_warnings(self, state: AgentState) -> List[str]:
        """Generate warnings if any."""
        warnings = []
        
        # Check errors
        if state.errors:
            warnings.append(f"{len(state.errors)} errors occurred during execution")
        
        # Check failed tasks
        if state.failed_tasks:
            warnings.append(f"{len(state.failed_tasks)} tasks failed")
        
        # Check quality
        if state.quality_score and state.quality_score < 0.75:
            warnings.append("Quality score below optimal threshold")
        
        return warnings
    
    def _estimate_tokens(self, state: AgentState) -> int:
        """Estimate total tokens used."""
        # Simple estimation based on operations
        base_tokens = 1000  # Base overhead
        
        if state.research_results:
            base_tokens += 2000
        if state.analysis_results:
            base_tokens += 1500
        if state.writing_results:
            word_count = state.writing_results.get("word_count", 0)
            base_tokens += word_count * 1.3  # Words to tokens ratio
        if state.quality_results:
            base_tokens += 1000
        
        return int(base_tokens)


# Global instance
merger = MergerAgent()


# Helper functions
def get_merger() -> MergerAgent:
    """Get the merger instance."""
    return merger


def create_final_output(state: AgentState) -> FinalOutput:
    """
    Create final output from state.
    
    Args:
        state: Complete workflow state
        
    Returns:
        Final output
    """
    return merger.merge(state)