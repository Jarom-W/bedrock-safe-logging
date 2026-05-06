import time
from typing import Any

from config import settings
from jsonl_loader import load_jsonl
from logging_utils import log_event
from providers import PromptProvider
from schemas import BedrockSuccess
from trace import get_trace_id


class ReplayProvider(PromptProvider):
    """
    Fake provider that returns responses from a JSONL file.

    This lets us test the same service path without calling Bedrock.
    """

    def __init__(self, jsonl_path: str | None = None) -> None:
        self.jsonl_path = jsonl_path or settings.replay_jsonl_path
        self.events = load_jsonl(self.jsonl_path)
        self.index = 0

        if not self.events:
            raise ValueError(f"Replay file contains no events: {self.jsonl_path}")

    def send(self, prompt: str, model_id: str | None = None) -> BedrockSuccess:
        start = time.perf_counter()
        trace_id = get_trace_id()
        active_model_id = model_id or settings.bedrock_model_id

        log_event(
            "INFO",
            "Starting replay request",
            event="bedrock_request_started",
            model_id=active_model_id,
            status="started",
            aws_profile=settings.aws_profile,
            aws_region=settings.aws_region,
        )

        event = self._next_event()
        response = event.get("response", {})
        output_text = response.get("output_text", "")

        latency_ms = int((time.perf_counter() - start) * 1000)

        log_event(
            "INFO",
            "Replay request completed",
            event="bedrock_request_completed",
            model_id=active_model_id,
            status="success",
            latency_ms=latency_ms,
            input_tokens=None,
            output_tokens=None,
            stop_reason="replay",
            aws_profile=settings.aws_profile,
            aws_region=settings.aws_region,
        )

        return BedrockSuccess(
            trace_id=trace_id,
            model_id=active_model_id,
            output_text=output_text,
            latency_ms=latency_ms,
            input_tokens=None,
            output_tokens=None,
            stop_reason="replay",
        )

    def _next_event(self) -> dict[str, Any]:
        """
        Return the next event and loop back to the beginning when done.
        """
        event = self.events[self.index]
        self.index = (self.index + 1) % len(self.events)
        return event
