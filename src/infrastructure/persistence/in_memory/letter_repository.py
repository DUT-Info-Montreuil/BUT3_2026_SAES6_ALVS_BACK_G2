# src/infrastructure/persistence/in_memory/letter_repository.py
"""Implémentation In-Memory du repository Letter."""

from typing import Dict, List, Optional
from uuid import UUID

from src.domain.collaboration.entities.letter import Letter
from src.domain.collaboration.repositories.letter_repository import ILetterRepository


class InMemoryLetterRepository(ILetterRepository):
    """Repository In-Memory pour Letter."""

    def __init__(self):
        self._store: Dict[UUID, Letter] = {}

    def save(self, letter: Letter) -> Letter:
        """Persiste une lettre."""
        self._store[letter.id] = letter
        return letter

    def find_by_id(self, letter_id: UUID) -> Optional[Letter]:
        """Récupère une lettre par ID."""
        return self._store.get(letter_id)

    def find_by_colli(self, colli_id: UUID, page: int = 1, per_page: int = 20) -> List[Letter]:
        """Récupère les lettres d'un COLLI."""
        letters = [l for l in self._store.values() if l.colli_id == colli_id]
        letters.sort(key=lambda l: l.created_at, reverse=True)
        start = (page - 1) * per_page
        return letters[start:start + per_page]

    def find_by_sender(self, sender_id: UUID) -> List[Letter]:
        """Récupère les lettres d'un utilisateur."""
        return [l for l in self._store.values() if l.sender_id == sender_id]

    def delete(self, letter: Letter) -> bool:
        """Supprime une lettre."""
        if letter.id in self._store:
            del self._store[letter.id]
            return True
        return False

    def count_by_colli(self, colli_id: UUID) -> int:
        """Compte les lettres d'un COLLI."""
        return len([l for l in self._store.values() if l.colli_id == colli_id])

    def clear(self) -> None:
        """Vide le store."""
        self._store.clear()
