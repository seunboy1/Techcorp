"""Unit tests for file I/O and processing methods in src.knowledge_base.KnowledgeBaseManager."""

from unittest.mock import patch, mock_open
from src.knowledge_base import KnowledgeBaseManager


def test_process_knowledge_base_md():
    """Test processing of knowledge base markdown file."""
    kb = KnowledgeBaseManager()
    md = """## Password Reset
- Reset your password at the portal
- Contact IT if locked out
"""
    with patch("builtins.open", mock_open(read_data=md)):
        kb.knowledge_items = []
        kb._process_knowledge_base_md()
        assert any(
            "Reset your password" in item.content for item in kb.knowledge_items
        )


def test_process_policies_md():
    """Test processing of company policies markdown file."""
    kb = KnowledgeBaseManager()
    md = """## Security Policy
- Never share your password
- Report incidents immediately
"""
    with patch("builtins.open", mock_open(read_data=md)):
        kb.knowledge_items = []
        kb._process_policies_md()
        assert any(
            "Never share your password" in item.content
            for item in kb.knowledge_items
        )


def test_process_troubleshooting_steps():
    """Test processing of troubleshooting steps."""
    kb = KnowledgeBaseManager()
    kb.troubleshooting_steps = {
        "slow_computer": {
            "category": "performance",
            "steps": ["Restart", "Check updates"],
            "escalation_trigger": "Unresolved after restart",
        }
    }
    kb.knowledge_items = []
    kb._process_troubleshooting_steps()
    assert any(
        "Troubleshooting steps for slow_computer" in item.content
        for item in kb.knowledge_items
    )
    assert any(
        "Escalation trigger for slow_computer" in item.content
        for item in kb.knowledge_items
    )


def test_process_installation_guides():
    """Test processing of installation guides."""
    kb = KnowledgeBaseManager()
    kb.installation_guides = {
        "Office": {
            "title": "Office Install",
            "steps": ["Download", "Run installer"],
            "common_issues": [{"issue": "Activation", "solution": "Contact IT"}],
        }
    }
    kb.knowledge_items = []
    kb._process_installation_guides()
    assert any(
        "Installation steps for Office" in item.content
        for item in kb.knowledge_items
    )
    assert any(
        "Common issue with Office" in item.content for item in kb.knowledge_items
    )
