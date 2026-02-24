# src/infrastructure/security/path_sanitizer.py
"""Sécurisation des chemins de fichiers contre le path traversal."""

from pathlib import Path

from werkzeug.utils import secure_filename


class PathSanitizer:
    """
    Utilitaire pour sécuriser les chemins de fichiers.

    Prévient les attaques de type path traversal (../../etc/passwd).
    """

    def __init__(self, base_upload_folder: str):
        self._base_folder = Path(base_upload_folder).resolve()

        # Créer le dossier s'il n'existe pas
        self._base_folder.mkdir(parents=True, exist_ok=True)

    def sanitize_filename(self, filename: str) -> str:
        """
        Nettoie un nom de fichier pour le rendre sûr.

        Args:
            filename: Le nom de fichier original.

        Returns:
            str: Le nom de fichier sécurisé.

        Raises:
            ValueError: Si le nom de fichier est invalide.
        """
        safe_name = secure_filename(filename)

        if not safe_name:
            raise ValueError("Nom de fichier invalide")

        return safe_name

    def get_safe_path(self, filename: str, subfolder: str = None) -> Path:
        """
        Génère un chemin sûr pour un fichier.

        Args:
            filename: Le nom de fichier.
            subfolder: Sous-dossier optionnel.

        Returns:
            Path: Le chemin absolu sécurisé.

        Raises:
            ValueError: Si le chemin tente de sortir du dossier de base.
        """
        safe_filename = self.sanitize_filename(filename)

        if subfolder:
            safe_subfolder = secure_filename(subfolder)
            target_folder = self._base_folder / safe_subfolder
            target_folder.mkdir(parents=True, exist_ok=True)
            full_path = target_folder / safe_filename
        else:
            full_path = self._base_folder / safe_filename

        # Vérifier que le chemin résolu reste dans le dossier de base
        resolved_path = full_path.resolve()
        if not self._is_safe_path(resolved_path):
            raise ValueError(
                f"Tentative de path traversal détectée: {filename}"
            )

        return resolved_path

    def _is_safe_path(self, path: Path) -> bool:
        """Vérifie que le chemin reste dans le dossier de base."""
        try:
            path.relative_to(self._base_folder)
            return True
        except ValueError:
            return False

    def delete_file(self, filename: str, subfolder: str = None) -> bool:
        """
        Supprime un fichier de manière sécurisée.

        Args:
            filename: Le nom du fichier à supprimer.
            subfolder: Sous-dossier optionnel.

        Returns:
            bool: True si supprimé, False si n'existe pas.
        """
        try:
            file_path = self.get_safe_path(filename, subfolder)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except ValueError:
            return False
