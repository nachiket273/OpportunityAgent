"""
Dummy client for testing purposes.
"""

from typing import Any

from pydantic import BaseModel

from opportunity_agent.llm.client import LLMClient


class FakeLLMClient(LLMClient):
    """
    A fake LLM client that simulates responses for testing.
    """

    def __init__(
        self,
        responses: list[dict[str, Any]] | None = None,
        exception_to_raise: Exception | None = None,
    ) -> None:
        """
        Initialize the fake LLM client.

        Args:
            responses (list[dict[str, Any]] | None): A list of responses to return for
            each call.
            exception_to_raise (Exception | None): An exception to raise instead of
            returning a response.
        """
        self.responses = responses or []
        self.exception_to_raise = exception_to_raise
        self.call_count = 0
        self.recorded_prompts: list[str] = []
        self.recorded_texts: list[str] = []

    def generate_json(
        self,
        prompt: str,
        text: str,
        response_schema: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        """
        Simulate generating a JSON response from the LLM.

        Args:
            prompt (str): The prompt to send to the LLM.
            text (str): The text to send to the LLM.
            response_schema (Type[BaseModel] | None):
                The schema for the expected response.
        """
        self.call_count += 1
        self.recorded_prompts.append(prompt)
        self.recorded_texts.append(text)

        # 1. Simulate raising an exception if specified
        if self.exception_to_raise:
            raise self.exception_to_raise

        # 2. Return pre-canned responses if available
        if self.responses:
            # Pop the first response or return the last one if out of responses
            if len(self.responses) > 1:
                return self.responses.pop(0)
            return self.responses[0]

        # 3. Return a default response if no responses are specified
        return {}
