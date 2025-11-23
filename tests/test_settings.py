"""Test settings configuration."""
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings, get_settings


def test_settings_loaded():
    """Test that settings load correctly."""
    assert settings is not None
    assert settings.env in ["development", "staging", "production"]
    assert settings.llm_model == "claude-sonnet-4-20250514"
    print("✅ Settings loaded successfully")


def test_is_mock_mode():
    """Test mock mode detection."""
    if settings.anthropic_api_key == "mock_key_sprint_1":
        assert settings.is_mock_mode is True
        print("✅ Mock mode detected correctly")
    else:
        assert settings.is_mock_mode is False
        print("✅ Real API mode detected correctly")


def test_validators():
    """Test that validators work."""
    assert settings.llm_temperature >= 0.0
    assert settings.llm_temperature <= 2.0
    assert settings.llm_max_tokens >= 1  # ← FIXED: was max_tokens
    print("✅ Validators working")


if __name__ == "__main__":
    test_settings_loaded()
    test_is_mock_mode()
    test_validators()
    print("\n✅ All settings tests passed!")