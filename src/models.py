"""
Data models for the intelligent help desk system.

This module defines all the Pydantic models and enums used throughout
the intelligent help desk system, including request/response models,
classification results, knowledge base items, and system health models.
"""
from enum import Enum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class RequestCategory(str, Enum):
    """Enumeration of possible request categories"""

    PASSWORD_RESET = "password_reset"
    SOFTWARE_INSTALLATION = "software_installation"
    HARDWARE_FAILURE = "hardware_failure"
    NETWORK_CONNECTIVITY = "network_connectivity"
    EMAIL_CONFIGURATION = "email_configuration"
    SECURITY_INCIDENT = "security_incident"
    POLICY_QUESTION = "policy_question"


class ClassificationResult(BaseModel):
    """Model for request classification results"""

    category: RequestCategory
    reasoning: str
    escalation_required: bool
    escalation_reason: Optional[str] = None


class KnowledgeItem(BaseModel):
    """Model for knowledge base items"""

    content: str
    source: str
    relevance_score: float
    category: Optional[str] = None


class HelpDeskRequest(BaseModel):
    """Model for incoming help desk requests"""

    request_id: Optional[str] = Field(
        None, description="Unique request identifier"
    )
    user_message: str = Field(..., description="User's request message")
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: Optional[str] = Field(None, description="Request timestamp")


class HelpDeskResponse(BaseModel):
    """Model for help desk system responses"""

    request_id: str
    classification: ClassificationResult
    response_message: str


class SystemHealth(BaseModel):
    """Model for system health status"""

    status: str
    components: Dict[str, str]
    timestamp: str


class TestResult(BaseModel):
    """Model for test evaluation results"""

    test_id: str
    expected_category: str
    predicted_category: str
    correct_classification: bool
    expected_elements: List[str]
    found_elements: List[str]
    escalation_correct: bool
    response_quality_score: float
