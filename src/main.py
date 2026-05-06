from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse

from auth import verify_auth
from config import settings
from errors import ServiceError
from provider_factory import get_provider
from schemas import PromptRequest
from trace import get_or_create_trace_id

app = FastAPI(title="Bedrock Service")


@app.get("/")
def root() -> dict:
    return {
        "service": "bedrock-service",
        "status": "running",
        "provider_mode": settings.provider_mode,
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/auth-check")
def auth_check(x_trace_id: str | None = Header(default=None)) -> dict:
    trace_id = get_or_create_trace_id(x_trace_id)

    identity = verify_auth()

    return {
        "trace_id": trace_id,
        "account": identity["Account"],
        "arn": identity["Arn"],
        "user_id": identity["UserId"],
        "aws_profile": settings.aws_profile,
        "aws_region": settings.aws_region,
    }


@app.post("/prompt")
def prompt(
    request_body: PromptRequest,
    x_trace_id: str | None = Header(default=None),
) -> dict:
    trace_id = get_or_create_trace_id(x_trace_id or request_body.trace_id)

    provider = get_provider()

    result = provider.send(
        prompt=request_body.prompt,
        model_id=request_body.model_id,
    )

    response = result.model_dump()
    response["trace_id"] = trace_id

    return response


@app.exception_handler(ServiceError)
def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    trace_id = get_or_create_trace_id()

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "internal_error",
                "message": "An unexpected internal error occurred.",
                "trace_id": trace_id,
            }
        },
    )
