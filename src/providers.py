from abc import ABC, abstractmethod
from schemas import BedrockSuccess

class PromptProvider(ABC):
    """
    Shared interface for anything that can answer a prompt.

    Implementations:
    - BedrockProvider: real AWS bedrock calls
    - ReplayProvider: fakse response from JSONL
    """

    @abstractmethod
    def send(self, prompt: str, model_id: str | None = None) -> BedrockSuccess:
        pass
