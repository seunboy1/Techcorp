# Techcorp: **AI-Powered Help Desk System**

## Overview

This project implements an intelligent help desk system that uses AI to classify user requests, retrieve relevant knowledge from a comprehensive database, and generate contextual responses. The system can automatically escalate complex issues that require human intervention.

## Project Structure

```bash
├── src/
│   ├── app.py                    # FastAPI REST API endpoints
│   ├── help_desk_system.py       # Main system orchestrator
│   ├── classifier.py             # AI-powered request classification
│   ├── knowledge_base.py         # Vector search and knowledge retrieval
│   ├── response_generator.py     # LLM-based response generation
│   ├── models.py                 # Pydantic data models
│   └── config.py                 # Configuration settings
├── tests/
│   ├── test_classifier.py        # Tests for request classification
│   ├── test_help_desk_system.py # Tests for main system functionality
│   ├── test_knowledge_base.py   # Tests for knowledge base operations
│   ├── test_response_generator.py # Tests for response generation
│   ├── test_models.py           # Tests for data models
│   └── test_knowledge_base_fileio.py # Tests for file I/O operations
├── knowledge_base/
│   ├── company_it_policies.md    # IT policy documentation
│   ├── knowledge_base.md         # General knowledge base
│   ├── installation_guides.json  # Software installation guides
│   ├── troubleshooting_database.json # Troubleshooting solutions
│   └── knowledge_base_index.faiss # Vector search index
├── docs/
│   ├── categories.json           # Request category definitions
│   ├── sample_conversations.json # Example conversations
│   └── test_requests.json       # Test request data
├── pyproject.toml               # Poetry dependency management
├── poetry.lock                  # Locked dependencies
├── Makefile                     # Build and deployment commands
├── Dockerfile                   # Container configuration
├── pre-commit-config.yaml       # Pre-commit hooks configuration
└── README.md                    # Project documentation
```

## Setup

- Create a virtual environment and install dependencies:
    ```bash
        make install
    ```

- Perform code formatting
    ```bash
        make format
    ```

- To run pylint on terminal
    ```bash
        make lint
    ```

- To run unit tests and code coverage for the FastAPI backend, use:
    ```bash
        make test
    ```

## Building and Running without Docker

- Run FastAPI locally:
    ```bash
        make local
    ```

- Open `http://localhost:8000` in your browser to access the API documentation.

### Pre-commit setup and basic command
#### Following various software best concepts and practices such as testing, code coverage, linting, code formatting.

-  Install pre-commit
   ```bash
      pip install pre-commit
   ```

-  Run against all the files
   ```bash
      pre-commit run --all-files
   ```

- To automate pre-commit checks, you will have to install the git hook scripts.
   ```bash
      pre-commit install
   ```
- Now pre-commit checks is done after every commits

## Building and Running using Docker container

-  Build the services
   ```bash
      make build
   ```

-  Run the Containers
   ```bash
      make run
   ```

-  Access the Application
    - Open your browser and navigate to http://localhost:8080

-  Clean up unnecessary files
   ```bash
      make clean
      make clean-venv
   ```

## API Endpoints

### Process Request
- **POST** `/process-request`
- Processes user requests through the complete AI pipeline
- Request body: `{"user_message": "string", "user_id": "string", "timestamp": "string"}`

### System Health
- **GET** `/health`
- Returns system health status and component status

### Root Endpoint
- **GET** `/`
- Returns API information and available endpoints

## Core Features

- **AI-Powered Classification**: Uses OpenAI GPT-3.5-turbo to categorize incoming requests
- **Vector Knowledge Search**: FAISS-based similarity search for relevant information retrieval
- **Contextual Response Generation**: LLM-generated responses incorporating retrieved knowledge
- **Intelligent Escalation**: Automatic detection of requests requiring human intervention
- **RESTful API**: FastAPI-based API with comprehensive error handling
- **Comprehensive Testing**: Automated test suite with performance evaluation

## Requirements

- Python 3.10+
- OpenAI API key
- Internet connection for model downloads

## Environment Variables

Create a `.env` file in the `src/` directory with:
```
# Get your API key from https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Optional: Override default settings
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.8
MAX_RESPONSE_LENGTH=500
MAX_RETRIEVAL_RESULTS=3
KNOWLEDGE_BASE_DIR=knowledge_base
DOCS=docs
```

## Live URL

[API Documentation](http://localhost:8000/docs) - Available when running locally
