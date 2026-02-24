# src/infrastructure/storage/file_storage.py
"""Service de stockage de fichiers."""

import hashlib
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from werkzeug.utils import secure_filename

from src.infrastructure.config.settings import get_settings


@dataclass
class StoredFile:
    """Representation d'un fichier stocke."""
    file_id: str
    file_name: str
    file_url: str
    mime_type: str
    size: int
    checksum: str
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            'file_id': self.file_id,
            'file_name': self.file_name,
            'file_url': self.file_url,
            'mime_type': self.mime_type,
            'size': self.size,
            'checksum': self.checksum,
            'created_at': self.created_at.isoformat()
        }


class FileStorageService:
    """
    Service de stockage de fichiers local.

    Peut etre etendu pour supporter S3, MinIO, etc.
    """

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp3', 'wav', 'm4a', 'doc', 'docx', 'txt'}
    MAX_SIZE = 16 * 1024 * 1024  # 16 MB

    def __init__(self, upload_folder: Optional[str] = None):
        settings = get_settings()
        self._upload_folder = upload_folder or settings.UPLOAD_FOLDER
        self._ensure_upload_folder()

    def _ensure_upload_folder(self):
        """Cree le dossier d'upload s'il n'existe pas."""
        Path(self._upload_folder).mkdir(parents=True, exist_ok=True)

    def _allowed_file(self, filename: str) -> bool:
        """Verifie si l'extension est autorisee."""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS

    def _get_extension(self, filename: str) -> str:
        """Extrait l'extension du fichier."""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''

    def _generate_file_id(self) -> str:
        """Genere un ID unique pour le fichier."""
        return str(uuid.uuid4())

    def _compute_checksum(self, data: bytes) -> str:
        """Calcule le checksum MD5 du fichier."""
        return hashlib.md5(data).hexdigest()

    # Signatures magiques (magic bytes) pour validation du contenu
    _MAGIC_SIGNATURES = {
        'png': [b'\x89PNG\r\n\x1a\n'],
        'jpg': [b'\xff\xd8\xff'],
        'jpeg': [b'\xff\xd8\xff'],
        'gif': [b'GIF87a', b'GIF89a'],
        'pdf': [b'%PDF'],
        'mp3': [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2', b'ID3'],
        'wav': [b'RIFF'],
        'm4a': [b'\x00\x00\x00', b'ftyp'],
        'doc': [b'\xd0\xcf\x11\xe0'],
        'docx': [b'PK\x03\x04'],
    }

    def _validate_mime_content(self, file_data: bytes, extension: str) -> None:
        """Valide que le contenu du fichier correspond a l'extension declaree."""
        if extension == 'txt':
            # Les fichiers texte n'ont pas de signature magique
            try:
                file_data[:1024].decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError(
                    "Le contenu du fichier ne correspond pas a un fichier texte"
                )
            return

        signatures = self._MAGIC_SIGNATURES.get(extension)
        if not signatures:
            return  # Pas de signature connue, on accepte

        for sig in signatures:
            if file_data[:len(sig)] == sig:
                return  # Signature valide

        raise ValueError(
            f"Le contenu du fichier ne correspond pas au type {extension}. "
            f"Le fichier pourrait etre corrompu ou avoir une extension incorrecte."
        )

    def _get_mime_type(self, extension: str) -> str:
        """Determine le type MIME selon l'extension."""
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'pdf': 'application/pdf',
            'mp3': 'audio/mpeg',
            'wav': 'audio/wav',
            'm4a': 'audio/mp4',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain'
        }
        return mime_types.get(extension, 'application/octet-stream')

    def save(self, file_data: bytes, original_filename: str) -> StoredFile:
        """
        Sauvegarde un fichier.

        Args:
            file_data: Contenu binaire du fichier
            original_filename: Nom original du fichier

        Returns:
            StoredFile avec les metadonnees

        Raises:
            ValueError: Si le fichier est invalide
        """
        # Validation
        if not original_filename:
            raise ValueError("Nom de fichier manquant")

        if not self._allowed_file(original_filename):
            raise ValueError(f"Extension non autorisee. Extensions valides: {', '.join(self.ALLOWED_EXTENSIONS)}")

        if len(file_data) > self.MAX_SIZE:
            raise ValueError(f"Fichier trop volumineux. Taille max: {self.MAX_SIZE // (1024*1024)} MB")

        if len(file_data) == 0:
            raise ValueError("Fichier vide")

        # Validation du contenu (magic bytes)
        extension = self._get_extension(original_filename)
        self._validate_mime_content(file_data, extension)

        # Generer ID et chemin
        file_id = self._generate_file_id()
        extension = self._get_extension(original_filename)
        safe_filename = secure_filename(original_filename)
        stored_filename = f"{file_id}.{extension}"
        file_path = os.path.join(self._upload_folder, stored_filename)

        # Sauvegarder le fichier
        with open(file_path, 'wb') as f:
            f.write(file_data)

        # Creer les metadonnees
        return StoredFile(
            file_id=file_id,
            file_name=safe_filename,
            file_url=f"/api/v1/files/{file_id}",
            mime_type=self._get_mime_type(extension),
            size=len(file_data),
            checksum=self._compute_checksum(file_data),
            created_at=datetime.utcnow()
        )

    def get_path(self, file_id: str) -> Optional[str]:
        """
        Recupere le chemin d'un fichier.

        Args:
            file_id: ID du fichier

        Returns:
            Chemin absolu ou None si non trouve
        """
        # Chercher le fichier avec n'importe quelle extension
        for ext in self.ALLOWED_EXTENSIONS:
            file_path = os.path.join(self._upload_folder, f"{file_id}.{ext}")
            if os.path.exists(file_path):
                return file_path
        return None

    def delete(self, file_id: str) -> bool:
        """
        Supprime un fichier.

        Args:
            file_id: ID du fichier

        Returns:
            True si supprime, False si non trouve
        """
        file_path = self.get_path(file_id)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False

    def exists(self, file_id: str) -> bool:
        """Verifie si un fichier existe."""
        return self.get_path(file_id) is not None


# Instance singleton
_file_storage = None


def get_file_storage() -> FileStorageService:
    """Recupere l'instance du service de stockage."""
    global _file_storage
    if _file_storage is None:
        _file_storage = FileStorageService()
    return _file_storage
