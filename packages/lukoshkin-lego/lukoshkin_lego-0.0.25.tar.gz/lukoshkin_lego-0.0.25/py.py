"""
Virtual Assistant Lambda Handler

This module implements a virtual assistant that processes user queries through
Amazon Lex and handles various intents including device control, weather information,
timers, and fallback to LLM for general queries.
"""

import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from typing import Any

import boto3
from loguru import logger


class VirtualAssistant:
    """
    Virtual Assistant class that handles processing of user queries through
    Amazon Lex and manages various intents.
    """

    BOT_ID = "PGRADZ0WFU"
    BOT_ALIAS_ID = "PGENOOBNXS"  # test-llm-fallback
    LOCALE_ID = "en_US"
    REGION = "us-east-1"

    def __init__(self):
        """Initialize the Virtual Assistant with AWS clients."""
        # Initialize AWS clients
        if "AWS_LAMBDA_FUNCTION_NAME" not in os.environ:
            # For local debugging, you might need to specify a profile or use default credentials
            session = boto3.Session(region_name=self.REGION)
            self.lex = session.client("lexv2-runtime")
            self.bedrock = session.client("bedrock-runtime")
        else:
            self.lex = boto3.client("lexv2-runtime", region_name=self.REGION)
            self.bedrock = boto3.client("bedrock-runtime")

    def handle_request(self, event: dict[str, Any]) -> dict[str, Any]:
        """
        Main handler for processing user requests.

        Args:
            event: The Lambda event object

        Returns:
            API Gateway response object
        """
        try:
            body = json.loads(event.get("body", "{}"))
            user_id = body.get("userId", str(uuid.uuid4()))
            session_id = body.get("sessionId", str(uuid.uuid4()))
            user_prompt = body.get("text", "")
            logger.info(
                f"Processing request for user: {user_id},"
                f" session: {session_id}, user asked: {user_prompt}"
            )
            if not user_prompt:
                return self.create_response(
                    400, {"message": "Text input is required!"}
                )

            intent, slots, confidence = self._process_lex_intent(
                session_id, user_prompt
            )
            if confidence < 0.9:
                return self.create_response(
                    200, self.handle_fallback_intent(user_prompt)
                )
            return self.create_response(
                200, self.handle_named_intent(intent, user_prompt, slots)
            )
        except Exception as exc:
            logger.error(
                f"Error processing request: {str(exc)}", exc_info=True
            )
            return self.create_response(
                500,
                {
                    "error": str(exc),
                    "message": "There was an issue processing your request.",
                },
            )

    def handle_named_intent(
        self, intent: str, user_text: str, slots: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Route the request to the appropriate intent handler.

        Args:
            intent: The detected intent from Lex
            user_text: The user's text input
            slots: The slots from Lex

        Returns:
            Response data
        """
        if intent == "ControlDevice":
            return self.handle_device_command(slots, user_text)
        if intent == "WeatherIntent":
            return self.handle_weather_intent(slots)
        if intent == "TimerIntent":
            return self.handle_timer_intent(slots)

        return self.handle_fallback_intent(user_text)

    def _process_lex_intent(
        self, session_id: str, user_prompt: str
    ) -> tuple[str, dict, float]:
        """
        Process the user prompt through Amazon Lex.

        Args:
            session_id: The session ID for the conversation
            user_prompt: The user's text input

        Returns:
            Tuple of (intent_name, slots, confidence_score)
        """
        lex_response = self.lex.recognize_text(
            botId=self.BOT_ID,
            botAliasId=self.BOT_ALIAS_ID,
            localeId=self.LOCALE_ID,
            sessionId=session_id,
            text=user_prompt,
        )
        state = lex_response.get("sessionState", {})
        interpretations = lex_response.get("interpretations", [{}])
        confidence_score = interpretations[0]["nluConfidence"]["score"]
        intent_name = state["intent"]["name"]
        slots = state["intent"]["slots"]
        return intent_name, slots, confidence_score

    def postprocess_fallback_intent(
        self, intent: str, user_prompt: str
    ) -> dict[str, Any] | None:
        """
        Post-process fallback intent to check for keywords and redirect to appropriate handlers.

        Args:
            intent: The detected intent
            user_prompt: The user's text input

        Returns:
            Response data or None
        """
        # Check for keywords in the text if the intent is FallbackIntent
        user_text_lower = user_prompt.lower()
        if intent == "FallbackIntent":
            if any(
                keyword in user_text_lower
                for keyword in [
                    "weather",
                    "temperature",
                    "forecast",
                    "rain",
                    "sunny",
                ]
            ):
                # Extract timeframe if present
                timeframe = "today"
                if "tomorrow" in user_text_lower:
                    timeframe = "tomorrow"
                elif "weekend" in user_text_lower:
                    timeframe = "this weekend"
                elif "next week" in user_text_lower:
                    timeframe = "next week"

                return self.create_response(
                    200,
                    self.handle_weather_intent(
                        {
                            "timeframe": {
                                "value": {"interpretedValue": timeframe}
                            }
                        }
                    ),
                )
            # Check for timer keywords
            elif any(
                keyword in user_text_lower
                for keyword in ["timer", "remind", "alarm", "wait"]
            ):
                # Extract duration if present
                duration = "5 minutes"  # Default
                for word in user_text_lower.split():
                    if word.isdigit():
                        index = user_text_lower.find(word)
                        if index >= 0:
                            # Try to extract "X minutes/seconds/hours"
                            end_index = user_text_lower.find(
                                " ", index + len(word) + 1
                            )
                            if end_index > 0:
                                duration = user_text_lower[
                                    index:end_index
                                ].strip()
                            else:
                                duration = user_text_lower[index:].strip()
                            break

                return self.create_response(
                    200,
                    self.handle_timer_intent(
                        {"duration": {"value": {"interpretedValue": duration}}}
                    ),
                )
        return None

    def _get_slot_value(self, slot: dict[str, Any] | None) -> str:
        """
        Helper method to extract values from Lex slots.

        Args:
            slot: The slot object from Lex

        Returns:
            The extracted value as a string
        """
        if not slot:
            return ""

        value = slot.get("value", {})
        return (
            value.get("resolvedValues", [])[0]
            if value.get("resolvedValues")
            else value.get("interpretedValue", "")
        )

    def handle_device_command(
        self, slots: dict[str, Any], user_text: str
    ) -> dict[str, Any]:
        """
        Handle device control commands.

        Args:
            slots: The slots from Lex
            user_text: The original user text

        Returns:
            Response data
        """
        device_name = self._get_slot_value(slots.get("DeviceName", {}))
        device_action = self._get_slot_value(slots.get("DeviceAction", {}))

        # Extract action from the user text if not provided in slots
        user_text_lower = user_text.lower()
        if not device_action:
            if (
                "turn on" in user_text_lower
                or "switch on" in user_text_lower
                or "power on" in user_text_lower
            ):
                device_action = "on"
            elif (
                "turn off" in user_text_lower
                or "switch off" in user_text_lower
                or "power off" in user_text_lower
            ):
                device_action = "off"

        logger.info(f"Device command: {device_name}, action: {device_action}")

        if device_name and device_action:
            response_text = (
                f"Successfully turned {device_name} {device_action}."
            )
        else:
            response_text = f"I understood you want to control the {device_name}, but I'm not sure what action to take."

        return {
            "type": "device_control",
            "response": response_text,
            "intent": "ControlDevice",
            "device": device_name,
            "action": device_action,
        }

    def handle_weather_intent(self, slots: dict[str, Any]) -> dict[str, Any]:
        """
        Handle weather-related queries.

        Args:
            slots: The slots from Lex

        Returns:
            Response data
        """
        timeframe = self._get_slot_value(slots.get("timeframe", {})) or "today"

        # Mock weather response
        weather_conditions = {
            "today": "sunny with a high of 75°F",
            "tomorrow": "partly cloudy with a high of 72°F",
            "this weekend": "rainy with temperatures around 68°F",
            "next week": "mostly sunny with temperatures in the mid-70s",
        }

        condition = weather_conditions.get(timeframe.lower(), "variable")
        response_text = f"The weather for {timeframe} is {condition}."

        return {
            "type": "weather",
            "response": response_text,
            "intent": "WeatherIntent",
            "timeframe": timeframe,
        }

    def handle_timer_intent(self, slots: dict[str, Any]) -> dict[str, Any]:
        """
        Handle timer and reminder requests.

        Args:
            slots: The slots from Lex

        Returns:
            Response data
        """
        duration = self._get_slot_value(slots.get("duration", {}))
        action = self._get_slot_value(slots.get("action", {}))

        if duration:
            # In a real implementation, this would create an actual timer in DynamoDB
            # and set up a scheduled Lambda function to handle the timer expiration

            # For now, just acknowledge the timer request
            if action:
                response_text = (
                    f"I've set a reminder to {action} in {duration}."
                )
            else:
                response_text = f"I've set a timer for {duration}."

            # Calculate and include the expiration time for display purposes
            try:
                # This is a simplified duration parser - a real implementation would be more robust
                duration_parts = duration.split()
                if len(duration_parts) >= 2:
                    amount = int(duration_parts[0])
                    unit = duration_parts[1].lower()

                    now = datetime.now()
                    if "minute" in unit:
                        expiration_time = now + timedelta(minutes=amount)
                    elif "hour" in unit:
                        expiration_time = now + timedelta(hours=amount)
                    elif "second" in unit:
                        expiration_time = now + timedelta(seconds=amount)
                    else:
                        expiration_time = now + timedelta(minutes=5)  # Default

                    expiration_str = expiration_time.strftime("%I:%M %p")
                    response_text += f" It will expire at {expiration_str}."
            except Exception as e:
                logger.warning(f"Error parsing duration: {str(e)}")
        else:
            response_text = "I couldn't understand the duration for the timer."

        return {
            "type": "timer",
            "response": response_text,
            "intent": "TimerIntent",
            "duration": duration,
            "action": action,
        }

    def handle_fallback_intent(self, user_text: str) -> dict[str, Any]:
        """
        Handle fallback to LLM for general queries.

        Args:
            user_text: The user's text input

        Returns:
            Response data
        """
        try:
            model_id = "anthropic.claude-v2"
            logger.info(f"Using LLM model: {model_id}")

            # Call Bedrock with Claude v2
            response = self.bedrock.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(
                    {
                        "prompt": f"Human: {user_text}\nAssistant:",
                        "max_tokens_to_sample": 300,
                        "temperature": 0.7,
                    }
                ),
            )

            # Parse the response
            response_body = json.loads(response["body"].read().decode("utf-8"))
            llm_response = response_body.get(
                "completion", "I'm not sure how to help with that."
            )

            return {
                "type": "llm",
                "response": llm_response,
                "intent": "FallbackIntent",
                "model": model_id,
            }

        except Exception as exc:
            logger.error(f"Error calling LLM: {str(exc)}", exc_info=True)
            return {
                "type": "error",
                "response": "I'm having trouble connecting to my knowledge service right now. Please try again later.",
                "intent": "FallbackIntent",
                "error": str(exc),
            }

    def create_response(self, status_code: int, body: dict) -> dict[str, Any]:
        """
        Create a standardized API response.

        Args:
            status_code: HTTP status code
            body: Response body

        Returns:
            API Gateway response object
        """
        return {
            "statusCode": status_code,
            "body": json.dumps(body, default=str),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
        }


# Command-line interface for local debugging
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python lambda_function.py "your text query here"')
        sys.exit(1)

    user_text = " ".join(sys.argv[1:])
    mock_event = {
        "body": json.dumps(
            {
                "text": user_text,
                "userId": "local-debug-user",
                "sessionId": f"local-debug-session-{uuid.uuid4()}",
            }
        )
    }

    assistant = VirtualAssistant()
    response = assistant.handle_request(mock_event)
    status_code = response.get("statusCode")
    body = json.loads(response.get("body", "{}"))

    print("\n===== RESPONSE =====")
    print(f"Status Code: {status_code}")
    print("\nResponse Body:")
    print(json.dumps(body, indent=2))

    # Print just the response text for convenience
    if "response" in body:
        print("\nResponse Text:")
        print(body["response"])
