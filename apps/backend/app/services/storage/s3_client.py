import uuid
from datetime import datetime, timedelta, timezone

import boto3
from botocore.config import Config

from app.core.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )


def generate_presigned_upload_url(filename: str, user_id: uuid.UUID, expiry_seconds: int = 3600) -> tuple[str, str]:
    key = f"uploads/{user_id}/{uuid.uuid4()}/{filename}"
    client = get_s3_client()
    url = client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.s3_bucket_name,
            "Key": key,
            "ContentType": "application/pdf",
        },
        ExpiresIn=expiry_seconds,
    )
    return url, key


def generate_presigned_download_url(s3_key: str, expiry_seconds: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": s3_key},
        ExpiresIn=expiry_seconds,
    )


def delete_object(s3_key: str) -> None:
    client = get_s3_client()
    client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)
