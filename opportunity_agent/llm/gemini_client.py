import json
import os

from google import genai
from pydantic import BaseModel

from opportunity_agent.llm.client import LLMClient


class GeminiClient(LLMClient):
    def __init__(self, api_key: str | None = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key must be provided either as an argument"
                "or through the GEMINI_API_KEY environment variable."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model = model

    def generate_json(
        self, prompt: str, text: str, response_schema: type[BaseModel]
    ) -> dict:
        """
        Generate a JSON response based on the provided prompt and text.
        """
        full_content = f"{prompt}\n\nDocument Text:\n{text}"

        config_args = {
            "response_mime_type": "application/json",
            "temperature": 0.7,
        }

        if response_schema:
            config_args["response_schema"] = response_schema

        response = self.client.generate_content(
            model=self.model,
            content=full_content,
            config=genai.types.GenerateContentConfig(**config_args),
        )

        return json.loads(response.text)
