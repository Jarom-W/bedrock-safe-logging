from dataclasses import dataclass
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError


@dataclass
class ServiceError(Exception): #Map the error attributes to a json object that has set structure
    error_type: str
    message: str
    trace_id: str
    status_code: int
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "type": self.error_type,
                "message": self.message,
                "trace_id": self.trace_id,
            }
        }

#Map errors to our ServiceError class above to have standardized output

def map_bedrock_error(exc: Exception, trace_id: str) -> ServiceError:
    if isinstance(exc, ClientError):
        code = exc.response.get("Error", {}).get("Code", "Unknown")
        message = exc.response.get("Error", {}).get("Message", str(exc))

        if code in {"AccessDeniedException", "UnrecognizedClientException", "ExpiredTokenException"}:
            return ServiceError(
                error_type="auth_failure",
                message="Authentication or authorization failed for AWS/Bedrock.",
                trace_id=trace_id,
                status_code=401,
                details={"aws_error_code": code, "aws_message": message},
            )

        if code in {"ThrottlingException", "TooManyRequestsException"}:
            return ServiceError(
                error_type="throttling",
                message="Request was throttled by Bedrock.",
                trace_id=trace_id,
                status_code=429,
                details={"aws_error_code": code, "aws_message": message},
            )

        if code in {"ValidationException"}:
            return ServiceError(
                error_type="invalid_payload",
                message="The request payload or model configuration is invalid.",
                trace_id=trace_id,
                status_code=400,
                details={"aws_error_code": code, "aws_message": message},
            )

        return ServiceError(
            error_type="upstream_error",
            message="Bedrock returned an upstream service error.",
            trace_id=trace_id,
            status_code=502,
            details={"aws_error_code": code, "aws_message": message},
        )

    if isinstance(exc, BotoCoreError):
        return ServiceError(
            error_type="auth_failure",
            message="AWS SDK failed before a Bedrock response was returned.",
            trace_id=trace_id,
            status_code=401,
            details={"sdk_error": str(exc)},
        )

    return ServiceError(
        error_type="internal_error",
        message="An unexpected internal error occurred.",
        trace_id=trace_id,
        status_code=500,
        details={"error": str(exc)},
    )
