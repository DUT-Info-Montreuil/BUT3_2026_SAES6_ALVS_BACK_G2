# src/domain/notification/entities/notification.py
"""Entite Notification du domaine."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class NotificationType(Enum):
    """Types de notification."""
    NEW_LETTER = "new_letter"
    NEW_COMMENT = "new_comment"
    COLLI_APPROVED = "colli_approved"
    COLLI_REJECTED = "colli_rejected"
    MEMBER_JOINED = "member_joined"
    USER_JOINED = "user_joined"  # Alias pour MEMBER_JOINED
    MEMBER_LEFT = "member_left"
    INVITATION = "invitation"
    SYSTEM = "system"


@dataclass
class Notification:
    """
    Notification pour un utilisateur.

    Attributes:
        id: Identifiant unique
        user_id: Utilisateur destinataire
        type: Type de notification
        title: Titre court
        message: Message detaille
        data: Donnees additionnelles (IDs, etc.)
        read: Statut de lecture
        read_at: Date de lecture
        created_at: Date de creation
    """
    user_id: UUID
    type: NotificationType
    title: str
    message: str
    data: Optional[dict] = None
    related_entity_id: Optional[UUID] = None
    related_entity_type: Optional[str] = None
    read: bool = False
    read_at: Optional[datetime] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Alias pour compatibilite
    @property
    def notification_type(self) -> NotificationType:
        """Alias pour le type de notification."""
        return self.type

    def mark_as_read(self) -> None:
        """Marque la notification comme lue."""
        self.read = True
        self.read_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'type': self.type.value,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'read': self.read,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'created_at': self.created_at.isoformat()
        }
