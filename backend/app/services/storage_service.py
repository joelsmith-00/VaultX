"""S3/MinIO storage wrapper for VaultX."""
import boto3
import asyncio
from typing import Optional

from app.config import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name=settings.S3_REGION,
    )


def _put_object(key: str, data: bytes, content_type: Optional[str] = None):
    client = _client()
    kwargs = {"Bucket": settings.S3_BUCKET_NAME, "Key": key, "Body": data}
    if content_type:
        kwargs["ContentType"] = content_type
    client.put_object(**kwargs)


def _delete_object(key: str):
    client = _client()
    client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=key)


async def upload_bytes(key: str, data: bytes, content_type: Optional[str] = None):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _put_object, key, data, content_type)


async def delete_object(key: str):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _delete_object, key)


def build_s3_url(key: str) -> str:
    # Return a public URL for local MinIO; production may use presigned URLs
    return f"{settings.S3_ENDPOINT_URL.rstrip('/')}" + f"/{settings.S3_BUCKET_NAME}/{key}"


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    client = _client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
        ExpiresIn=expires_in,
    )
