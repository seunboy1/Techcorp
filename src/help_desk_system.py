"""
Main help desk system module for orchestrating all components.

This module provides the central IntelligentHelpDeskSystem class that coordinates
request classification, knowledge base retrieval, and response generation to
provide comprehensive IT support responses.
"""

import uuid
from datetime import datetime

from .models import HelpDeskRequest, HelpDeskResponse, SystemHealth
from .classifier import RequestClassifier
from .knowledge_base import KnowledgeBaseManager
from .response_generator import ResponseGenerator
from .config import Config


class IntelligentHelpDeskSystem:
    """Main intelligent help desk system that orchestrates all components"""

    def __init__(self):
        self.classifier = RequestClassifier()
        self.knowledge_base = KnowledgeBaseManager()
        self.response_generator = ResponseGenerator()

        # Initialize the system
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the help desk system"""
        print("Initializing Intelligent Help Desk System...")

        # Load knowledge base
        self.knowledge_base.load_knowledge_base()

        print("System initialization complete!")

    def process_request(self, request: HelpDeskRequest) -> HelpDeskResponse:
        """Process a help desk request through the complete pipeline"""

        # Generate request ID if not provided
        if not request.request_id:
            request.request_id = str(uuid.uuid4())

        print(
            f"Processing request {request.request_id}: {request.user_message[:50]}..."
        )

        try:
            # Step 1: Classify the request
            print("Step 1: Classifying request...")
            classification = self.classifier.classify_request(request.user_message)
            print(f"Classification: {classification.category.value}")

            # Step 2: Retrieve relevant knowledge
            print("Step 2: Retrieving relevant knowledge...")
            knowledge_items = self.knowledge_base.search_knowledge(
                request.user_message,
                category=classification.category.value,
                top_k=int(Config.MAX_RETRIEVAL_RESULTS),
            )
            print(f"Retrieved {len(knowledge_items)} knowledge items")

            # Step 3: Generate response
            print("Step 3: Generating response...")
            response = self.response_generator.generate_response(
                request.user_message,
                classification,
                knowledge_items,
                request.request_id,
            )

            print(f"Request {request.request_id} processed successfully")
            return response

        except Exception as e:
            print(f"Error processing request: {e}")
            # Return error response
            return self._create_error_response(request.request_id, str(e))

    def _create_error_response(
        self, request_id: str, error_message: str
    ) -> HelpDeskResponse:
        """Create an error response when processing fails"""
        from .models import ClassificationResult, RequestCategory

        error_classification = ClassificationResult(
            category=RequestCategory.POLICY_QUESTION,  # Default category
            reasoning="Error occurred during processing",
            escalation_required=True,
            escalation_reason="System error requires manual intervention",
        )

        error_msg = (
            "I apologize, but I encountered an error while processing your request. "
            f"Please contact IT support directly. Error: {error_message}"
        )

        return HelpDeskResponse(
            request_id=request_id,
            classification=error_classification,
            response_message=error_msg,
        )

    def get_system_health(self) -> SystemHealth:
        """Get system health status"""
        components = {
            "classifier": "healthy",
            "knowledge_base": (
                "healthy" if self.knowledge_base.vector_index else "unhealthy"
            ),
            "response_generator": "healthy",
        }

        # Determine overall status
        overall_status = (
            "healthy"
            if all(status == "healthy" for status in components.values())
            else "degraded"
        )

        return SystemHealth(
            status=overall_status,
            components=components,
            timestamp=datetime.now().isoformat(),
        )
