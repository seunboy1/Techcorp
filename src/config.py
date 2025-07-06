"""Configuration settings for the Intelligent Help Desk System"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration settings for the Intelligent Help Desk System"""

    # Get the project root directory (parent of src directory)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_EMBEDDING_MODEL = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002"
    )
    OPENAI_EMBEDDING_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "1536"))

    # Classification Configuration
    CLASSIFICATION_CONFIDENCE_THRESHOLD = float(
        os.getenv("CLASSIFICATION_CONFIDENCE_THRESHOLD", "0.8")
    )

    # Vector Search Configuration
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))

    # Response Configuration
    MAX_RESPONSE_LENGTH = os.getenv("MAX_RESPONSE_LENGTH", "500")
    MAX_RETRIEVAL_RESULTS = os.getenv("MAX_RETRIEVAL_RESULTS", "3")

    # Knowledge Base Directory
    DOCS = os.getenv("DOCS", "docs")
    KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")

    # File Paths (all relative to project root)
    CATEGORIES_PATH = os.path.join(PROJECT_ROOT, DOCS, "categories.json")
    TEST_REQUESTS_PATH = os.path.join(PROJECT_ROOT, DOCS, "test_requests.json")
    POLICIES_PATH = os.path.join(
        PROJECT_ROOT, KNOWLEDGE_BASE_DIR, "company_it_policies.md"
    )
    KNOWLEDGE_BASE_PATH = os.path.join(
        PROJECT_ROOT, KNOWLEDGE_BASE_DIR, "knowledge_base.md"
    )
    INSTALLATION_GUIDES_PATH = os.path.join(
        PROJECT_ROOT, KNOWLEDGE_BASE_DIR, "installation_guides.json"
    )
    TROUBLESHOOTING_PATH = os.path.join(
        PROJECT_ROOT, KNOWLEDGE_BASE_DIR, "troubleshooting_database.json"
    )
    SAMPLE_CONVERSATIONS_PATH = os.path.join(
        PROJECT_ROOT, KNOWLEDGE_BASE_DIR, "sample_conversations.json"
    )
