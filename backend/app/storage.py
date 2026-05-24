"""Azure Blob Storage service with local fallback for development."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from .config import settings

LOCAL_STORAGE_DIR = Path("/tmp/rashid_reports")


class BlobStorageService:
    def __init__(self):
        self._conn_str = settings.azure_storage_connection_string
        self._container = settings.azure_storage_container
        self._use_azure = bool(self._conn_str)

        if not self._use_azure:
            LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    async def upload_report(self, file_bytes: bytes, blob_name: str, content_type: str) -> str:
        if self._use_azure:
            from azure.storage.blob.aio import BlobServiceClient
            from azure.storage.blob import ContentSettings

            async with BlobServiceClient.from_connection_string(self._conn_str) as client:
                container = client.get_container_client(self._container)
                await container.upload_blob(
                    blob_name,
                    file_bytes,
                    content_settings=ContentSettings(content_type=content_type),
                    overwrite=True,
                )
            return blob_name
        else:
            path = LOCAL_STORAGE_DIR / blob_name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(file_bytes)
            return blob_name

    def get_download_url(self, blob_name: str, expiry_hours: int = 24) -> str:
        if self._use_azure:
            from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

            client = BlobServiceClient.from_connection_string(self._conn_str)
            account_name = client.account_name
            account_key = client.credential.account_key

            sas = generate_blob_sas(
                account_name=account_name,
                container_name=self._container,
                blob_name=blob_name,
                account_key=account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc) + timedelta(hours=expiry_hours),
            )
            return f"https://{account_name}.blob.core.windows.net/{self._container}/{blob_name}?{sas}"
        else:
            return f"/api/reports/files/{blob_name}"

    async def delete_report(self, blob_name: str) -> None:
        if self._use_azure:
            from azure.storage.blob.aio import BlobServiceClient

            async with BlobServiceClient.from_connection_string(self._conn_str) as client:
                container = client.get_container_client(self._container)
                await container.delete_blob(blob_name)
        else:
            path = LOCAL_STORAGE_DIR / blob_name
            if path.exists():
                path.unlink()
