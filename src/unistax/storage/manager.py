"""Storage manager."""

from typing import Optional
from dataclasses import dataclass
from unistax.storage.backends import StorageBackend


@dataclass
class StorageConfig:
    """Storage configuration."""

    backend: str  # local, s3, azure, gcs
    base_path: str = "/"
    bucket: Optional[str] = None
    region: Optional[str] = None
    access_key: Optional[str] = None
    secret_key: Optional[str] = None


class StorageManager:
    """Manage file storage."""

    def __init__(self, backend: StorageBackend):
        """Initialize storage manager.

        Args:
            backend: Storage backend
        """
        self.backend = backend

    def upload(self, source_path: str, dest_path: str) -> str:
        """Upload file.

        Args:
            source_path: Local file path
            dest_path: Destination path

        Returns:
            URL of uploaded file
        """
        return self.backend.upload(source_path, dest_path)

    def download(self, source_path: str, dest_path: str):
        """Download file.

        Args:
            source_path: Storage file path
            dest_path: Local destination path
        """
        self.backend.download(source_path, dest_path)

    def delete(self, path: str):
        """Delete file.

        Args:
            path: File path
        """
        self.backend.delete(path)

    def exists(self, path: str) -> bool:
        """Check if file exists.

        Args:
            path: File path

        Returns:
            True if exists
        """
        return self.backend.exists(path)

    def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get presigned URL.

        Args:
            path: File path
            expires_in: URL expiration (seconds)

        Returns:
            Presigned URL
        """
        return self.backend.get_url(path, expires_in)
