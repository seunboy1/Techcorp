"""Unit tests for src.response_generator.ResponseGenerator covering all logic branches."""

from unittest.mock import patch
import pytest
from src.response_generator import ResponseGenerator
from src.models import (
    ClassificationResult,
    RequestCategory,
    KnowledgeItem,
    HelpDeskResponse,
)


def make_classification(
    category=RequestCategory.PASSWORD_RESET,
    escalation_required=False,
    escalation_reason=None,
):
    """Helper to create a ClassificationResult."""
    return ClassificationResult(
        category=category,
        reasoning="reason",
        escalation_required=escalation_required,
        escalation_reason=escalation_reason,
    )


def test_generate_response_no_knowledge_items():
    """Test early return when no knowledge items are provided."""
    rg = ResponseGenerator()
    classification = make_classification()
    resp = rg.generate_response("msg", classification, [], "reqid")
    assert isinstance(resp, HelpDeskResponse)
    assert "No specific knowledge base information" in resp.response_message


def test_generate_response_exception_fallback():
    """Test fallback response when LLM call fails."""
    rg = ResponseGenerator()
    classification = make_classification()
    knowledge_items = [
        KnowledgeItem(
            content="info",
            source="src",
            relevance_score=1.0,
            category="password_reset",
        )
    ]
    with patch.object(rg, "client") as mock_client:
        mock_client.chat.completions.create.side_effect = Exception("fail")
        resp = rg.generate_response(
            "msg", classification, knowledge_items, "reqid"
        )
        assert isinstance(resp, HelpDeskResponse)
        assert "password" in resp.response_message.lower()


def test_create_response_prompt_exception():
    """Test prompt creation when category info file read fails."""
    rg = ResponseGenerator()
    classification = make_classification()
    with patch("builtins.open", side_effect=Exception("fail")):
        prompt = rg._create_response_prompt(
            "msg", classification, "context", "contact"
        )
        assert "Category information not available" in prompt


@pytest.mark.parametrize(
    "category,expected",
    [
        ("password_reset", "password"),
        ("software_installation", "software"),
        ("hardware_failure", "hardware"),
        ("network_connectivity", "network"),
        ("email_configuration", "email"),
        ("security_incident", "security"),
        ("policy_question", "policy"),
    ],
)
def test_generate_fallback_response(category, expected):
    """Test fallback response for all categories."""
    rg = ResponseGenerator()
    classification = make_classification(category=RequestCategory(category))
    resp = rg._generate_fallback_response(classification, "reqid")
    assert expected.split()[0] in resp.response_message.lower()


def test_generate_response_returns_helpdeskresponse():
    """Test normal LLM response generation."""
    rg = ResponseGenerator()
    classification = ClassificationResult(
        category=RequestCategory.PASSWORD_RESET,
        reasoning="reason",
        escalation_required=False,
    )
    knowledge_items = [
        KnowledgeItem(
            content="info",
            source="src",
            relevance_score=1.0,
            category="password_reset",
        )
    ]
    with patch.object(rg, "client") as mock_client:
        mock_client.chat.completions.create.return_value.choices = [
            type(
                "obj",
                (object,),
                {
                    "message": type(
                        "obj", (object,), {"content": "Test response"}
                    )()
                },
            )
        ]
        resp = rg.generate_response(
            "test", classification, knowledge_items, "reqid"
        )
        assert isinstance(resp, HelpDeskResponse)
        assert resp.response_message == "Test response"
