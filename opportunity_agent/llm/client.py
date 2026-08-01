from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMClient(ABC):

    @abstractmethod
    def generate_json(
        self, prompt: str, text: str, response_schema: type[BaseModel]
    ) -> dict:
        """
        Generate a JSON response based on the provided prompt and text.
        """
