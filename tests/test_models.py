"""Unit tests for all data models in src.models."""

from datetime import datetime
from src.models import (
    HelpDeskRequest,
    ClassificationResult,
    RequestCategory,
    KnowledgeItem,
    HelpDeskResponse,
    SystemHealth,
    TestResult,
)


def test_help_desk_request_model():
    """Test HelpDeskRequest model instantiation and fields."""
    req = HelpDeskRequest(
        user_message="Test", user_id="u1", timestamp="2024-01-01T00:00:00Z"
    )
    assert req.user_message == "Test"
    assert req.user_id == "u1"
    assert req.timestamp == "2024-01-01T00:00:00Z"


def test_classification_result_model():
    """Test ClassificationResult model instantiation and fields."""
    c = ClassificationResult(
        category=RequestCategory.PASSWORD_RESET,
        reasoning="reason",
        escalation_required=True,
    )
    assert c.category == RequestCategory.PASSWORD_RESET
    assert c.escalation_required is True


def test_knowledge_item_model():
    """Test KnowledgeItem model instantiation and fields."""
    k = KnowledgeItem(
        content="info", source="src", relevance_score=0.9, category="cat"
    )
    assert k.content == "info"
    assert k.relevance_score == 0.9
    assert k.category == "cat"


def test_help_desk_response_model():
    """Test HelpDeskResponse model instantiation and fields."""
    c = ClassificationResult(
        category=RequestCategory.PASSWORD_RESET,
        reasoning="reason",
        escalation_required=False,
    )
    r = HelpDeskResponse(request_id="r1", classification=c, response_message="msg")
    assert r.request_id == "r1"
    assert r.classification.category == RequestCategory.PASSWORD_RESET
    assert r.response_message == "msg"


def test_system_health_model():
    """Test SystemHealth model instantiation and fields."""
    s = SystemHealth(
        status="healthy",
        components={"a": "ok"},
        timestamp=datetime.now().isoformat(),
    )
    assert s.status == "healthy"
    assert "a" in s.components


def test_test_result_model():
    """Test TestResult model instantiation and fields."""
    t = TestResult(
        test_id="t1",
        expected_category="cat",
        predicted_category="cat",
        correct_classification=True,
        expected_elements=["a"],
        found_elements=["a"],
        escalation_correct=True,
        response_quality_score=1.0,
    )
    assert t.correct_classification is True
    assert t.response_quality_score == 1.0
