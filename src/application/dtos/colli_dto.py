# src/application/dtos/colli_dto.py
"""Data Transfer Objects pour les Collis."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from src.domain.collaboration.entities.colli import Colli
from src.domain.collaboration.value_objects.colli_status import ColliStatus


@dataclass
class CreateColliDTO:
    """DTO pour la création d'un COLLI."""
    name: str
    theme: str
    description: Optional[str] = None


@dataclass
class ColliResponseDTO:
    """DTO pour les réponses contenant un COLLI."""
    id: str
    name: str
    theme: str
    description: Optional[str]
    creator_id: str
    status: str
    rejection_reason: Optional[str]
    member_count: int
    created_at: str
    updated_at: str

    @classmethod
    def from_entity(cls, colli: Colli) -> "ColliResponseDTO":
        """Construit le DTO depuis une entité du domaine."""
        return cls(
            id=str(colli.id),
            name=colli.name,
            theme=colli.theme,
            description=colli.description,
            creator_id=str(colli.creator_id),
            status=colli.status.value,
            rejection_reason=colli.rejection_reason,
            member_count=colli.member_count,
            created_at=colli.created_at.isoformat(),
            updated_at=colli.updated_at.isoformat()
        )
    
    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return asdict(self)


@dataclass
class ColliListResponseDTO:
    """DTO pour les listes paginées de COLLIs."""
    items: List[ColliResponseDTO]
    total: int
    page: int
    per_page: int
    pages: int
    
    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
            "page": self.page,
            "per_page": self.per_page,
            "pages": self.pages
        }
