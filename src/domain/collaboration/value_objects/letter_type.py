# src/domain/collaboration/value_objects/letter_type.py
"""Value Object pour le type de lettre."""

from enum import Enum


class LetterType(Enum):
    """
    Types de lettres possibles dans un COLLI.

    - TEXT: Lettre texte simple
    - FILE: Lettre avec fichier PDF attaché
    """
    TEXT = 'text'
    FILE = 'file'

    @classmethod
    def from_string(cls, value: str) -> "LetterType":
        """Convertit une string en LetterType."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Type de lettre invalide: {value}. Doit être 'text' ou 'file'")

    def requires_content(self) -> bool:
        """Vérifie si ce type nécessite du contenu texte."""
        return self == LetterType.TEXT

    def requires_file(self) -> bool:
        """Vérifie si ce type nécessite un fichier."""
        return self == LetterType.FILE
