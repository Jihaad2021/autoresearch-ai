"""
Centralized configuration management for AutoResearch AI.
All settings loaded from environment variables with validation.
"""

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Environment
    env: str = Field(default="development", description="Environment: development, staging, production")
    debug: bool = Field(default=True, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # LLM Configuration
    anthropic_api_key: str = Field(default="mock_key_sprint_1", description="Anthropic API key")
    llm_model: str = Field(default="claude-sonnet-4-20250514", description="Default LLM model")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    llm_max_tokens: int = Field(default=4096, ge=1, le=200000, description="Max tokens for LLM")
    
    # Search Tools
    tavily_api_key: str = Field(default="mock_key_sprint_1", description="Tavily API key")
    serper_api_key: str = Field(default="mock_key_sprint_1", description="Serper API key")
    news_api_key: str = Field(default="mock_key_sprint_1", description="News API key")
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/autoresearch",
        description="PostgreSQL database URL"
    )
    
    # Cache
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis cache URL"
    )
    cache_ttl: int = Field(default=3600, ge=0, description="Cache TTL in seconds")
    
    # Monitoring
    langsmith_api_key: str = Field(default="mock_key_sprint_1", description="LangSmith API key")
    langsmith_project: str = Field(default="autoresearch-ai", description="LangSmith project name")
    langsmith_tracing_v2: bool = Field(default=False, description="Enable LangSmith tracing")
    
    # Application Settings
    max_iterations: int = Field(default=3, ge=1, le=10, description="Max iterations for re-planning")
    default_timeout: int = Field(default=300, ge=10, description="Default timeout in seconds")
    max_concurrent_tasks: int = Field(default=5, ge=1, le=20, description="Max concurrent tasks")
    
    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, ge=1024, le=65535, description="API port")
    api_reload: bool = Field(default=True, description="Auto-reload on code changes")
    
    # UI Settings
    ui_host: str = Field(default="0.0.0.0", description="UI host")
    ui_port: int = Field(default=8501, ge=1024, le=65535, description="UI port")
    
    @field_validator("env")
    @classmethod
    def validate_env(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v.lower() not in allowed:
            raise ValueError(f"env must be one of {allowed}")
        return v.lower()
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}")
        return v.upper()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.env == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.env == "production"
    
    @property
    def is_mock_mode(self) -> bool:
        """Check if using mock API keys."""
        return self.anthropic_api_key == "mock_key_sprint_1"


# Global settings instance
settings = Settings()


# Convenience functions
def get_settings() -> Settings:
    """Get settings instance."""
    return settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global settings
    settings = Settings()
    return settings