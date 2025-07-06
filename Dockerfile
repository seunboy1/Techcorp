# Use the official Python image with a slimmed-down version of Debian
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install poetry

# Set the working directory in the container
WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry: don't create virtual env (we're already in container)
RUN poetry config virtualenvs.create false

# Install dependencies only, not the project itself
RUN poetry install --only=main --no-interaction --no-ansi --no-root

# Copy the src folder itself into the container
COPY src ./src
COPY knowledge_base ./knowledge_base  
COPY docs ./docs  
COPY Makefile README.md ./

# Expose port for FastAPI
EXPOSE 8080

# Fixed healthcheck endpoint for FastAPI
HEALTHCHECK CMD curl --fail http://localhost:8080/health

# Use poetry run in CMD
CMD ["poetry", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8080"]