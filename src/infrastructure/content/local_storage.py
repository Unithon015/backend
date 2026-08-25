import asyncio
from pathlib import Path
from uuid import UUID, uuid4

from src.application.content.service import ContentStorage, UploadPayload


class LocalContentStorage(ContentStorage):
    """MVP adapter. Replace with an S3 adapter before multi-instance deployment."""

    def __init__(self, base_directory: str):
        self._base_directory = Path(base_directory).resolve()

    async def store(self, submission_id: UUID, payload: UploadPayload) -> str:
        suffix = Path(payload.filename).suffix.lower()
        storage_key = f"{submission_id}/{uuid4().hex}{suffix}"
        destination = self._resolve(storage_key)
        await asyncio.to_thread(destination.parent.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(destination.write_bytes, payload.content)
        return storage_key

    async def delete(self, storage_key: str) -> None:
        destination = self._resolve(storage_key)
        if destination.exists():
            await asyncio.to_thread(destination.unlink)

    def resolve_for_download(self, storage_key: str) -> Path:
        return self._resolve(storage_key)

    def _resolve(self, storage_key: str) -> Path:
        destination = (self._base_directory / storage_key).resolve()
        if not destination.is_relative_to(self._base_directory):
            raise ValueError("Invalid storage key")
        return destination
