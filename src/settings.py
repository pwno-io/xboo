from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_KEY: str = Field(default=..., validation_alias=AliasChoices("API_KEY", "SCOUT_API_KEY", "MOONSHOT_API_KEY", "OPENAI_API_KEY"))
    API_BASE: str = Field(default=..., validation_alias=AliasChoices("API_BASE", "SCOUT_API_BASE", "MOONSHOT_API_BASE", "OPENAI_API_BASE"))
    MODEL: str = Field(default=..., validation_alias=AliasChoices("MODEL", "SCOUT_MODEL", "MOONSHOT_MODEL", "OPENAI_MODEL"))

    CHALLENGE_API_KEY: str = Field(default=..., validation_alias=AliasChoices("CHALLENGE_API_KEY"))
    CHALLENGE_API_BASE: str = Field(default=..., validation_alias=AliasChoices("CHALLENGE_API_BASE"))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()