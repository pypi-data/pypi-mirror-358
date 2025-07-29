from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid


class Population(BaseModel):
    population_id: uuid.UUID
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DataItem(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    data_type: str
    content: Any
    created_at: datetime
    updated_at: datetime


class Agent(BaseModel):
    agent_id: uuid.UUID
    name: str
    population_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime
    data_items: List[DataItem] = Field(default_factory=list)


class CreatePopulationPayload(BaseModel):
    name: str
    description: Optional[str] = None


class InitialDataItemPayload(BaseModel):
    data_type: str
    content: Any


class CreateAgentPayload(BaseModel):
    name: str
    population_id: Optional[uuid.UUID] = None
    agent_data: Optional[List[InitialDataItemPayload]] = None


class CreateDataItemPayload(BaseModel):
    data_type: str
    content: Any


class UpdateDataItemPayload(BaseModel):
    content: Any


class DeletionResponse(BaseModel):
    message: str


# --- Generation Operation Models ---
class QualGenerationRequest(BaseModel):
    question: str
    data_types: Optional[List[str]] = None
    exclude_data_types: Optional[List[str]] = None
    images: Optional[Dict[str, str]] = (
        None  # Dict of {description: url} for multiple images
    )


class QualGenerationResponse(BaseModel):
    question: str
    answer: str


class MCGenerationRequest(BaseModel):
    question: str
    options: List[str]
    images: Optional[Dict[str, str]] = None


class MCGenerationResponse(BaseModel):
    question: str
    options: List[str]
    chosen_option: str


class AddContextRequest(BaseModel):
    context: str


class AddContextResponse(BaseModel):
    message: str
    session_id: uuid.UUID


# --- Survey Session Models ---
class TurnType(str, Enum):
    """Enum for different types of conversation turns."""

    CONTEXT = "context"
    IMAGE = "image"
    QUALITATIVE_QUESTION = "qualitative_question"
    MULTIPLE_CHOICE_QUESTION = "multiple_choice_question"


class BaseTurn(BaseModel):
    """Base model for all conversation turns."""

    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    type: TurnType

    class Config:
        use_enum_values = True


class ContextTurn(BaseTurn):
    """A context turn that provides background information."""

    type: Literal[TurnType.CONTEXT] = TurnType.CONTEXT
    user_context: str


class ImageTurn(BaseTurn):
    """A standalone image turn (e.g., for context or reference)."""

    type: Literal[TurnType.IMAGE] = TurnType.IMAGE
    images: Dict[str, str]
    caption: Optional[str] = None


class QualitativeQuestionTurn(BaseTurn):
    """A qualitative question-answer turn."""

    type: Literal[TurnType.QUALITATIVE_QUESTION] = TurnType.QUALITATIVE_QUESTION
    user_question: str
    user_images: Optional[Dict[str, str]] = None
    llm_response: Optional[str] = None


class MultipleChoiceQuestionTurn(BaseTurn):
    """A multiple choice question-answer turn."""

    type: Literal[TurnType.MULTIPLE_CHOICE_QUESTION] = TurnType.MULTIPLE_CHOICE_QUESTION
    user_question: str
    user_options: List[str]
    user_images: Optional[Dict[str, str]] = None
    llm_chosen_option: Optional[str] = None

    @validator("user_options")
    def validate_options(cls, v):
        if not v:
            raise ValueError("Multiple choice questions must have at least one option")
        if len(v) < 2:
            raise ValueError(
                "Multiple choice questions should have at least two options"
            )
        return v

    @validator("llm_chosen_option")
    def validate_chosen_option(cls, v, values):
        if (
            v is not None
            and "user_options" in values
            and v not in values["user_options"]
        ):
            raise ValueError(f"Chosen option '{v}' must be one of the provided options")
        return v


# Union type for all possible turn types
SurveySessionTurn = Union[
    ContextTurn, ImageTurn, QualitativeQuestionTurn, MultipleChoiceQuestionTurn
]


class SurveySessionCreateResponse(BaseModel):
    id: uuid.UUID  # Session ID
    agent_id: uuid.UUID
    created_at: datetime
    status: str


class SurveySessionDetailResponse(BaseModel):
    """Detailed survey session response with typed conversation turns."""

    id: uuid.UUID
    agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str
    conversation_history: List[SurveySessionTurn] = Field(default_factory=list)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SurveySessionListItemResponse(BaseModel):
    """Summary response for listing survey sessions."""

    id: uuid.UUID
    agent_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    status: str
    turn_count: int = Field(description="Number of turns in conversation history")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class SurveySessionCloseResponse(BaseModel):
    id: uuid.UUID  # Session ID
    status: str
    updated_at: datetime
    message: Optional[str] = None
