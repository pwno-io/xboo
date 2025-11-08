from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    API_KEY: str
    API_BASE_URL: str = Field(default="http://10.0.0.6:8000")
