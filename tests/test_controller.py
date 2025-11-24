"""Test Controller Agent."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.meta_agent.controller import ControllerAgent, process_brief
from src.meta_agent.schemas import Brief, ContentType, ToneStyle


def test_controller_initialization():
    """Test controller can be initialized."""
    controller = ControllerAgent()
    assert controller is not None
    assert controller.request_count == 0
    print("✅ Controller initialized")


def test_generate_request_id():
    """Test request ID generation."""
    controller = ControllerAgent()
    
    id1 = controller._generate_request_id()
    id2 = controller._generate_request_id()
    
    assert id1 != id2
    assert id1.startswith("req_")
    assert id2.startswith("req_")
    print(f"✅ Generated unique request IDs: {id1}, {id2}")


def test_initialize_state():
    """Test state initialization."""
    controller = ControllerAgent()
    
    brief = Brief(
        topic="AI trends 2024",
        content_type=ContentType.ARTICLE,
        target_length=2000,
    )
    
    request_id = controller._generate_request_id()
    state = controller._initialize_state(brief, request_id)
    
    assert state.brief.topic == "AI trends 2024"
    assert state.iteration == 1
    assert len(state.agent_history) == 1
    assert state.agent_history[0]["agent"] == "Controller"
    print("✅ State initialized correctly")


def test_execute_workflow():
    """Test full workflow execution."""
    controller = ControllerAgent()
    
    brief = Brief(
        topic="Machine Learning Basics",
        content_type=ContentType.ARTICLE,
        target_length=2000,
        tone=ToneStyle.PROFESSIONAL,
    )
    
    output = controller.execute(brief)
    
    # Check output structure
    assert output is not None
    assert output.article is not None
    assert output.article.title is not None
    assert output.article.word_count == 2000
    assert output.quality.overall_score > 0
    assert output.metrics.total_duration_seconds > 0
    assert output.metrics.total_cost > 0
    
    print("✅ Workflow executed successfully")
    print(f"   Title: {output.article.title}")
    print(f"   Word count: {output.article.word_count}")
    print(f"   Quality: {output.quality.overall_score}/100")
    print(f"   Cost: ${output.metrics.total_cost:.2f}")
    print(f"   Time: {output.metrics.total_duration_seconds:.1f}s")


def test_process_brief_helper():
    """Test process_brief helper function."""
    brief = Brief(
        topic="Python Programming",
        content_type=ContentType.ARTICLE,
    )
    
    output = process_brief(brief)
    
    assert output is not None
    assert "Python Programming" in output.article.title
    print("✅ process_brief() helper works")


def test_mock_article_generation():
    """Test mock article content."""
    controller = ControllerAgent()
    
    brief = Brief(
        topic="Artificial Intelligence",
        content_type=ContentType.ARTICLE,
    )
    
    article_text = controller._generate_mock_article(brief)
    
    assert "Artificial Intelligence" in article_text
    assert "Introduction" in article_text
    assert "Conclusion" in article_text
    assert len(article_text) > 500
    print("✅ Mock article generated")
    print(f"   Length: {len(article_text)} characters")


if __name__ == "__main__":
    test_controller_initialization()
    test_generate_request_id()
    test_initialize_state()
    test_execute_workflow()
    test_process_brief_helper()
    test_mock_article_generation()
    print("\n✅ All Controller tests passed!")