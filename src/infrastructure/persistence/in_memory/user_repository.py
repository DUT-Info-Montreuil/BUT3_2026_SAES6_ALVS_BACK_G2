# src/infrastructure/persistence/in_memory/user_repository.py
"""Implémentation In-Memory du repository User pour les tests."""

from typing import Dict, List, Optional
from uuid import UUID

from src.domain.identity.entities.user import User
from src.domain.identity.repositories.user_repository import IUserRepository
from src.domain.identity.value_objects.email import Email


class InMemoryUserRepository(IUserRepository):
    """
    Implémentation In-Memory du repository User.

    Utilisé pour tests et développement local.
    """

    def __init__(self):
        self._store: Dict[UUID, User] = {}
        self._email_index: Dict[str, UUID] = {}  # Index pour recherche par email

    def save(self, user: User) -> User:
        """Persiste un utilisateur."""
        self._store[user.id] = user
        self._email_index[str(user.email).lower()] = user.id
        return user

    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Récupère un utilisateur par ID."""
        return self._store.get(user_id)

    def find_by_email(self, email: Email) -> Optional[User]:
        """Récupère un utilisateur par Email (Value Object)."""
        user_id = self._email_index.get(str(email).lower())
        if user_id:
            return self._store.get(user_id)
        return None

    def find_by_email_str(self, email: str) -> Optional[User]:
        """Récupère un utilisateur par email (string)."""
        user_id = self._email_index.get(email.lower())
        if user_id:
            return self._store.get(user_id)
        return None

    def email_exists(self, email: str) -> bool:
        """Vérifie si un email existe déjà."""
        return email.lower() in self._email_index

    def find_all(self, page: int = 1, per_page: int = 20) -> List[User]:
        """Récupère tous les utilisateurs avec pagination."""
        all_users = list(self._store.values())
        start = (page - 1) * per_page
        end = start + per_page
        return all_users[start:end]

    def delete(self, user: User) -> bool:
        """Supprime un utilisateur."""
        if user.id in self._store:
            email = str(self._store[user.id].email).lower()
            del self._store[user.id]
            if email in self._email_index:
                del self._email_index[email]
            return True
        return False

    def count(self) -> int:
        """Compte les utilisateurs."""
        return len(self._store)

    def clear(self) -> None:
        """Vide le store (tests)."""
        self._store.clear()
        self._email_index.clear()
