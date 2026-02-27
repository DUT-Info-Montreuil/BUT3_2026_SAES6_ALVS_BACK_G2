# src/application/dtos/comment_dto.py
"""DTOs pour les Comments."""

from dataclasses import dataclass, asdict
from typing import Optional
from uuid import UUID

from src.domain.collaboration.entities.comment import Comment


@dataclass
class CreateCommentCommand:
    """Commande pour créer un commentaire."""
    letter_id: UUID
    sender_id: UUID
    content: str
    parent_comment_id: Optional[UUID] = None


@dataclass
class UpdateCommentCommand:
    """Commande pour modifier un commentaire."""
    comment_id: UUID
    editor_id: UUID
    content: str


@dataclass
class CommentResponseDTO:
    """DTO de réponse pour un commentaire."""
    id: str
    content: str
    letter_id: str
    sender_id: str
    parent_comment_id: Optional[str]
    created_at: str
    updated_at: str

    @classmethod
    def from_entity(cls, comment: Comment) -> "CommentResponseDTO":
        """Construit le DTO depuis une entité."""
        return cls(
            id=str(comment.id),
            content=comment.content,
            letter_id=str(comment.letter_id),
            sender_id=str(comment.sender_id),
            parent_comment_id=str(comment.parent_comment_id) if comment.parent_comment_id else None,
            created_at=comment.created_at.isoformat(),
            updated_at=comment.updated_at.isoformat()
        )
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class CommentListResponseDTO:
    """DTO pour une liste paginée de commentaires."""
    items: list
    total: int
    page: int
    per_page: int
    has_more: bool
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            'items': [item.to_dict() if hasattr(item, 'to_dict') else item for item in self.items],
            'total': self.total,
            'page': self.page,
            'per_page': self.per_page,
            'has_more': self.has_more
        }
