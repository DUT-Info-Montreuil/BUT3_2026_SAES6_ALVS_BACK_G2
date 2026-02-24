# src/domain/shared/entity_id.py
"""Identifiants typés pour les entités du domaine."""

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class EntityId:
    """
    Value Object représentant un identifiant d'entité.

    Immuable et comparable par valeur.
    """
    value: UUID

    @classmethod
    def generate(cls) -> "EntityId":
        """Génère un nouvel identifiant unique."""
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> "EntityId":
        """Crée un EntityId depuis une chaîne."""
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)


# Alias typés pour chaque type d'entité
@dataclass(frozen=True)
class ColliId(EntityId):
    """Identifiant d'un COLLI."""
    pass


@dataclass(frozen=True)
class UserId(EntityId):
    """Identifiant d'un utilisateur."""
    pass


@dataclass(frozen=True)
class LetterId(EntityId):
    """Identifiant d'une lettre."""
    pass


@dataclass(frozen=True)
class MembershipId(EntityId):
    """Identifiant d'une appartenance."""
    pass


@dataclass(frozen=True)
class CommentId(EntityId):
    """Identifiant d'un commentaire."""
    pass
