"""Storage service abstraction and local filesystem implementation."""

import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Union, Optional

from app.core.config import get_settings
from app.core.security import safe_join

settings = get_settings()


class StorageService(ABC):
    """Abstract storage service interface."""

    @abstractmethod
    def save_file(
        self, file_data: Union[bytes, BinaryIO], filename: str, subfolder: str = "original"
    ) -> str:
        """Saves file and returns relative or storage path."""
        pass

    @abstractmethod
    def get_file_path(self, filename: str, subfolder: str = "original") -> str:
        """Returns absolute filesystem path for local access."""
        pass

    @abstractmethod
    def delete_file(self, filename: str, subfolder: str = "original") -> bool:
        """Deletes a file from storage."""
        pass

    @abstractmethod
    def file_exists(self, filename: str, subfolder: str = "original") -> bool:
        """Checks if a file exists in storage."""
        pass


class LocalStorageService(StorageService):
    """Local filesystem storage implementation."""

    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.STORAGE_BASE_PATH).resolve()
        self.original_dir = self.base_path / "original"
        self.pages_dir = self.base_path / "pages"
        self.processed_dir = self.base_path / "processed"

        # Ensure directories exist
        self.original_dir.mkdir(parents=True, exist_ok=True)
        self.pages_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def _get_target_dir(self, subfolder: str) -> Path:
        if subfolder == "original":
            return self.original_dir
        elif subfolder == "pages":
            return self.pages_dir
        elif subfolder == "processed":
            return self.processed_dir
        else:
            target = safe_join(self.base_path, subfolder)
            target.mkdir(parents=True, exist_ok=True)
            return target

    def save_file(
        self, file_data: Union[bytes, BinaryIO], filename: str, subfolder: str = "original"
    ) -> str:
        target_dir = self._get_target_dir(subfolder)
        target_path = safe_join(target_dir, filename)

        if isinstance(file_data, bytes):
            with open(target_path, "wb") as f:
                f.write(file_data)
        else:
            file_data.seek(0)
            with open(target_path, "wb") as f:
                shutil.copyfileobj(file_data, f)

        return str(target_path)

    def get_file_path(self, filename: str, subfolder: str = "original") -> str:
        target_dir = self._get_target_dir(subfolder)
        target_path = safe_join(target_dir, filename)
        return str(target_path)

    def delete_file(self, filename: str, subfolder: str = "original") -> bool:
        target_dir = self._get_target_dir(subfolder)
        target_path = safe_join(target_dir, filename)
        if target_path.exists():
            target_path.unlink()
            return True
        return False

    def file_exists(self, filename: str, subfolder: str = "original") -> bool:
        target_dir = self._get_target_dir(subfolder)
        target_path = safe_join(target_dir, filename)
        return target_path.exists()


_storage_instance: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Singleton getter for StorageService."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = LocalStorageService()
    return _storage_instance
