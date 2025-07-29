import uuid
from typing import TYPE_CHECKING, List, Optional, Dict

from .models import (
    QualGenerationRequest,
    QualGenerationResponse,
    MCGenerationRequest,
    MCGenerationResponse,
    SurveySessionCloseResponse,
    AddContextRequest,
    AddContextResponse,
    SurveySessionDetailResponse,
)

if TYPE_CHECKING:
    from .client import Simile


class Agent:
    """Represents an agent and provides methods for interacting with it directly."""

    def __init__(self, agent_id: uuid.UUID, client: "Simile"):
        self._agent_id = agent_id
        self._client = client

    @property
    def id(self) -> uuid.UUID:
        return self._agent_id

    async def generate_qual_response(
        self, question: str, images: Optional[Dict[str, str]] = None
    ) -> QualGenerationResponse:
        """Generates a qualitative response from this agent based on a question."""
        return await self._client.generate_qual_response(
            agent_id=self._agent_id, question=question, images=images
        )

    async def generate_mc_response(
        self, question: str, options: List[str], images: Optional[Dict[str, str]] = None
    ) -> MCGenerationResponse:
        """Generates a multiple-choice response from this agent."""
        return await self._client.generate_mc_response(
            agent_id=self._agent_id,
            question=question,
            options=options,
            images=images,
        )


class SurveySession:
    """Represents an active survey session with an agent, allowing for contextual multi-turn generation."""

    def __init__(
        self, id: uuid.UUID, agent_id: uuid.UUID, status: str, client: "Simile"
    ):
        self._id = id
        self._agent_id = agent_id
        self._status = status
        self._client = client

    @property
    def id(self) -> uuid.UUID:
        return self._id

    @property
    def agent_id(self) -> uuid.UUID:
        return self._agent_id

    @property
    def status(self) -> str:
        return self._status

    async def get_details(self) -> SurveySessionDetailResponse:
        """Retrieves detailed information about this survey session including typed conversation history."""
        return await self._client.get_survey_session_details(self._id)

    async def generate_qual_response(
        self,
        question: str,
        images: Optional[Dict[str, str]] = None,
    ) -> QualGenerationResponse:
        """Generates a qualitative response within this survey session."""
        endpoint = f"sessions/{str(self._id)}/qual"
        payload = QualGenerationRequest(
            question=question,
            data_types=None,
            exclude_data_types=None,
            images=images,
        )
        return await self._client._request(
            "POST",
            endpoint,
            json=payload.model_dump(),
            response_model=QualGenerationResponse,
        )

    async def generate_mc_response(
        self, question: str, options: List[str], images: Optional[Dict[str, str]] = None
    ) -> MCGenerationResponse:
        """Generates a multiple-choice response within this survey session."""
        endpoint = f"sessions/{str(self._id)}/mc"
        payload = MCGenerationRequest(question=question, options=options, images=images)
        return await self._client._request(
            "POST",
            endpoint,
            json=payload.model_dump(),
            response_model=MCGenerationResponse,
        )

    async def add_context(self, ctx: str) -> AddContextResponse:
        """Adds text to the SurveySession without requesting a response."""
        endpoint = f"sessions/{str(self._id)}/context"
        payload = AddContextRequest(context=ctx)
        return await self._client._request(
            "POST",
            endpoint,
            json=payload.model_dump(),
            response_model=AddContextResponse,
        )

    async def close(self) -> SurveySessionCloseResponse:
        """Closes this survey session on the server."""
        endpoint = f"sessions/{str(self._id)}/close"
        return await self._client._request(
            "POST", endpoint, response_model=SurveySessionCloseResponse
        )

    async def add_historical_mc_turn(
        self,
        question: str,
        options: List[str],
        chosen_option: str,
        timestamp: Optional[str] = None,
    ) -> Dict:
        """Adds a historical multiple choice turn to this session with a pre-specified answer.
        
        This method allows you to add a multiple choice question-answer pair to the session's
        conversation history without generating a new response. This is useful for recreating
        conversation history or adding context from previous interactions.
        
        Args:
            question: The multiple choice question text
            options: List of answer options
            chosen_option: The option that was selected
            timestamp: Optional ISO timestamp of when this interaction occurred
            
        Returns:
            Dictionary with success status and the added turn details
            
        Raises:
            Simile.APIError: If the API request fails
        """
        endpoint = f"sessions/{str(self._id)}/historical-mc"
        payload = {
            "question": question,
            "options": options,
            "chosen_option": chosen_option,
        }
        if timestamp:
            payload["timestamp"] = timestamp
            
        return await self._client._request(
            "POST",
            endpoint,
            json=payload,
            response_model=None,  # Return raw dict since we don't have a specific model
        )
