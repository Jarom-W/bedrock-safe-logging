import os
import pytest
from fastapi.testclient import TestClient
from main import app
from logging_utils import log_event

pytestmark = pytest.mark.integration

def test_prompt_integration() -> None:

    client = TestClient(app)

    response = client.post(
        "/prompt",
        json={"prompt": "Reply with exactly: BEDROCK_SMOKE_TEST_OK"},
    )

    assert response.status_code == 200
    body = response.json()

    assert "trace_id" in body
    assert "output_text" in body
    assert isinstance(body["output_text"], str)

    input_tokens = body.get("input_tokens") or 0
    output_tokens = body.get("output_tokens") or 0
    model_id = body.get("model_id", "unknown")

    # Nova Lite pricing ex:
    # $0.06 / 1M input tokens
    # $0.24 / 1M output tokens
    estimated_cost_usd = (
        (input_tokens / 1_000_000) * 0.06
        + (output_tokens / 1_000_000) * 0.24
    )

    log_event(
        "INFO",
        "Running Bedrock Integration Test",
        event="integration_test_completed",
        env="integration",
        model_id=model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=round(estimated_cost_usd, 8),
    )
    log_event(
        "INFO",
        "Running Bedrock Integration Test",
        event="integration_test_completed",
        env="integration"
    )

