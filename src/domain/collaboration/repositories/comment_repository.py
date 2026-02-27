# src/domain/collaboration/repositories/comment_repository.py
"""Interface (Port) pour le repository Comment."""

from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from src.domain.collaboration.entities.comment import Comment


class ICommentRepository(ABC):
    """Interface pour le repository Comment."""
    
    @abstractmethod
    def save(self, comment: Comment) -> Comment:
        """Persiste un commentaire."""
        pass
    
    @abstractmethod
    def find_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """Récupère un commentaire par ID."""
        pass
    
    @abstractmethod
    def find_by_letter(
        self,
        letter_id: UUID,
        page: int = 1,
        per_page: int = 50
    ) -> List[Comment]:
        """Récupère les commentaires d'une lettre avec pagination."""
        pass
    
    @abstractmethod
    def find_by_sender(self, sender_id: UUID) -> List[Comment]:
        """Récupère les commentaires d'un utilisateur."""
        pass
    
    @abstractmethod
    def delete(self, comment: Comment) -> bool:
        """Supprime un commentaire."""
        pass
    
    @abstractmethod
    def count_by_letter(self, letter_id: UUID) -> int:
        """Compte les commentaires d'une lettre."""
        pass
