from typing import List, Optional

import httpx
from pydantic import BaseModel

from .config import Config


# Response Models
class TargetInfo(BaseModel):
    ip: str
    port: List[int]


class Challenge(BaseModel):
    challenge_code: str
    difficulty: str
    points: int
    hint_viewed: bool
    solved: bool
    target_info: TargetInfo


class ChallengesResponse(BaseModel):
    current_stage: str  # "debug" or "competition"
    challenges: List[Challenge]


class HintResponse(BaseModel):
    hint_content: str
    penalty_points: int
    first_use: bool


class AnswerRequest(BaseModel):
    challenge_code: str
    answer: str


class AnswerResponse(BaseModel):
    correct: bool
    earned_points: int
    is_solved: bool


class ErrorResponse(BaseModel):
    detail: str


# API Client
class ProblemAPIClient:
    def __init__(self, config: Optional[Config] = None):
        """Initialize the API client with configuration.

        Args:
            config: Optional Config object. If None, will load from environment.
        """
        self.config = config or Config()
        self.base_url = self.config.API_BASE_URL
        self.api_key = self.config.API_KEY
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"accept": "application/json", "Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the httpx client."""
        if self.client is None:
            raise RuntimeError(
                "Client not initialized. Use 'async with ProblemAPIClient()' context manager."
            )
        return self.client

    async def get_challenges(self) -> ChallengesResponse:
        """Get the list of available challenges.

        Returns:
            ChallengesResponse with current stage and list of challenges.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        client = self._get_client()
        response = await client.get("/api/v1/challenges")
        response.raise_for_status()
        return ChallengesResponse.model_validate(response.json())

    async def get_hint(self, challenge_code: str) -> HintResponse:
        """Get a hint for a specific challenge.

        Args:
            challenge_code: The code of the challenge to get hint for.

        Returns:
            HintResponse with hint content, penalty points, and first use flag.

        Raises:
            httpx.HTTPStatusError: If the request fails (e.g., 500 if challenge doesn't exist).
        """
        client = self._get_client()
        response = await client.get(f"/api/v1/hint/{challenge_code}")
        response.raise_for_status()
        return HintResponse.model_validate(response.json())

    async def submit_answer(self, challenge_code: str, answer: str) -> AnswerResponse:
        """Submit an answer for a challenge.

        Args:
            challenge_code: The code of the challenge.
            answer: The answer/flag to submit.

        Returns:
            AnswerResponse with correctness, earned points, and solved status.

        Raises:
            httpx.HTTPStatusError: If the request fails (e.g., 500 if challenge doesn't exist).
        """
        client = self._get_client()
        request_data = AnswerRequest(challenge_code=challenge_code, answer=answer)
        response = await client.post("/api/v1/answer", json=request_data.model_dump())
        response.raise_for_status()
        return AnswerResponse.model_validate(response.json())


# Convenience function for one-off requests
async def get_challenges(config: Optional[Config] = None) -> ChallengesResponse:
    """Convenience function to get challenges without managing client lifecycle."""
    async with ProblemAPIClient(config) as client:
        return await client.get_challenges()


async def get_hint(challenge_code: str, config: Optional[Config] = None) -> HintResponse:
    """Convenience function to get hint without managing client lifecycle."""
    async with ProblemAPIClient(config) as client:
        return await client.get_hint(challenge_code)


async def submit_answer(
    challenge_code: str, answer: str, config: Optional[Config] = None
) -> AnswerResponse:
    """Convenience function to submit answer without managing client lifecycle."""
    async with ProblemAPIClient(config) as client:
        return await client.submit_answer(challenge_code, answer)
