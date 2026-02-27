# src/domain/collaboration/value_objects/file_attachment.py
"""Value Object pour les pièces jointes aux lettres."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class FileType(Enum):
    """Types de fichiers autorisés."""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


@dataclass(frozen=True)
class FileAttachment:
    """
    Value Object représentant une pièce jointe.
    
    Immuable, contient les métadonnées du fichier.
    """
    url: str
    file_type: FileType
    original_name: str
    size_bytes: int
    mime_type: str
    
    ALLOWED_EXTENSIONS = {
        FileType.IMAGE: {"png", "jpg", "jpeg", "gif", "webp"},
        FileType.AUDIO: {"mp3", "wav", "m4a", "ogg"},
        FileType.VIDEO: {"mp4", "webm", "mov"},
        FileType.DOCUMENT: {"pdf"},
    }
    
    MAX_SIZE_BYTES = 16 * 1024 * 1024  # 16 MB
    
    @classmethod
    def create(
        cls,
        url: str,
        original_name: str,
        size_bytes: int,
        mime_type: str
    ) -> "FileAttachment":
        """Factory method avec validation."""
        extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
        file_type = cls._detect_file_type(extension)
        
        if file_type is None:
            raise ValueError(f"Extension de fichier non autorisée: {extension}")
        
        if size_bytes > cls.MAX_SIZE_BYTES:
            raise ValueError(f"Fichier trop volumineux: {size_bytes} bytes (max: {cls.MAX_SIZE_BYTES})")
        
        return cls(
            url=url,
            file_type=file_type,
            original_name=original_name,
            size_bytes=size_bytes,
            mime_type=mime_type
        )
    
    @classmethod
    def _detect_file_type(cls, extension: str) -> Optional[FileType]:
        """Détecte le type de fichier depuis l'extension."""
        for file_type, extensions in cls.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return file_type
        return None
    
    @property
    def size_mb(self) -> float:
        """Retourne la taille en mégaoctets."""
        return round(self.size_bytes / (1024 * 1024), 2)
