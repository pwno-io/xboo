"""Configuration management for Scout agent."""

from dataclasses import dataclass, field
from typing import Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScoutSettings(BaseSettings):
    """Settings loaded from environment/.env with sensible fallbacks.
    
    Supports multiple provider env names via aliases:
    - SCOUT_* (preferred by this project)
    - MOONSHOT_*
    - OPENAI_*
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",
    )

    # Model configuration (prefer SCOUT_*, then MOONSHOT_*, then OPENAI_*)
    model_name: str = Field(
        default="moonshot-v1-128k",
        validation_alias=AliasChoices("SCOUT_MODEL", "MOONSHOT_MODEL", "OPENAI_MODEL"),
    )
    base_url: str = Field(
        default="https://api.moonshot.cn/v1",
        validation_alias=AliasChoices("SCOUT_BASE_URL", "MOONSHOT_BASE_URL", "OPENAI_BASE_URL"),
    )
    api_key: str = Field(
        default="",
        validation_alias=AliasChoices("SCOUT_API_KEY", "MOONSHOT_API_KEY", "OPENAI_API_KEY"),
    )
    temperature: float = Field(
        default=0.7,
        validation_alias=AliasChoices("SCOUT_TEMPERATURE"),
    )

    # Tool execution safety settings
    execution_timeout: int = Field(
        default=30,  # seconds
        validation_alias=AliasChoices("SCOUT_EXECUTION_TIMEOUT"),
    )
    max_output_size: int = 100000  # bytes

    # Dangerous command patterns to block
    dangerous_commands: list[str] = Field(
        default_factory=lambda: [
            "rm -rf /",
            "dd if=",
            "mkfs",
            ":(){ :|:& };:",
            "> /dev/sda",
            "mv /* /dev/null",
        ]
    )


@dataclass
class ScoutConfig:
    """Configuration for Scout agent and its components."""
    
    # Model configuration
    model_name: str
    base_url: str
    api_key: str
    temperature: float = 0.7
    
    # Tool execution safety settings
    execution_timeout: int = 30  # seconds
    max_output_size: int = 100000  # bytes
    
    # Dangerous command patterns to block
    dangerous_commands: list[str] = field(default_factory=lambda: [
        "rm -rf /",
        "dd if=",
        "mkfs",
        ":(){ :|:& };:", 
        "> /dev/sda",
        "mv /* /dev/null",
    ])
    
    @classmethod
    def from_env(cls) -> "ScoutConfig":
        """Create configuration from environment variables and .env automatically."""
        s = ScoutSettings()
        print("TEST:", s.model_name, s.base_url, s.api_key, s.temperature, s.execution_timeout)
        return cls(
            model_name=s.model_name,
            base_url=s.base_url,
            api_key=s.api_key,
            temperature=s.temperature,
            execution_timeout=s.execution_timeout,
        )
    
    def is_command_dangerous(self, command: str) -> bool:
        """Check if a command contains dangerous patterns."""
        return any(pattern in command for pattern in self.dangerous_commands)

