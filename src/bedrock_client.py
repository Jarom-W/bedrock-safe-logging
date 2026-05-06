
from __future__ import annotations
import time
import re
from typing import Any
from botocore.exceptions import ClientError
from auth import build_session
from config import settings
from errors import ServiceError, map_bedrock_error
from logging_utils import log_event
from schemas import BedrockSuccess
from trace import get_trace_id
from dotenv import dotenv_values;

env_vars = dotenv_values(".env"); # Serialize Environment into a json object

#Regex patterns for email, ssn ,aws keys, bearer tokens, and generic secrets
# Long-term and temporary AWS access key IDs.
AWS_ACCESS_KEY_ID_RE = re.compile(
    r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"
)

# Broader AWS principal/resource unique IDs.
# Useful for logs because AWS sometimes exposes role/user/account identifiers.
AWS_UNIQUE_ID_RE = re.compile(
    r"\b(?:A3T|ABIA|ACCA|AGPA|AIDA|AIPA|AKIA|ANPA|ANVA|AROA|ASCA|ASIA)[A-Z0-9]{16}\b"
)

# AWS secret access keys are commonly 40 chars from this character set.
# This can false-positive, so use carefully.
AWS_SECRET_ACCESS_KEY_RE = re.compile(
    r"(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"
)

# Explicit env/key assignment forms.
AWS_ACCESS_KEY_ASSIGNMENT_RE = re.compile(
    r"""(?ix)
    \b(
        aws_access_key_id |
        aws_secret_access_key |
        aws_session_token |
        aws_security_token
    )\b
    \s*[:=]\s*
    ["']?
    ([^\s"',;]+)
    """
)

# AWS session tokens can be long and variable.
# Better detected by key name/context than pure value shape.
AWS_SESSION_TOKEN_ASSIGNMENT_RE = re.compile(
    r"""(?ix)
    \b(aws_session_token|aws_security_token)\b
    \s*[:=]\s*
    ["']?
    ([A-Za-z0-9/+=._-]{20,})
    """
)

# Amazon Resource Names are not always secrets, but they can expose account IDs/resource names.
# I would mask only if your policy says account/resource identifiers should not print.
AWS_ARN_RE = re.compile(
    r"\barn:aws[a-zA-Z-]*:[^\s\"']+\b"
)

# AWS account IDs are not secrets by themselves, but can be sensitive metadata.
AWS_ACCOUNT_ID_RE = re.compile(
    r"\b\d{12}\b"
)
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
AWS_ACCESS_KEY_ID_RE = re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")
BEARER_TOKEN_RE = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9\-._~+/]+=*")
GENERIC_SECRET_ASSIGNMENT_RE = re.compile(
    r"""(?ix)
    \b(api[_-]?key|secret|token|password)\b
    \s*[:=]\s*
    ["']?
    ([^\s"',;]+)
    """
)

PRIVATE_KEY_HEADER_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |)?PRIVATE KEY-----"
)

def _mask_sensitive_information(prompt: str) -> str:
    """Function to mark sensitive, previously known patterns and mask existing environment variables in logging."""
    masked = prompt
    
    for key, value in env_vars.items(): #Iterate through each env variable
        if value in masked and value not in ["True", "true", "false", "False", "INFO", "ERROR", "WARNING"]: #If env var is in the prompt, we replace it with asterisks
            masked = masked.replace(value, "*" * len(value))

    masked = AWS_ACCESS_KEY_ASSIGNMENT_RE.sub(
        lambda m: f"{m.group(1)}=[MASKED AWS SECRET]",
        masked,
    )

    masked = AWS_SESSION_TOKEN_ASSIGNMENT_RE.sub(
        lambda m: f"{m.group(1)}=[MASKED AWS TOKEN]",
        masked,
    )

    # Value-shape patterns.
    masked = AWS_ACCESS_KEY_ID_RE.sub("[MASKED AWS ACCESS KEY ID]", masked)
    masked = AWS_UNIQUE_ID_RE.sub("[MASKED AWS UNIQUE ID]", masked)
    masked = AWS_SECRET_ACCESS_KEY_RE.sub("[MASKED AWS SECRET ACCESS KEY]", masked)    
    masked = EMAIL_RE.sub("*****@****", masked)
    masked = SSN_RE.sub("***-**-****", masked)
    masked = AWS_ACCESS_KEY_ID_RE.sub("*****", masked)
    masked = BEARER_TOKEN_RE.sub("*****", masked)
    masked = PRIVATE_KEY_HEADER_RE.sub("*****", masked)
    masked = GENERIC_SECRET_ASSIGNMENT_RE.sub(
        lambda m: f"{m.group(1)}=[MASKED SECRET]",
        masked,
    )
    return masked

