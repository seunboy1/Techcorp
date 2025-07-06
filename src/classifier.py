"""
Request classifier module for intelligent help desk system.

This module provides classification functionality for incoming help desk requests
using OpenAI's LLM API to categorize requests and determine escalation requirements.
"""

import json
from typing import Dict, Any
import openai
from .models import ClassificationResult, RequestCategory
from .config import Config


class RequestClassifier:
    """Classifies incoming help desk requests using LLM for escalation only"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
        """Load category definitions"""
        with open(Config.CATEGORIES_PATH, "r", encoding="utf-8") as f:
            categories = json.load(f)["categories"]
        self.categories = categories

    def classify_request(self, user_message: str) -> ClassificationResult:
        """Classify a user request into predefined categories, using LLM for escalation only"""

        # Create classification prompt
        classification_prompt = self.create_classification_prompt(user_message)

        try:
            # Call OpenAI API for classification
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert IT help desk classifier. Your job is to "
                            "categorize user requests accurately and determine if "
                            "escalation to a human is needed."
                        ),
                    },
                    {"role": "user", "content": classification_prompt},
                ],
                temperature=0.1,
                max_tokens=300,
            )

            # Parse the response
            classification_text = response.choices[0].message.content.strip()
            classification_data = self._parse_classification_response(
                classification_text
            )
            escalation_required = classification_data.get("escalate", False)
            escalation_reason = classification_data.get("escalation_reason", None)

            # Check confidence threshold and escalate if too low
            confidence = classification_data.get("confidence", 0.5)
            if confidence < Config.CLASSIFICATION_CONFIDENCE_THRESHOLD:
                escalation_required = True
                escalation_reason = (
                    f"Low classification confidence ({confidence:.2f}) - "
                    f"manual review required"
                )
            return ClassificationResult(
                category=RequestCategory(classification_data["category"]),
                reasoning=classification_data["reasoning"],
                escalation_required=escalation_required,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            print(f"Classification error: {e}")
            # If LLM fails, return a minimal ClassificationResult
            return ClassificationResult(
                category=RequestCategory.POLICY_QUESTION,
                reasoning=f"LLM error: {str(e)}",
                escalation_required=False,
                escalation_reason="LLM unavailable or error",
            )

    def create_classification_prompt(self, user_message: str) -> str:
        """Create the classification prompt for the LLM (ask for escalation info)"""

        categories_text = ""
        for category, info in self.categories.items():
            triggers = info.get("escalation_triggers", [])
            triggers_text = (
                f" (Escalation triggers: {', '.join(triggers)})"
                if triggers
                else ""
            )
            categories_text += (
                f"- {category}: {info['description']}{triggers_text}\n"
            )

        prompt = f"""
            Please classify the following IT help desk request into one of these categories:

            {categories_text}

            User Request: "{user_message}"

            Please respond in the following JSON format:
            {{
                "category": "category_name",
                "confidence": 0.95,
                "reasoning": "Brief explanation of why this category was chosen",
                "escalate": true/false,
                "escalation_reason": "If escalation is needed, explain why; otherwise null or empty"
            }}

            Only use the exact category names listed above. Confidence should be between 0.0 and 1.0.
        """
        return prompt

    def _parse_classification_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the LLM classification response (with escalation info)"""
        try:
            # Try to extract JSON from the response
            if "{" in response_text and "}" in response_text:
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                json_str = response_text[start:end]
                data = json.loads(json_str)

                return {
                    "category": data.get("category", "general"),
                    "confidence": float(data.get("confidence", 0.5)),
                    "reasoning": data.get("reasoning", "No reasoning provided"),
                    "escalate": data.get("escalate", False),
                    "escalation_reason": data.get("escalation_reason", None),
                }
            raise ValueError("No JSON found in response")

        except Exception as e:
            print(f"Error parsing classification response: {e}")
            return {
                "category": "general",
                "confidence": 0.5,
                "reasoning": f"Error parsing response: {str(e)}",
                "escalate": False,
                "escalation_reason": None,
            }
