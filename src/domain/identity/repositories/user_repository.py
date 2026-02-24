# src/domain/identity/repositories/user_repository.py
"""Interface (Port) pour le repository User."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.identity.entities.user import User
from src.domain.identity.value_objects.email import Email


class IUserRepository(ABC):
    """
    Interface pour le repository User.

    Définit le contrat pour la persistance des utilisateurs.
    """

    @abstractmethod
    def save(self, user: User) -> User:
        """Persiste un utilisateur."""
        pass

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Récupère un utilisateur par son ID."""
        pass

    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        """Récupère un utilisateur par son email."""
        pass

    @abstractmethod
    def find_by_email_str(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par son email (string)."""
        pass

    @abstractmethod
    def email_exists(self, email: str) -> bool:
        """Vérifie si un email est déjà utilisé."""
        pass

    @abstractmethod
    def find_all(self, page: int = 1, per_page: int = 20) -> List[User]:
        """Récupère tous les utilisateurs avec pagination."""
        pass

    @abstractmethod
    def delete(self, user: User) -> bool:
        """Supprime un utilisateur."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Retourne le nombre total d'utilisateurs."""
        pass
