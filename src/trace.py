import uuid #Universally Unique Identifiers 128 bit
from contextvars import ContextVar
from typing import Optional

trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="-") # Context vars store variables that must be consistent at the top-lvel of the module

def generate_trace_id() -> str:
    return str(uuid.uuid4()) #Generate new unique trace for request

def set_trace_id(trace_id: str) -> None:
    trace_id_ctx.set(trace_id) #Set the trace_id attribute of the trace_id_ctx ContextVar class as the uuid we generated

def get_trace_id() -> str:
    return trace_id_ctx.get() #Helper function to extract the trace_id from the ContextVar class within trace_id_ctx

def get_or_create_trace_id(incoming_trace_id: Optional[str] = None) -> str:
    trace_id = incoming_trace_id.strip() if incoming_trace_id else generate_trace_id() #If trace id is passed, return same trace id, else mint anew one.
    set_trace_id(trace_id)
    return trace_id
