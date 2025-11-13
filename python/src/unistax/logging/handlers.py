"""Custom log handlers.

Provides specialized handlers for enterprise logging needs.
"""

import gzip
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path


class RotatingFileHandlerWithCompression(RotatingFileHandler):
    """Rotating file handler with gzip compression.

    Automatically compresses rotated log files to save disk space.
    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: str | None = None,
        delay: bool = False,
        compress: bool = True,
    ) -> None:
        """Initialize rotating file handler with compression.

        Args:
            filename: Log file name
            mode: File mode
            maxBytes: Maximum file size before rotation
            backupCount: Number of backup files to keep
            encoding: File encoding
            delay: Delay file opening
            compress: Whether to compress rotated files
        """
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.compress = compress

    def doRollover(self) -> None:
        """Perform log rotation with optional compression.

        Overrides parent method to add compression.
        """
        # Close current file
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore

        # Rotate files
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = self.rotation_filename(f"{self.baseFilename}.{i}")
                dfn = self.rotation_filename(f"{self.baseFilename}.{i + 1}")

                if Path(sfn).exists():
                    if Path(dfn).exists():
                        Path(dfn).unlink()
                    Path(sfn).rename(dfn)

            # Move current file to .1
            dfn = self.rotation_filename(f"{self.baseFilename}.1")
            if Path(dfn).exists():
                Path(dfn).unlink()

            # Close current stream before rename
            self.rotate(self.baseFilename, dfn)

            # Compress the rotated file
            if self.compress:
                self._compress_file(dfn)

        # Open new file
        if not self.delay:
            self.stream = self._open()

    def _compress_file(self, filename: str) -> None:
        """Compress a log file using gzip.

        Args:
            filename: File to compress
        """
        compressed_filename = f"{filename}.gz"

        try:
            with open(filename, "rb") as f_in:
                with gzip.open(compressed_filename, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove original file
            Path(filename).unlink()
        except Exception as e:
            # Log compression error but don't fail rotation
            print(f"Error compressing log file {filename}: {e}")
