"""Configuration management for Scout agent."""

import os
from dataclasses import dataclass, field
from typing import Optional


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
        """Create configuration from environment variables."""
        model = os.getenv("MOONSHOT_MODEL") or os.getenv("OPENAI_MODEL", "moonshot-v1-128k")
        base_url = os.getenv("MOONSHOT_BASE_URL") or os.getenv("OPENAI_BASE_URL", "https://api.moonshot.cn/v1")
        api_key = os.getenv("MOONSHOT_API_KEY") or os.getenv("OPENAI_API_KEY", "")
        
        # Allow customization via environment
        timeout = int(os.getenv("SCOUT_EXECUTION_TIMEOUT", "30"))
        temperature = float(os.getenv("SCOUT_TEMPERATURE", "0.7"))
        
        return cls(
            model_name=model,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
            execution_timeout=timeout,
        )
    
    def is_command_dangerous(self, command: str) -> bool:
        """Check if a command contains dangerous patterns."""
        return any(pattern in command for pattern in self.dangerous_commands)

