import asyncio
from io import BytesIO
from uuid import UUID, uuid4
from pathlib import Path

import boto3
from botocore.config import Config

from src.application.content.service import ContentStorage, UploadPayload


class S3ContentStorage(ContentStorage):
    def __init__(self, bucket: str, region: str, access_key: str, secret_key: str):
        self._bucket = bucket
        self._client = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=f"https://s3.{region}.amazonaws.com",
            config=Config(signature_version="s3v4"),
        )

    async def store(self, submission_id: UUID, payload: UploadPayload) -> str:
        suffix = Path(payload.filename).suffix.lower()
        storage_key = f"{submission_id}/{uuid4().hex}{suffix}"
        await asyncio.to_thread(
            self._client.put_object,
            Bucket=self._bucket,
            Key=storage_key,
            Body=payload.content,
            ContentType=payload.mime_type,
        )
        return storage_key

    async def delete(self, storage_key: str) -> None:
        await asyncio.to_thread(
            self._client.delete_object,
            Bucket=self._bucket,
            Key=storage_key,
        )

    async def read_bytes(self, storage_key: str) -> bytes:
        buf = BytesIO()
        await asyncio.to_thread(
            self._client.download_fileobj,
            self._bucket,
            storage_key,
            buf,
        )
        return buf.getvalue()

    async def get_download_url(self, storage_key: str) -> str | None:
        return await asyncio.to_thread(
            self._client.generate_presigned_url,
            "get_object",
            Params={"Bucket": self._bucket, "Key": storage_key},
            ExpiresIn=3600,
        )
