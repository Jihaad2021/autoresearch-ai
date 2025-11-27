"""Test Merger Agent."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meta_agent.merger import MergerAgent, create_final_output
from src.meta_agent.schemas import (
    Brief,
    ContentType,
    AgentState,
)


def test_merger_initialization():
    """Test merger initialization."""
    merger = MergerAgent()
    assert merger is not None
    assert merger.merge_count == 0
    print("✅ Merger initialized")


def test_merge_complete_results():
    """Test merging complete results."""
    merger = MergerAgent()
    
    brief = Brief(
        topic="Artificial Intelligence",
        content_type=ContentType.ARTICLE,
        target_length=2000,
    )
    
    state = AgentState(brief=brief)
    
    # Add complete results
    state.research_results = {
        "all_sources": [
            "Source 1 about AI",
            "Source 2 about AI",
            "Source 3 about AI",
            "Source 4 about AI",
            "Source 5 about AI",
        ],
        "total_workers": 2,
        "successful_workers": 2,
    }
    
    state.writing_results = {
        "content": "Article content about AI..." * 100,
        "word_count": 2000,
        "sections": [
            {"title": "Introduction", "content": "Intro..."},
            {"title": "Main", "content": "Main..."},
            {"title": "Conclusion", "content": "Conclusion..."},
        ]
    }
    
    state.quality_results = {
        "average_quality": 88.0,
    }
    
    state.quality_score = 0.88
    state.completeness_score = 0.95
    
    # Add costs properly
    state.add_cost("web_search_worker", 0.02)
    state.add_cost("article_writer_worker", 0.08)
    state.add_cost("fact_checker_worker", 0.05)
    # Total = 0.15
    
    # Merge
    output = merger.merge(state)
    
    # Verify output
    assert output is not None
    assert output.brief_topic == "Artificial Intelligence"
    assert output.article is not None
    assert output.article.word_count == 2000
    assert output.quality is not None
    assert output.quality.overall_score > 0
    assert output.source_count == 5
    assert len(output.sources) == 5
    assert output.metrics is not None
    
    # Use approximate comparison for float
    assert abs(output.metrics.total_cost - 0.15) < 0.01  # ← FIXED
    
    print("✅ Complete results merged")
    print(f"   Article: {output.article.word_count} words")
    print(f"   Quality: {output.quality.overall_score:.0f}/100")
    print(f"   Sources: {output.source_count}")
    print(f"   Cost: ${output.metrics.total_cost:.2f}")

def test_merge_minimal_results():
    """Test merging minimal results."""
    merger = MergerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Minimal results
    state.research_results = {"all_sources": ["Source 1"]}
    state.quality_score = 0.75
    
    # Merge
    output = merger.merge(state)
    
    # Should still create valid output
    assert output is not None
    assert output.article is not None
    assert output.article.content is not None
    assert len(output.article.content) > 0
    
    print("✅ Minimal results merged")
    print(f"   Has default content: {len(output.article.content) > 500}")


def test_create_article():
    """Test article creation."""
    merger = MergerAgent()
    
    brief = Brief(topic="Python", content_type=ContentType.ARTICLE, target_length=1500)
    state = AgentState(brief=brief)
    
    state.writing_results = {
        "content": "Python programming content...",
        "word_count": 1500,
    }
    
    article = merger._create_article(state)
    
    assert article is not None
    assert "Python" in article.title
    assert article.word_count == 1500
    assert article.reading_time_minutes > 0
    assert len(article.keywords) > 0
    
    print("✅ Article creation works")
    print(f"   Title: {article.title}")
    print(f"   Words: {article.word_count}")
    print(f"   Reading time: {article.reading_time_minutes} min")


def test_create_quality_score():
    """Test quality score creation."""
    merger = MergerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    state.quality_score = 0.85
    state.completeness_score = 0.90
    state.quality_results = {
        "average_quality": 88.0,
        "factual_accuracy": 92.0,
    }
    
    quality = merger._create_quality_score(state)
    
    assert quality is not None
    assert quality.overall_score == 85.0
    assert quality.completeness == 90.0
    assert quality.factual_accuracy == 92.0
    assert len(quality.strengths) > 0
    
    print("✅ Quality score creation works")
    print(f"   Overall: {quality.overall_score:.0f}/100")
    print(f"   Completeness: {quality.completeness:.0f}/100")


def test_extract_sources():
    """Test source extraction."""
    merger = MergerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    state.research_results = {
        "all_sources": [f"Source {i}" for i in range(1, 11)]  # 10 sources
    }
    
    sources = merger._extract_sources(state)
    
    assert len(sources) == 10
    assert all(s.source_id.startswith("source_") for s in sources)
    assert all(s.relevance_score > 0 for s in sources)
    
    print("✅ Source extraction works")
    print(f"   Sources: {len(sources)}")


def test_create_execution_metrics():
    """Test execution metrics creation."""
    merger = MergerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    state.research_results = {}
    state.writing_results = {}
    state.quality_results = {}
    state.add_cost("worker1", 0.05)
    state.add_cost("worker2", 0.07)
    state.iteration = 2
    
    metrics = merger._create_execution_metrics(state)
    
    assert metrics is not None
    assert abs(metrics.total_cost - 0.12) < 0.01  # ← CHANGED: Use approximate comparison
    assert len(metrics.workers_used) == 2
    assert metrics.iterations == 2
    assert metrics.total_tokens > 0
    
    print("✅ Execution metrics creation works")
    print(f"   Cost: ${metrics.total_cost:.2f}")
    print(f"   Workers: {len(metrics.workers_used)}")
    print(f"   Iterations: {metrics.iterations}")

def test_generate_system_notes():
    """Test system notes generation."""
    merger = MergerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    state.iteration = 2
    state.add_cost("worker1", 0.05)
    state.add_cost("worker2", 0.03)
    
    notes = merger._generate_system_notes(state)
    
    assert len(notes) > 0
    assert any("Sprint 1" in note for note in notes)
    assert any("iteration" in note.lower() for note in notes)
    
    print("✅ System notes generation works")
    print(f"   Notes: {len(notes)}")


def test_generate_warnings():
    """Test warnings generation."""
    merger = MergerAgent()
    
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    # Add some issues
    state.add_error("Test error")
    state.quality_score = 0.70  # Low quality
    
    warnings = merger._generate_warnings(state)
    
    assert len(warnings) > 0
    assert any("error" in w.lower() for w in warnings)
    assert any("quality" in w.lower() for w in warnings)
    
    print("✅ Warnings generation works")
    print(f"   Warnings: {len(warnings)}")


def test_helper_function():
    """Test create_final_output helper."""
    brief = Brief(topic="Test", content_type=ContentType.ARTICLE)
    state = AgentState(brief=brief)
    
    state.research_results = {"all_sources": ["S1", "S2"]}
    state.quality_score = 0.85
    
    output = create_final_output(state)
    
    assert output is not None
    assert output.article is not None
    
    print("✅ Helper function works")


if __name__ == "__main__":
    test_merger_initialization()
    test_merge_complete_results()
    test_merge_minimal_results()
    test_create_article()
    test_create_quality_score()
    test_extract_sources()
    test_create_execution_metrics()
    test_generate_system_notes()
    test_generate_warnings()
    test_helper_function()
    print("\n✅ All Merger tests passed!")