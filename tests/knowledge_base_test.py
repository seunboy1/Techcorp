"""
Unit tests for src.knowledge_base.KnowledgeBaseManager covering
category mapping, loading, searching, and edge cases.
"""

from unittest.mock import patch, mock_open, MagicMock
import json
import numpy as np
from src.knowledge_base import KnowledgeBaseManager
from src.models import KnowledgeItem


def test_category_mapping():
    """Test category mapping from section titles to categories."""
    kb = KnowledgeBaseManager()
    assert kb._map_category_from_title("Password Reset") == "password_reset"
    assert (
        kb._map_category_from_title("Software Installation")
        == "software_installation"
    )
    assert kb._map_category_from_title("Hardware Failure") == "hardware_failure"
    assert (
        kb._map_category_from_title("Network Connectivity")
        == "network_connectivity"
    )
    assert (
        kb._map_category_from_title("Email Configuration") == "email_configuration"
    )
    assert kb._map_category_from_title("Security Incident") == "security_incident"
    assert kb._map_category_from_title("Policy Question") == "policy_question"


def test_load_knowledge_base_loads_from_disk(monkeypatch):
    """Test loading knowledge base from disk with mocked file and faiss."""
    kb = KnowledgeBaseManager()
    # Mock os.path.exists to always return True
    monkeypatch.setattr("os.path.exists", lambda path: True)
    # Mock faiss.read_index
    with patch("faiss.read_index", return_value=MagicMock()), patch(
        "builtins.open",
        mock_open(
            read_data=json.dumps(
                [
                    {
                        "content": "c",
                        "source": "s",
                        "relevance_score": 0.0,
                        "category": "cat",
                    }
                ]
            )
        ),
    ):
        kb.load_knowledge_base()
        assert kb.vector_index is not None
        assert len(kb.knowledge_items) == 1


def test_create_vector_embeddings_handles_empty():
    """Test that creating vector embeddings with no items does not error."""
    kb = KnowledgeBaseManager()
    kb.knowledge_items = []
    kb._create_vector_embeddings()  # Should not error
    assert kb.vector_index is None


def test_get_openai_embeddings_batches():
    """Test batching of OpenAI embeddings call with mocked client."""
    kb = KnowledgeBaseManager()
    # Patch client.embeddings.create to return fake embeddings
    kb.client = MagicMock()
    kb.client.embeddings.create.return_value.data = [
        MagicMock(embedding=[0.1, 0.2, 0.3]) for _ in range(2)
    ]
    result = kb._get_openai_embeddings(["a", "b"])
    assert isinstance(result, list)
    assert result[0] == [0.1, 0.2, 0.3]


def test_search_knowledge_returns_empty_if_no_index():
    """Test that search_knowledge returns empty list if no index or items."""
    kb = KnowledgeBaseManager()
    kb.vector_index = None
    kb.knowledge_items = []
    result = kb.search_knowledge("query")
    assert not result


def test_search_knowledge_filters_and_returns(monkeypatch):
    """Test search_knowledge returns filtered and scored results."""
    kb = KnowledgeBaseManager()
    kb.vector_index = MagicMock()
    kb.knowledge_items = [
        KnowledgeItem(content="c", source="s", relevance_score=0.0, category="cat")
    ]
    # Patch embeddings and faiss search
    monkeypatch.setattr(
        kb, "_get_openai_embeddings", lambda texts: [np.array([1.0, 2.0, 3.0])]
    )
    kb.vector_index.search.return_value = (np.array([[0.9]]), np.array([[0]]))
    result = kb.search_knowledge("query", category="cat", top_k=1)
    assert len(result) == 1
    assert result[0].relevance_score == 0.9


# Optionally, you can add more tests for loading and searching if you mock file I/O and embeddings.
