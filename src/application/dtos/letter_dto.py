# src/application/dtos/letter_dto.py
"""DTOs pour les Letters."""

from dataclasses import dataclass, asdict
from typing import Optional
from uuid import UUID

from src.domain.collaboration.entities.letter import Letter


@dataclass
class CreateTextLetterCommand:
    """Commande pour créer une lettre texte."""
    colli_id: UUID
    sender_id: UUID
    content: str
    title: Optional[str] = None


@dataclass
class CreateFileLetterCommand:
    """Commande pour créer une lettre fichier."""
    colli_id: UUID
    sender_id: UUID
    file_url: str
    file_name: str
    description: Optional[str] = None
    title: Optional[str] = None


@dataclass
class UpdateLetterCommand:
    """Commande pour modifier une lettre."""
    letter_id: UUID
    editor_id: UUID
    content: str


@dataclass
class LetterResponseDTO:
    """DTO de réponse pour une lettre."""
    id: str
    letter_type: str
    content: Optional[str]
    file_url: Optional[str]
    file_name: Optional[str]
    title: Optional[str]
    colli_id: str
    sender_id: str
    created_at: str
    updated_at: str
    comment_count: int = 0
    sender: Optional[dict] = None

    @classmethod
    def from_entity(cls, letter: Letter, comment_count: int = 0, sender_data: Optional[dict] = None) -> "LetterResponseDTO":
        """Construit le DTO depuis une entité."""
        return cls(
            id=str(letter.id),
            letter_type=letter.letter_type.value,
            content=letter.content,
            file_url=letter.file_url,
            file_name=letter.file_name,
            title=letter.title,
            colli_id=str(letter.colli_id),
            sender_id=str(letter.sender_id),
            created_at=letter.created_at.isoformat(),
            updated_at=letter.updated_at.isoformat(),
            comment_count=comment_count,
            sender=sender_data
        )

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return asdict(self)


@dataclass
class LetterListResponseDTO:
    """DTO pour une liste paginée de lettres."""
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
