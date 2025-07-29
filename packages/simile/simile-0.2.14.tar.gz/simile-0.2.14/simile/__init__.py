from .client import Simile
from .auth_client import SimileAuth
from .models import (
    Population, Agent, DataItem, 
    CreatePopulationPayload, CreateAgentPayload, CreateDataItemPayload, UpdateDataItemPayload,
    DeletionResponse,
    QualGenerationRequest, 
    QualGenerationResponse, 
    MCGenerationRequest,
    MCGenerationResponse
)
from .exceptions import (
    SimileAPIError, 
    SimileAuthenticationError, 
    SimileNotFoundError, 
    SimileBadRequestError
)

__all__ = [
    "Simile",
    "SimileAuth",
    "Population", "Agent", "DataItem",
    "CreatePopulationPayload", "CreateAgentPayload", "CreateDataItemPayload", "UpdateDataItemPayload",
    "DeletionResponse",
    "QualGenerationRequest", "QualGenerationResponse", 
    "MCGenerationRequest", "MCGenerationResponse",
    "SimileAPIError", "SimileAuthenticationError", "SimileNotFoundError", "SimileBadRequestError"
]

__version__ = "0.2.13"
