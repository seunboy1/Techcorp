"""
Response generator module for the intelligent help desk system.

This module provides functionality to generate contextual responses using
OpenAI's LLM API combined with retrieved knowledge base information to
create comprehensive and helpful IT support responses.
"""
import json
from typing import List
import openai
from .models import ClassificationResult, KnowledgeItem, HelpDeskResponse
from .config import Config


class ResponseGenerator:
    """Generates contextual responses using LLM and retrieved knowledge"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    def generate_response(
        self,
        user_message: str,
        classification: ClassificationResult,
        knowledge_items: List[KnowledgeItem],
        request_id: str,
    ) -> HelpDeskResponse:
        """Generate a comprehensive help desk response"""

        # Prepare knowledge context
        if not knowledge_items:
            return HelpDeskResponse(
                request_id=request_id,
                classification=classification,
                response_message="No specific knowledge base information available.",
            )

        context_parts = []
        for i, item in enumerate(knowledge_items[:5], 1):  # Limit to top 5 items
            context_parts.append(f"{i}. {item.content} (Source: {item.source})")

        knowledge_context = "\n".join(context_parts)

        # Determine escalation details
        escalation_contact = self._get_escalation_contact(
            classification.category.value
        )

        # Create response prompt
        response_prompt = self._create_response_prompt(
            user_message, classification, knowledge_context, escalation_contact
        )

        try:
            # Generate response using LLM
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful IT support specialist. Provide clear, "
                            "actionable solutions based on the provided knowledge base."
                        ),
                    },
                    {"role": "user", "content": response_prompt},
                ],
                temperature=0.3,
                max_tokens=800,
            )

            response_text = response.choices[0].message.content.strip()

            return HelpDeskResponse(
                request_id=request_id,
                classification=classification,
                response_message=response_text,
            )

        except Exception as e:
            print(f"Response generation error: {e}")
            # Fallback response
            return self._generate_fallback_response(classification, request_id)

    def _create_response_prompt(
        self,
        user_message: str,
        classification: ClassificationResult,
        knowledge_context: str,
        escalation_contact: str,
    ) -> str:
        """Create the response generation prompt"""

        try:
            with open(Config.CATEGORIES_PATH, "r", encoding="utf-8") as f:
                categories = json.load(f)["categories"]
                cat_info = categories.get(classification.category.value, {})
                description = cat_info.get('description', 'N/A')
                resolution_time = cat_info.get('typical_resolution_time', 'N/A')
                category_info = (
                    f"Description: {description}\n"
                    f"Typical Resolution Time: {resolution_time}"
                )
        except:
            category_info = "Category information not available"

        escalation_info = ""
        if classification.escalation_required:
            escalation_info = (
                f"\nESCALATION: This request will be escalated to "
                f"{escalation_contact}"
            )
        prompt = f"""
            You are an IT support specialist responding to a help desk request.

            USER REQUEST: "{user_message}"

            CLASSIFICATION: {classification.category.value}
            REASONING: {classification.reasoning}
            ESCALATION REQUIRED: {classification.escalation_required}
            ESCALATION REASON: {classification.escalation_reason or "None"}{escalation_info}

            CATEGORY INFORMATION:
            {category_info}

            RELEVANT KNOWLEDGE BASE INFORMATION:
            {knowledge_context}

            Please provide a helpful response that:
            1. Acknowledges the user's issue
            2. Provides clear, step-by-step solutions based on the knowledge base
            3. Mentions escalation if required
            4. Is professional and empathetic
            5. Includes specific contact information if needed
            6. Response should be in a well structured test not email

            Format your response as a natural, helpful message. Keep it under {Config.MAX_RESPONSE_LENGTH} characters.
        """
        return prompt

    def _get_escalation_contact(self, category: str) -> str:
        """Get appropriate escalation contact based on category"""
        escalation_contacts = {
            "security_incident": "security@techcorp.com",
            "hardware_failure": "hardware-support@techcorp.com",
            "network_connectivity": "network-support@techcorp.com",
            "email_configuration": "email-support@techcorp.com",
            "software_installation": "software-support@techcorp.com",
            "password_reset": "it-support@techcorp.com",
            "policy_question": "it-support@techcorp.com",
        }
        return escalation_contacts.get(category, "it-support@techcorp.com")

    def _generate_fallback_response(
        self,
        classification: ClassificationResult,
        request_id: str,
    ) -> HelpDeskResponse:
        """Generate a fallback response when LLM fails"""

        # Create a simple template-based response
        category = classification.category.value
        response_templates = {
            "password_reset": (
                "I understand you're having password issues. Please visit our "
                "password reset portal at company.com/reset. If you continue to "
                "have problems, please contact IT support."
            ),
            "software_installation": (
                "For software installation issues, please ensure you have "
                "administrator privileges and download from approved vendors. "
                "Contact your manager for approval of new software."
            ),
            "hardware_failure": (
                "I'm sorry to hear about your hardware issue. Please backup "
                "your data and contact hardware support immediately for assistance."
            ),
            "network_connectivity": (
                "For network connectivity issues, please check your physical "
                "connections and try restarting your network adapter. Contact "
                "network support if the issue persists."
            ),
            "email_configuration": (
                "For email configuration issues, please check your internet "
                "connection and verify your email settings. Contact email "
                "support if needed."
            ),
            "security_incident": (
                "This appears to be a security incident. Please do not attempt "
                "to fix this yourself. Contact the security team immediately "
                "at security@techcorp.com."
            ),
            "policy_question": (
                "For policy questions, please refer to our company IT policies. "
                "Contact IT support if you need clarification."
            ),
        }

        response_message = response_templates.get(
            category,
            (
                "Thank you for contacting IT support. We're working on your "
                "request and will get back to you soon."
            ),
        )

        return HelpDeskResponse(
            request_id=request_id,
            classification=classification,
            response_message=response_message,
        )
