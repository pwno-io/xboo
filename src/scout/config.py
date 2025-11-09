"""Configuration management for Scout agent."""

from dataclasses import dataclass, field
from typing import Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

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

