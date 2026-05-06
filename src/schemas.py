#This file defines set structures for prompts, sucess messages, error messages, and error responses to allow for safe logging
#Trace id is included in all structures

from typing import Optional
from pydantic import BaseModel, Field

class PromptRequest(BaseModel):
    prompt: str = Field(min_length=1)
    model_id: Optional[str] = None
    trace_id: Optional[str] = None


class BedrockSuccess(BaseModel):
    trace_id: str
    model_id: str
    output_text: str
    latency_ms: int
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    stop_reason: Optional[str] = None


class ErrorBody(BaseModel):
    type: str
    message: str
    trace_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody
