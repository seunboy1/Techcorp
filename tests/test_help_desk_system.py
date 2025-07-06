"""
Test module for IntelligentHelpDeskSystem.

This module contains unit tests for the IntelligentHelpDeskSystem class,
testing various scenarios including normal operation, error handling,
and system health monitoring.
"""

from unittest.mock import patch, MagicMock
from src.help_desk_system import IntelligentHelpDeskSystem
from src.models import (
    HelpDeskRequest,
    HelpDeskResponse,
    ClassificationResult,
    RequestCategory,
    SystemHealth,
)


def test_process_request_normal():
    """Test normal request processing with successful classification and response generation."""
    system = IntelligentHelpDeskSystem()
    request = HelpDeskRequest(user_message="reset my password")
    with patch.object(system, "classifier") as mock_classifier, patch.object(
        system, "knowledge_base"
    ) as mock_kb, patch.object(system, "response_generator") as mock_rg:
        mock_classifier.classify_request.return_value = ClassificationResult(
            category=RequestCategory.PASSWORD_RESET,
            reasoning="reason",
            escalation_required=False,
            escalation_reason=None,
        )
        mock_kb.search_knowledge.return_value = []
        mock_rg.generate_response.return_value = HelpDeskResponse(
            request_id="1",
            classification=mock_classifier.classify_request.return_value,
            response_message="msg",
        )
        resp = system.process_request(request)
        assert isinstance(resp, HelpDeskResponse)
        assert resp.response_message == "msg"


def test_process_request_error():
    """Test request processing when classifier raises an exception."""
    system = IntelligentHelpDeskSystem()
    request = HelpDeskRequest(user_message="reset my password")
    with patch.object(system, "classifier") as mock_classifier:
        mock_classifier.classify_request.side_effect = Exception("fail")
        resp = system.process_request(request)
        assert isinstance(resp, HelpDeskResponse)
        assert resp.classification.category == RequestCategory.POLICY_QUESTION
        assert resp.classification.escalation_required is True
        assert "error" in resp.response_message.lower()


def test_create_error_response():
    """Test creation of error response with proper escalation flags."""
    system = IntelligentHelpDeskSystem()
    resp = system._create_error_response("id1", "fail")
    assert isinstance(resp, HelpDeskResponse)
    assert resp.classification.category == RequestCategory.POLICY_QUESTION
    assert resp.classification.escalation_required is True
    assert "fail" in resp.response_message


def test_get_system_health_healthy():
    """Test system health check when all components are functioning properly."""
    system = IntelligentHelpDeskSystem()
    # Mock vector_index to simulate healthy knowledge base
    system.knowledge_base.vector_index = MagicMock()
    health = system.get_system_health()
    assert isinstance(health, SystemHealth)
    assert health.status == "healthy"
    assert health.components["knowledge_base"] == "healthy"


def test_get_system_health_degraded():
    """Test system health check when knowledge base is unavailable."""
    system = IntelligentHelpDeskSystem()
    # Simulate unhealthy knowledge base
    system.knowledge_base.vector_index = None
    health = system.get_system_health()
    assert health.status == "degraded"
    assert health.components["knowledge_base"] == "unhealthy"
