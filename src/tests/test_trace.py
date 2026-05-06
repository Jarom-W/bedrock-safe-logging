#Test trace creation and durability

from trace import get_or_create_trace_id

def test_generates_trace_id():
    trace_id = get_or_create_trace_id()
    assert isinstance(trace_id, str)
    assert len(trace_id) > 10

def test_reuses_incoming_trace_id():
    trace_id = get_or_create_trace_id("fixed-trace-id")
    assert trace_id == "fixed-trace-id"
