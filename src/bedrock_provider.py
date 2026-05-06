from schemas import BedrockSuccess
from bedrock_client import send_prompt
from providers import PromptProvider

class BedrockProvider(PromptProvider):
    """
    Real provider that calls AWS Bedrock
    """
    def send(self, prompt: str, model_id: str | None = None) -> BedrockSuccess:
        return send_prompt(prompt=prompt, model_id=model_id)
