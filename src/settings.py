from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LLM_API_KEY: str = Field(default=..., validation_alias=AliasChoices("API_KEY", "SCOUT_API_KEY", "MOONSHOT_API_KEY", "OPENAI_API_KEY"))
    LLM_API_BASE: str = Field(default=..., validation_alias=AliasChoices("API_BASE", "SCOUT_API_BASE", "MOONSHOT_API_BASE", "OPENAI_API_BASE"))
    LLM_MODEL: str = Field(default=..., validation_alias=AliasChoices("MODEL", "SCOUT_MODEL", "MOONSHOT_MODEL", "OPENAI_MODEL"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()