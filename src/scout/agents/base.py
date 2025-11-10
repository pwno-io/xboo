from langchain_openai import ChatOpenAI

from src.settings import settings


class BaseAgent:
    def __init__(self):
        self.model: ChatOpenAI = ChatOpenAI(
            model=settings.MODEL,
            # base_url=settings.API_BASE,
            api_key=settings.API_KEY,
            max_retries=5,
        )