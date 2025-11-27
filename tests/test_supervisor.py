"""Test Supervisor Agent."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meta_agent.supervisor import SupervisorAgent, evaluate_results
from src.meta_agent.schemas import (
    Brief,
    ContentType,
    AgentState,
)


def test_supervisor_initialization():
    """Test supervisor initialization."""
    supervisor = SupervisorAgent()
    assert supervisor is not None
    assert supervisor.quality_threshold == 0.80
    assert supervisor.completeness_threshold == 0.75
    assert supervisor.evaluation_count == 0
    print("✅ Supervisor initialized")


def test_evaluate_high_quality():
    """Test evaluation with high quality results."""
    supervisor = SupervisorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Mock high quality results
    state.research_results = {
        "all_sources": ["S1", "S2", "S3", "S4", "S5", "S6"],
        "total_workers": 2,
        "successful_workers": 2,
    }
    
    state.writing_results = {
        "content": "A" * 1500,
        "word_count": 2000,
    }
    
    state.quality_results = {
        "average_quality": 88.0,
    }
    
    # Evaluate
    should_continue, feedback = supervisor.evaluate(state)
    
    # Should complete (high quality)
    assert should_continue == False
    assert state.quality_score >= supervisor.quality_threshold
    assert state.completeness_score >= supervisor.completeness_threshold
    
    print("✅ High quality evaluation works")
    print(f"   Quality: {state.quality_score:.1%}")
    print(f"   Completeness: {state.completeness_score:.1%}")
    print(f"   Decision: COMPLETE")


def test_evaluate_low_quality():
    """Test evaluation with low quality results."""
    supervisor = SupervisorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Mock low quality results
    state.research_results = {
        "all_sources": ["S1", "S2"],  # Only 2 sources (need 5)
        "total_workers": 2,
        "successful_workers": 1,
    }
    
    state.writing_results = {
        "content": "Short content",
        "word_count": 500,  # Too short
    }
    
    # Evaluate
    should_continue, feedback = supervisor.evaluate(state)
    
    # Should continue (low quality)
    assert should_continue == True
    assert state.quality_score < supervisor.quality_threshold or \
           state.completeness_score < supervisor.completeness_threshold
    assert "sources" in feedback.lower() or "short" in feedback.lower()
    
    print("✅ Low quality evaluation works")
    print(f"   Quality: {state.quality_score:.1%}")
    print(f"   Decision: CONTINUE")
    print(f"   Feedback: {feedback}")


def test_evaluate_incomplete():
    """Test evaluation with incomplete results."""
    supervisor = SupervisorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Only research, no writing
    state.research_results = {
        "all_sources": ["S1", "S2"],  # Few sources
    }
    # No writing_results!
    
    # Evaluate
    should_continue, feedback = supervisor.evaluate(state)
    
    # Should continue (incomplete - missing writing)
    assert should_continue == True
    
    # Verify it's because of low quality (no writing = low score)
    assert state.quality_score < supervisor.quality_threshold
    
    # Check feedback mentions the issue
    feedback_lower = feedback.lower()
    assert any(keyword in feedback_lower for keyword in ["quality", "sources", "threshold"])
    
    print("✅ Incomplete evaluation works")
    print(f"   Quality: {state.quality_score:.1%}")
    print(f"   Completeness: {state.completeness_score:.1%}")
    print(f"   Decision: CONTINUE")
    print(f"   Feedback: {feedback}")


def test_max_iterations():
    """Test max iterations limit."""
    supervisor = SupervisorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief, max_iterations=2)
    
    # Set to max iterations
    state.iteration = 2
    
    # Mock low quality (would normally continue)
    state.research_results = {"all_sources": ["S1"]}
    state.writing_results = {"content": "Short", "word_count": 100}
    
    # Evaluate
    should_continue, feedback = supervisor.evaluate(state)
    
    # Should complete (max iterations reached)
    assert should_continue == False
    assert "maximum" in feedback.lower() or "iterations" in feedback.lower()
    
    print("✅ Max iterations check works")
    print(f"   Iteration: {state.iteration}/{state.max_iterations}")
    print(f"   Decision: COMPLETE (max reached)")


def test_quality_score_calculation():
    """Test quality score calculation."""
    supervisor = SupervisorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Add results
    state.research_results = {
        "all_sources": ["S1", "S2", "S3", "S4", "S5"],
        "total_workers": 2,
        "successful_workers": 2,
    }
    
    state.writing_results = {
        "content": "A" * 2000,
        "word_count": 2000,
    }
    
    score = supervisor._calculate_quality_score(state)
    
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Should be decent with good results
    
    print("✅ Quality score calculation works")
    print(f"   Score: {score:.1%}")


def test_completeness_score_calculation():
    """Test completeness score calculation."""
    supervisor = SupervisorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Add required components
    state.research_results = {"sources": []}
    state.writing_results = {"content": "text"}
    
    # Add optional components
    state.analysis_results = {"insights": []}
    state.quality_results = {"score": 85}
    
    score = supervisor._calculate_completeness_score(state)
    
    assert 0.0 <= score <= 1.0
    assert score >= 1.0  # Should be 100% or more (capped at 1.0)
    
    print("✅ Completeness score calculation works")
    print(f"   Score: {score:.1%}")


def test_quality_report():
    """Test quality report generation."""
    supervisor = SupervisorAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Add results
    state.research_results = {"sources": []}
    state.writing_results = {"content": "text"}
    state.quality_score = 0.85
    state.completeness_score = 0.90
    state.should_continue = False
    state.supervisor_feedback = "Good quality"
    
    report = supervisor.get_quality_report(state)
    
    assert "overall_quality" in report
    assert "completeness" in report
    assert "components" in report
    assert "metrics" in report
    assert report["overall_quality"] == 0.85
    
    print("✅ Quality report generation works")
    print(f"   Overall quality: {report['overall_quality']:.1%}")
    print(f"   Components: {sum(report['components'].values())}/4")


def test_helper_function():
    """Test evaluate_results helper."""
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # High quality results
    state.research_results = {"all_sources": ["S1", "S2", "S3", "S4", "S5"]}
    state.writing_results = {"content": "A" * 2000, "word_count": 2000}
    
    should_continue, feedback = evaluate_results(state)
    
    assert isinstance(should_continue, bool)
    assert isinstance(feedback, str)
    
    print("✅ Helper function works")


if __name__ == "__main__":
    test_supervisor_initialization()
    test_evaluate_high_quality()
    test_evaluate_low_quality()
    test_evaluate_incomplete()
    test_max_iterations()
    test_quality_score_calculation()
    test_completeness_score_calculation()
    test_quality_report()
    test_helper_function()
    print("\n✅ All Supervisor tests passed!")