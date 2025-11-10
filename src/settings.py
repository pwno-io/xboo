from typing import Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    # langsmith_api_key: Optional[str] = Field(None, validation_alias="LANGSMITH_API_KEY")
    
    # # For local tracing
    # langsmith_endpoint: Optional[str] = Field(None, validation_alias="LANGSMITH_ENDPOINT")
    # langsmith_project: Optional[str] = Field(None, validation_alias="LANGSMITH_PROJECT")
    # langsmith_tracing: Optional[bool] = Field(None, validation_alias="LANGSMITH_TRACING")

    API_KEY: str = Field(default=..., validation_alias=AliasChoices("API_KEY"))
    API_BASE: str = Field(default=..., validation_alias=AliasChoices("API_BASE"))
    MODEL: str = Field(default=..., validation_alias=AliasChoices("MODEL"))

    CHALLENGE_API_KEY: str = Field(default=..., validation_alias=AliasChoices("CHALLENGE_API_KEY"))
    CHALLENGE_API_BASE: str = Field(default=..., validation_alias=AliasChoices("CHALLENGE_API_BASE"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()