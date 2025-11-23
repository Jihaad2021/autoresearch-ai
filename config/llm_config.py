"""
LLM client configuration and initialization.
Supports Claude API with mock mode for testing.
"""

import os
from typing import Optional, Dict, Any
from anthropic import Anthropic, AsyncAnthropic
from config.settings import settings


class LLMConfig:
    """LLM configuration and client management."""
    
    def __init__(self):
        """Initialize LLM configuration."""
        self.api_key = settings.anthropic_api_key
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.is_mock = settings.is_mock_mode
        
        # Initialize clients (lazy loading)
        self._client: Optional[Anthropic] = None
        self._async_client: Optional[AsyncAnthropic] = None
    
    @property
    def client(self) -> Anthropic:
        """Get synchronous Anthropic client."""
        if self._client is None:
            if self.is_mock:
                # Mock client for testing
                self._client = None  # Will be handled by mock methods
            else:
                self._client = Anthropic(api_key=self.api_key)
        return self._client
    
    @property
    def async_client(self) -> AsyncAnthropic:
        """Get asynchronous Anthropic client."""
        if self._async_client is None:
            if self.is_mock:
                # Mock client for testing
                self._async_client = None  # Will be handled by mock methods
            else:
                self._async_client = AsyncAnthropic(api_key=self.api_key)
        return self._async_client
    
    def get_default_params(self) -> Dict[str, Any]:
        """Get default LLM parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
    
    def create_message(
        self,
        messages: list,
        system: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Create a message using Claude API (sync).
        
        Args:
            messages: List of message dicts
            system: System prompt
            **kwargs: Additional parameters
            
        Returns:
            API response
        """
        if self.is_mock:
            return self._mock_response(messages, system)
        
        params = self.get_default_params()
        params.update(kwargs)
        
        if system:
            params["system"] = system
        
        return self.client.messages.create(
            messages=messages,
            **params
        )
    
    async def acreate_message(
        self,
        messages: list,
        system: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Create a message using Claude API (async).
        
        Args:
            messages: List of message dicts
            system: System prompt
            **kwargs: Additional parameters
            
        Returns:
            API response
        """
        if self.is_mock:
            return self._mock_response(messages, system)
        
        params = self.get_default_params()
        params.update(kwargs)
        
        if system:
            params["system"] = system
        
        return await self.async_client.messages.create(
            messages=messages,
            **params
        )
    
    def _mock_response(self, messages: list, system: Optional[str] = None) -> Any:
        """Generate mock response for testing."""
        from types import SimpleNamespace
        
        # Extract last user message
        user_msg = next((m for m in reversed(messages) if m["role"] == "user"), {})
        content = user_msg.get("content", "")
        
        # Generate simple mock response
        mock_text = f"Mock response for: {content[:100]}..."
        
        # Mimic Anthropic API response structure
        return SimpleNamespace(
            id="mock_msg_id",
            type="message",
            role="assistant",
            content=[SimpleNamespace(type="text", text=mock_text)],
            model=self.model,
            stop_reason="end_turn",
            usage=SimpleNamespace(input_tokens=100, output_tokens=50)
        )


# Global LLM config instance
llm_config = LLMConfig()


# Convenience functions
def get_llm_config() -> LLMConfig:
    """Get LLM config instance."""
    return llm_config


def reload_llm_config() -> LLMConfig:
    """Reload LLM config."""
    global llm_config
    llm_config = LLMConfig()
    return llm_config