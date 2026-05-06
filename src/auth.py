import boto3
from botocore.exceptions import ClientError

from config import settings
from errors import ServiceError
from trace import get_trace_id


def build_session(profile: str | None = None, region: str | None = None) -> boto3.Session:
    return boto3.Session(
        profile_name=profile or settings.aws_profile,
        region_name=region or settings.aws_region,
    ) # Return an AWS session


def verify_auth(profile: str | None = None, region: str | None = None) -> dict:
    session = build_session(profile=profile, region=region)
    sts = session.client("sts")

    try:
        return sts.get_caller_identity() #Try to verify with sts get-caller-identity
    except ClientError as exc:
        raise ServiceError(
            error_type="auth_failure",
            message="AWS authentication failed. Run aws sso login or verify your named profile.",
            trace_id=get_trace_id(),
            status_code=401,
            details={"aws_error": str(exc)},
        ) from exc