#Toggle hellper functions if prompt is to be loged based on env var
def _build_log_prompt_fields(prompt: str) -> dict[str, Any]:
    if settings.safe_logging and not settings.log_prompts:
        return {"prompt_logged": False}
    else:
        return {
            "prompt_logged": True,
            "prompt": _mask_sensitive_information(prompt),
        }

#Log i/o tokens
def _extract_usage(response: dict[str, Any]) -> dict[str, Any]:
    usage = response.get("usage", {})
    return {
        "input_tokens": usage.get("inputTokens"),
        "output_tokens": usage.get("outputTokens"),
    }

#Helper to extract the model's response
def _extract_text(response: dict[str, Any]) -> str:
    content = response.get("output", {}).get("message", {}).get("content", [])
    texts = [part["text"] for part in content if isinstance(part, dict) and "text" in part]
    if not texts:
        return ""
    return "\n".join(texts)

#Send prompt and map response - whether error or not into a logging shape we've defined
def send_prompt(
    prompt: str,
    model_id: str | None = None,
    profile: str | None = None,
    region: str | None = None,
) -> BedrockSuccess:
    active_model_id = model_id or settings.bedrock_model_id #Extract values from settings from config.py
    active_profile = profile or settings.aws_profile
    active_region = region or settings.aws_region
    trace_id = get_trace_id() #Get or create new trace id

    session = build_session(profile=active_profile, region=active_region) #Build session in AWS
    client = session.client("bedrock-runtime")#Declare Bedrock client

    start = time.perf_counter() #Monotonic timer for short durations.

    log_event(
        "INFO",
        "Starting Bedrock request",
        event="bedrock_request_started",
        model_id=active_model_id,
        status="started",
        aws_profile=active_profile,
        aws_region=active_region,
        **_build_log_prompt_fields(prompt),
    )

    try:
        response = client.converse(
            modelId=active_model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        usage = _extract_usage(response)
        output_text = _extract_text(response)
        stop_reason = response.get("stopReason")

        log_event(
            "INFO",
            "Bedrock request completed",
            event="bedrock_request_completed",
            model_id=active_model_id,
            status="success",
            latency_ms=latency_ms,
            stop_reason=stop_reason,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            aws_profile=active_profile,
            aws_region=active_region,
        )

        return BedrockSuccess(
            trace_id=trace_id,
            model_id=active_model_id,
            output_text=output_text,
            latency_ms=latency_ms,
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
            stop_reason=stop_reason,
        )

    except (ClientError, Exception) as exc:
        latency_ms = int((time.perf_counter() - start) * 1000)
        mapped = map_bedrock_error(exc, trace_id=trace_id)

        log_event(
            "ERROR",
            f"Bedrock request failed: {exec.__class__.__name__}: {exc}",
            event="bedrock_request_failed",
            model_id=active_model_id,
            status="error",
            latency_ms=latency_ms,
            error_type=mapped.error_type,
            aws_profile=active_profile,
            aws_region=active_region,
        )

        raise mapped from exc #Raise the error mapped to our structured error logging 
