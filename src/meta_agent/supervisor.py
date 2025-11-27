"""
Supervisor Agent - Evaluates quality and decides next action.

The Supervisor is responsible for:
1. Evaluating execution results
2. Calculating quality scores
3. Deciding whether to continue or complete
4. Providing feedback for improvement
5. Identifying quality issues
6. Recommending next steps
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from typing import Dict, Any, List, Tuple
from datetime import datetime

from src.meta_agent.schemas import (
    AgentState,
    WorkflowPhase,
)


class SupervisorAgent:
    """
    Supervisor Agent - Quality evaluation and decision making.
    
    The Supervisor evaluates the quality of execution results
    and decides whether the workflow should continue iterating
    or complete.
    """
    
    def __init__(self):
        """Initialize supervisor."""
        self.evaluation_count = 0
        
        # Quality thresholds
        self.quality_threshold = 0.80  # 80%
        self.completeness_threshold = 0.75  # 75%
        self.min_sources = 5
    
    def evaluate(self, state: AgentState) -> Tuple[bool, str]:
        """
        Evaluate execution results and decide next action.
        
        Args:
            state: Current workflow state
            
        Returns:
            Tuple of (should_continue, feedback)
            - should_continue: True = iterate again, False = complete
            - feedback: Feedback for improvement
        """
        print(f"\n{'='*60}")
        print(f"🔍 Supervisor: Evaluating results")
        print(f"{'='*60}")
        
        self.evaluation_count += 1
        
        # Calculate quality scores
        quality_score = self._calculate_quality_score(state)
        completeness_score = self._calculate_completeness_score(state)
        
        # Store in state
        state.quality_score = quality_score
        state.completeness_score = completeness_score
        
        print(f"\n📊 Quality Metrics:")
        print(f"   Quality Score: {quality_score:.1%}")
        print(f"   Completeness Score: {completeness_score:.1%}")
        print(f"   Quality Threshold: {self.quality_threshold:.1%}")
        print(f"   Completeness Threshold: {self.completeness_threshold:.1%}")
        
        # Check iteration limit
        if state.iteration >= state.max_iterations:
            print(f"\n⚠️  Max iterations reached ({state.max_iterations})")
            decision = False
            feedback = "Maximum iterations reached. Completing with current results."
        
        # Evaluate quality
        elif quality_score >= self.quality_threshold and completeness_score >= self.completeness_threshold:
            print(f"\n✅ Quality acceptable!")
            decision = False
            feedback = "Quality and completeness meet thresholds. Ready to complete."
        
        else:
            print(f"\n⚠️  Quality below threshold")
            decision = True
            feedback = self._generate_feedback(state, quality_score, completeness_score)
        
        # Update state
        state.should_continue = decision
        state.supervisor_feedback = feedback
        
        # Record evaluation
        state.add_agent_action(
            agent_name="Supervisor",
            action="evaluate",
            details={
                "quality_score": quality_score,
                "completeness_score": completeness_score,
                "decision": "CONTINUE" if decision else "COMPLETE",
                "iteration": state.iteration,
            }
        )
        
        print(f"\n🎯 Decision: {'CONTINUE (iterate again)' if decision else 'COMPLETE (done)'}")
        print(f"📝 Feedback: {feedback}")
        print(f"{'='*60}\n")
        
        return decision, feedback
    
    def _calculate_quality_score(self, state: AgentState) -> float:
        """
        Calculate overall quality score.
        
        Args:
            state: Current workflow state
            
        Returns:
            Quality score (0.0 to 1.0)
        """
        scores = []
        
        # Research quality
        if state.research_results:
            research_score = self._evaluate_research(state.research_results)
            scores.append(research_score)
        
        # Analysis quality
        if state.analysis_results:
            analysis_score = self._evaluate_analysis(state.analysis_results)
            scores.append(analysis_score)
        
        # Writing quality
        if state.writing_results:
            writing_score = self._evaluate_writing(state.writing_results)
            scores.append(writing_score)
        
        # Quality check results
        if state.quality_results:
            quality_check_score = self._evaluate_quality_check(state.quality_results)
            scores.append(quality_check_score)
        
        # If no scores, return 0
        if not scores:
            return 0.0
        
        # Average all scores
        return sum(scores) / len(scores)
    
    def _calculate_completeness_score(self, state: AgentState) -> float:
        """
        Calculate completeness score.
        
        Args:
            state: Current workflow state
            
        Returns:
            Completeness score (0.0 to 1.0)
        """
        required_components = {
            "research_results": state.research_results is not None,
            "writing_results": state.writing_results is not None,
        }
        
        # Count completed components
        completed = sum(1 for v in required_components.values() if v)
        total = len(required_components)
        
        # Calculate percentage
        completeness = completed / total if total > 0 else 0.0
        
        # Bonus for optional components
        if state.analysis_results:
            completeness += 0.1
        if state.quality_results:
            completeness += 0.1
        
        # Cap at 1.0
        return min(completeness, 1.0)
    
    def _evaluate_research(self, research_results: Dict[str, Any]) -> float:
        """
        Evaluate research quality.
        
        Args:
            research_results: Research results
            
        Returns:
            Research quality score (0.0 to 1.0)
        """
        score = 0.5  # Base score
        
        # Check number of sources
        if "all_sources" in research_results:
            source_count = len(research_results["all_sources"])
            if source_count >= self.min_sources:
                score += 0.3
            elif source_count >= 3:
                score += 0.2
            else:
                score += 0.1
        
        # Check successful workers
        if "successful_workers" in research_results:
            success_rate = research_results.get("successful_workers", 0) / max(research_results.get("total_workers", 1), 1)
            score += success_rate * 0.2
        
        return min(score, 1.0)
    
    def _evaluate_analysis(self, analysis_results: Dict[str, Any]) -> float:
        """
        Evaluate analysis quality.
        
        Args:
            analysis_results: Analysis results
            
        Returns:
            Analysis quality score (0.0 to 1.0)
        """
        score = 0.6  # Base score
        
        # Check if insights exist
        if "key_insights" in analysis_results:
            insight_count = len(analysis_results.get("key_insights", []))
            if insight_count >= 3:
                score += 0.3
            elif insight_count >= 1:
                score += 0.2
        
        # Check confidence
        if "confidence" in analysis_results:
            avg_confidence = analysis_results.get("confidence", 0)
            score += avg_confidence * 0.1
        
        return min(score, 1.0)
    
    def _evaluate_writing(self, writing_results: Dict[str, Any]) -> float:
        """
        Evaluate writing quality.
        
        Args:
            writing_results: Writing results
            
        Returns:
            Writing quality score (0.0 to 1.0)
        """
        score = 0.6  # Base score
        
        # Check if content exists
        if "content" in writing_results:
            content = writing_results.get("content", "")
            if len(content) > 1000:
                score += 0.2
            elif len(content) > 500:
                score += 0.1
        
        # Check word count
        if "word_count" in writing_results:
            word_count = writing_results.get("word_count", 0)
            if word_count >= 1500:
                score += 0.2
            elif word_count >= 1000:
                score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_quality_check(self, quality_results: Dict[str, Any]) -> float:
        """
        Evaluate quality check results.
        
        Args:
            quality_results: Quality check results
            
        Returns:
            Quality check score (0.0 to 1.0)
        """
        # Use average quality if available
        if "average_quality" in quality_results:
            return quality_results["average_quality"] / 100.0
        
        # Otherwise use base score
        return 0.8
    
    def _generate_feedback(
        self,
        state: AgentState,
        quality_score: float,
        completeness_score: float
    ) -> str:
        """
        Generate feedback for improvement.
        
        Args:
            state: Current state
            quality_score: Quality score
            completeness_score: Completeness score
            
        Returns:
            Feedback message
        """
        issues = []
        
        # Quality issues
        if quality_score < self.quality_threshold:
            gap = self.quality_threshold - quality_score
            issues.append(f"Quality {gap:.1%} below threshold")
            
            # Specific issues
            if state.research_results:
                source_count = len(state.research_results.get("all_sources", []))
                if source_count < self.min_sources:
                    issues.append(f"Need {self.min_sources - source_count} more sources")
            
            if state.writing_results:
                word_count = state.writing_results.get("word_count", 0)
                target = state.brief.target_length or 2000
                if word_count < target * 0.9:
                    issues.append(f"Article too short ({word_count}/{target} words)")
        
        # Completeness issues
        if completeness_score < self.completeness_threshold:
            if not state.research_results:
                issues.append("Missing research results")
            if not state.writing_results:
                issues.append("Missing writing results")
            if not state.analysis_results:
                issues.append("Consider adding analysis step")
        
        # Generate feedback message
        if issues:
            return "; ".join(issues) + ". Re-plan and improve."
        else:
            return "Minor improvements needed. Re-plan for better quality."
    
    def get_quality_report(self, state: AgentState) -> Dict[str, Any]:
        """
        Generate detailed quality report.
        
        Args:
            state: Current workflow state
            
        Returns:
            Quality report
        """
        report = {
            "overall_quality": state.quality_score or 0.0,
            "completeness": state.completeness_score or 0.0,
            "iteration": state.iteration,
            "max_iterations": state.max_iterations,
            "should_continue": state.should_continue,
            "feedback": state.supervisor_feedback,
            "components": {
                "research": state.research_results is not None,
                "analysis": state.analysis_results is not None,
                "writing": state.writing_results is not None,
                "quality_check": state.quality_results is not None,
            },
            "metrics": {
                "total_cost": state.total_cost,
                "total_tasks": len(state.all_tasks),
                "completed_tasks": len(state.completed_tasks),
                "failed_tasks": len(state.failed_tasks),
                "errors": len(state.errors),
            }
        }
        
        return report


# Global instance
supervisor = SupervisorAgent()


# Helper functions
def get_supervisor() -> SupervisorAgent:
    """Get the supervisor instance."""
    return supervisor


def evaluate_results(state: AgentState) -> Tuple[bool, str]:
    """
    Evaluate execution results.
    
    Args:
        state: Current workflow state
        
    Returns:
        Tuple of (should_continue, feedback)
    """
    return supervisor.evaluate(state)