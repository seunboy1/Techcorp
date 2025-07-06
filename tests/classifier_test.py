"""Unit tests for src.classifier.RequestClassifier covering all logic branches."""

import json
from unittest.mock import mock_open, patch

import pytest

from src.classifier import RequestClassifier
from src.models import ClassificationResult, RequestCategory


def mock_categories():
    """Return a mock categories dictionary for testing."""
    return {"password_reset": {"description": "desc", "escalation_triggers": []}}


@pytest.fixture
def classifier_fixture():
    """Fixture to create a RequestClassifier with mocked categories file."""
    with patch(
        "builtins.open",
        mock_open(read_data=json.dumps({"categories": mock_categories()})),
    ):
        return RequestClassifier()


def test_classify_request_normal(classifier_fixture):
    """Test normal classification with high confidence and no escalation."""
    with patch.object(classifier_fixture, "client") as mock_client:
        mock_client.chat.completions.create.return_value.choices = [
            type(
                "obj",
                (object,),
                {
                    "message": type(
                        "obj",
                        (object,),
                        {
                            "content": (
                                '{"category": "password_reset", "confidence": 0.95, '
                                '"reasoning": "reason", "escalate": false, '
                                '"escalation_reason": null}'
                            )
                        },
                    )()
                },
            )
        ]
        result = classifier_fixture.classify_request("reset my password")
        assert isinstance(result, ClassificationResult)
        assert result.category == RequestCategory.PASSWORD_RESET
        assert result.escalation_required is False


def test_classify_request_low_confidence(classifier_fixture):
    """Test classification with low confidence triggers escalation."""
    with patch.object(classifier_fixture, "client") as mock_client:
        mock_client.chat.completions.create.return_value.choices = [
            type(
                "obj",
                (object,),
                {
                    "message": type(
                        "obj",
                        (object,),
                        {
                            "content": (
                                '{"category": "password_reset", "confidence": 0.2, '
                                '"reasoning": "reason", "escalate": false, '
                                '"escalation_reason": null}'
                            )
                        },
                    )()
                },
            )
        ]
        result = classifier_fixture.classify_request("reset my password")
        assert result.escalation_required is True
        assert "Low classification confidence" in result.escalation_reason


def test_classify_request_escalate_true(classifier_fixture):
    """Test classification with escalate true in LLM response."""
    with patch.object(classifier_fixture, "client") as mock_client:
        mock_client.chat.completions.create.return_value.choices = [
            type(
                "obj",
                (object,),
                {
                    "message": type(
                        "obj",
                        (object,),
                        {
                            "content": (
                                '{"category": "password_reset", "confidence": 0.95, '
                                '"reasoning": "reason", "escalate": true, '
                                '"escalation_reason": "manual"}'
                            )
                        },
                    )()
                },
            )
        ]
        result = classifier_fixture.classify_request("reset my password")
        assert result.escalation_required is True
        assert result.escalation_reason == "manual"


def test_classify_request_llm_error(classifier_fixture):
    """Test classification when LLM call raises an exception."""
    with patch.object(classifier_fixture, "client") as mock_client:
        mock_client.chat.completions.create.side_effect = Exception("fail")
        result = classifier_fixture.classify_request("reset my password")
        assert result.category == RequestCategory.POLICY_QUESTION
        assert "LLM error" in result.reasoning


def test_create_classification_prompt(classifier_fixture):
    """Test prompt creation includes user message and category."""
    prompt = classifier_fixture.create_classification_prompt("reset my password")
    assert "reset my password" in prompt
    assert "password_reset" in prompt


def test_parse_classification_response_valid(classifier_fixture):
    """Test parsing a valid JSON LLM response."""
    response_json = (
        '{"category": "password_reset", "confidence": 0.9, "reasoning": "r", '
        '"escalate": false, "escalation_reason": null}'
    )
    resp = classifier_fixture._parse_classification_response(response_json)
    assert resp["category"] == "password_reset"
    assert resp["confidence"] == 0.9
    assert resp["escalate"] is False


def test_parse_classification_response_invalid_json(classifier_fixture):
    """Test parsing an invalid JSON LLM response returns defaults."""
    resp = classifier_fixture._parse_classification_response("not a json")
    assert resp["category"] == "general"
    assert resp["confidence"] == 0.5
    assert resp["escalate"] is False
