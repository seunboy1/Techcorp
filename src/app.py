"""
FastAPI application for the intelligent help desk system.

This module provides the REST API endpoints for the intelligent help desk system,
including request processing, system health monitoring, and CORS configuration
for web-based frontends.
"""

from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import HelpDeskRequest, HelpDeskResponse, SystemHealth
from .help_desk_system import IntelligentHelpDeskSystem


# Initialize FastAPI app
app = FastAPI(
    title="Intelligent Help Desk System API",
    description=(
        "AI-powered help desk system with request classification, "
        "knowledge retrieval, and response generation"
    ),
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the help desk system
help_desk_system = IntelligentHelpDeskSystem()


class ProcessRequestRequest(BaseModel):
    """Request model for processing help desk requests"""

    user_message: str
    user_id: Optional[str] = None
    timestamp: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Intelligent Help Desk System API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "process_request": "/process-request",
            "system_health": "/health",
        },
    }


@app.post("/process-request", response_model=HelpDeskResponse)
async def process_request(request: ProcessRequestRequest):
    """Process a help desk request through the complete pipeline"""
    try:
        # Create help desk request
        help_desk_request = HelpDeskRequest(
            user_message=request.user_message,
            user_id=request.user_id,
            timestamp=request.timestamp,
        )

        # Process the request
        response = help_desk_system.process_request(help_desk_request)

        return response

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        ) from e


@app.get("/health", response_model=SystemHealth)
async def get_system_health():
    """Get system health status"""
    return help_desk_system.get_system_health()
