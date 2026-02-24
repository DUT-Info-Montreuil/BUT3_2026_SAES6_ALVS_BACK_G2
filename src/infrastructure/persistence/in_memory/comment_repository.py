# src/infrastructure/persistence/in_memory/comment_repository.py
"""Implémentation In-Memory du repository Comment."""

from typing import Dict, List, Optional
from uuid import UUID

from src.domain.collaboration.entities.comment import Comment
from src.domain.collaboration.repositories.comment_repository import ICommentRepository


class InMemoryCommentRepository(ICommentRepository):
    """Repository In-Memory pour Comment."""

    def __init__(self):
        self._store: Dict[UUID, Comment] = {}

    def save(self, comment: Comment) -> Comment:
        """Persiste un commentaire."""
        self._store[comment.id] = comment
        return comment

    def find_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """Récupère un commentaire par ID."""
        return self._store.get(comment_id)

    def find_by_letter(self, letter_id: UUID, page: int = 1, per_page: int = 50) -> List[Comment]:
        """Récupère les commentaires d'une lettre."""
        comments = [c for c in self._store.values() if c.letter_id == letter_id]
        comments.sort(key=lambda c: c.created_at)
        start = (page - 1) * per_page
        return comments[start:start + per_page]

    def find_by_sender(self, sender_id: UUID) -> List[Comment]:
        """Récupère les commentaires d'un utilisateur."""
        return [c for c in self._store.values() if c.sender_id == sender_id]

    def delete(self, comment: Comment) -> bool:
        """Supprime un commentaire."""
        if comment.id in self._store:
            del self._store[comment.id]
            return True
        return False

    def count_by_letter(self, letter_id: UUID) -> int:
        """Compte les commentaires d'une lettre."""
        return len([c for c in self._store.values() if c.letter_id == letter_id])

    def clear(self) -> None:
        """Vide le store."""
        self._store.clear()
