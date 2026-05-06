from bedrock_client import _mask_sensitive_information

def test_masks_email() -> None:
    text = "Contact jane.doe@example.com for help"
    result = _mask_sensitive_information(text)
    assert "**@**" in result


def test_masks_ssn() -> None:
    text = "Patient SSN is 123-45-6789"
    result = _mask_sensitive_information(text)
    assert "***-**-****" in result


def test_masks_aws_access_key_id() -> None:
    text = "Use AKIAABCDEFGHIJKLMNOP"
    result = _mask_sensitive_information(text)
    assert "[MASKED AWS ACCESS KEY ID]" in result


def test_masks_bearer_token() -> None:
    text = "Authorization: Bearer abc.def.ghi"
    result = _mask_sensitive_information(text)
    assert "*****" in result


def test_masks_secret_assignment() -> None:
    text = 'api_key=super-secret-value'
    result = _mask_sensitive_information(text)
    assert result == "api_key=[MASKED SECRET]"


def test_masks_private_key_header() -> None:
    text = "-----BEGIN PRIVATE KEY-----"
    result = _mask_sensitive_information(text)
    assert "*****" in result


def test_masks_multiple_patterns() -> None:
    text = (
        "Email jane@example.com "
        "SSN 123-45-6789 "
        "token=my-secret-token"
    )
    result = _mask_sensitive_information(text)
    assert "**@**" in result
    assert "***-**-****" in result
    assert "[MASKED SECRET]" in result


def test_leaves_benign_text_unchanged() -> None:
    text = "Summarize this support request."
    result = _mask_sensitive_information(text)
    assert result == text
