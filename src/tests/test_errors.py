from botocore.exceptions import ClientError

from errors import map_bedrock_error


def _client_error(code: str, message: str) -> ClientError:
    return ClientError(
        error_response={"Error": {"Code": code, "Message": message}},
        operation_name="Converse",
    )


def test_maps_auth_failure():
    err = map_bedrock_error(_client_error("AccessDeniedException", "denied"), "trace-1")
    assert err.error_type == "auth_failure"
    assert err.status_code == 401


def test_maps_throttling():
    err = map_bedrock_error(_client_error("ThrottlingException", "slow down"), "trace-2")
    assert err.error_type == "throttling"
    assert err.status_code == 429


def test_maps_validation():
    err = map_bedrock_error(_client_error("ValidationException", "bad payload"), "trace-3")
    assert err.error_type == "invalid_payload"
    assert err.status_code == 400
