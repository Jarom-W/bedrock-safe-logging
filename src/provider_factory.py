from config import settings
from bedrock_provider import BedrockProvider
from providers import PromptProvider
from replay_provider import ReplayProvider

def get_provider() -> PromptProvider:
    """
    Choose the active provider from config.
    """

    mode = settings.provider_mode.lower().strip()

    if mode == "live":
        return BedrockProvider()
    if mode == "replay":
        return ReplayProvider()

    raise ValueError(f"Unknown PROVIDER MODE {settings.provider_mode}")
