# src/infrastructure/storage/__init__.py
"""Module de stockage de fichiers."""

from src.infrastructure.storage.file_storage import FileStorageService, StoredFile, get_file_storage

__all__ = ['FileStorageService', 'StoredFile', 'get_file_storage']
