"""Test LLM configuration."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.llm_config import llm_config, get_llm_config


def test_llm_config_loaded():
    """Test LLM config loads correctly."""
    assert llm_config is not None
    assert llm_config.model == "claude-sonnet-4-20250514"
    print("✅ LLM config loaded")


def test_mock_mode():
    """Test mock mode."""
    if llm_config.is_mock:
        print("✅ Running in mock mode (no API calls)")
    else:
        print("⚠️  Running with real API (test will skip API call)")


def test_mock_response():
    """Test mock response generation."""
    # Only test if in mock mode
    if not llm_config.is_mock:
        print("⚠️  Skipping API test (real API key detected)")
        return
    
    messages = [{"role": "user", "content": "Hello, Claude!"}]
    response = llm_config.create_message(messages)
    
    assert response is not None
    assert hasattr(response, "content")
    assert len(response.content) > 0
    print(f"✅ Mock response: {response.content[0].text}")


def test_default_params():
    """Test default parameters."""
    params = llm_config.get_default_params()
    assert "model" in params
    assert "temperature" in params
    assert "max_tokens" in params
    print(f"✅ Default params: {params}")


def test_mock_method_directly():
    """Test _mock_response method directly."""
    messages = [{"role": "user", "content": "Test message"}]
    response = llm_config._mock_response(messages)
    
    assert response is not None
    assert hasattr(response, "content")
    print(f"✅ Mock method works: {response.content[0].text[:50]}...")


if __name__ == "__main__":
    test_llm_config_loaded()
    test_mock_mode()
    test_mock_response()
    test_default_params()
    test_mock_method_directly()
    print("\n✅ All LLM config tests passed!")