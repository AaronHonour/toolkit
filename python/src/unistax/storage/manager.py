"""Storage manager."""

from dataclasses import dataclass

from unistax.storage.backends import StorageBackend


@dataclass
class StorageConfig:
    """Storage configuration."""

    backend: str  # local, s3, azure, gcs
    base_path: str = "/"
    bucket: str | None = None
    region: str | None = None
    access_key: str | None = None
    secret_key: str | None = None


class StorageManager:
    """Manage file storage."""

    def __init__(self, backend: StorageBackend) -> None:
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

    def download(self, source_path: str, dest_path: str) -> None:
        """Download file.

        Args:
            source_path: Storage file path
            dest_path: Local destination path
        """
        self.backend.download(source_path, dest_path)

    def delete(self, path: str) -> None:
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
