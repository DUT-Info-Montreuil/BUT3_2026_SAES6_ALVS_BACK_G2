# src/domain/identity/value_objects/hashed_password.py
"""Value Object pour les mots de passe hashés."""

from dataclasses import dataclass

import bcrypt


@dataclass(frozen=True)
class HashedPassword:
    """
    Value Object représentant un mot de passe hashé.

    Le mot de passe en clair n'est jamais stocké.
    Utilise bcrypt pour le hashage sécurisé.
    """
    value: str  # Le hash bcrypt

    MIN_PASSWORD_LENGTH = 8

    @classmethod
    def create(cls, plain_password: str) -> "HashedPassword":
        """
        Factory method pour créer un mot de passe hashé.

        Args:
            plain_password: Le mot de passe en clair.

        Returns:
            HashedPassword: Le mot de passe hashé.

        Raises:
            ValueError: Si le mot de passe est trop court.
        """
        if len(plain_password) < cls.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Le mot de passe doit contenir au moins {cls.MIN_PASSWORD_LENGTH} caractères"
            )

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return cls(value=hashed.decode('utf-8'))

    @classmethod
    def from_hash(cls, hash_value: str) -> "HashedPassword":
        """Reconstruit depuis un hash existant (depuis la BDD)."""
        return cls(value=hash_value)

    def verify(self, plain_password: str) -> bool:
        """
        Vérifie si le mot de passe en clair correspond au hash.

        Args:
            plain_password: Le mot de passe à vérifier.

        Returns:
            bool: True si le mot de passe est correct.
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            self.value.encode('utf-8')
        )

    def __str__(self) -> str:
        return "[HASHED]"  # Ne jamais exposer le hash

    def __repr__(self) -> str:
        return "HashedPassword([HASHED])"
