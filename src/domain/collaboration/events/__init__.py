# src/domain/collaboration/events/__init__.py
"""Domain Events pour le contexte Collaboration."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    """Classe de base pour tous les événements du domaine."""
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ColliApproved(DomainEvent):
    """Événement émis quand un COLLI est approuvé."""
    colli_id: UUID = field(default=None)  # type: ignore
    approved_by: Optional[UUID] = None

    def __post_init__(self):
        if self.colli_id is None:
            raise ValueError("colli_id is required")


@dataclass(frozen=True)
class ColliRejected(DomainEvent):
    """Événement émis quand un COLLI est rejeté."""
    colli_id: UUID = field(default=None)  # type: ignore
    rejected_by: Optional[UUID] = None
    reason: Optional[str] = None

    def __post_init__(self):
        if self.colli_id is None:
            raise ValueError("colli_id is required")


@dataclass(frozen=True)
class MemberAdded(DomainEvent):
    """Événement émis quand un membre est ajouté à un COLLI."""
    colli_id: UUID = field(default=None)  # type: ignore
    user_id: UUID = field(default=None)  # type: ignore
    role: str = field(default=None)  # type: ignore

    def __post_init__(self):
        if self.colli_id is None or self.user_id is None or self.role is None:
            raise ValueError("colli_id, user_id and role are required")


@dataclass(frozen=True)
class MemberRemoved(DomainEvent):
    """Événement émis quand un membre est retiré d'un COLLI."""
    colli_id: UUID = field(default=None)  # type: ignore
    user_id: UUID = field(default=None)  # type: ignore

    def __post_init__(self):
        if self.colli_id is None or self.user_id is None:
            raise ValueError("colli_id and user_id are required")


@dataclass(frozen=True)
class LetterCreated(DomainEvent):
    """Événement émis quand une lettre est créée."""
    letter_id: UUID = field(default=None)  # type: ignore
    colli_id: UUID = field(default=None)  # type: ignore
    sender_id: UUID = field(default=None)  # type: ignore

    def __post_init__(self):
        if self.letter_id is None or self.colli_id is None or self.sender_id is None:
            raise ValueError("letter_id, colli_id and sender_id are required")


@dataclass(frozen=True)
class CommentAdded(DomainEvent):
    """Événement émis quand un commentaire est ajouté à une lettre."""
    comment_id: UUID = field(default=None)  # type: ignore
    letter_id: UUID = field(default=None)  # type: ignore
    author_id: UUID = field(default=None)  # type: ignore

    def __post_init__(self):
        if self.comment_id is None or self.letter_id is None or self.author_id is None:
            raise ValueError("comment_id, letter_id and author_id are required")
