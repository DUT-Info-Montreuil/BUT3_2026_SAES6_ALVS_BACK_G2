# src/domain/collaboration/entities/membership.py
"""Entité Membership représentant l'appartenance d'un utilisateur à un COLLI."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from src.domain.collaboration.value_objects.member_role import MemberRole


@dataclass
class Membership:
    """
    Entity représentant l'appartenance d'un utilisateur à un COLLI.

    Cette entité est contrôlée par l'Aggregate Root Colli.
    """
    id: UUID
    user_id: UUID
    colli_id: UUID
    role: MemberRole
    joined_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        user_id: UUID,
        colli_id: UUID,
        role: MemberRole = MemberRole.MEMBER
    ) -> "Membership":
        """Factory method pour créer une nouvelle appartenance."""
        return cls(
            id=uuid4(),
            user_id=user_id,
            colli_id=colli_id,
            role=role
        )

    def promote_to(self, new_role: MemberRole) -> None:
        """
        Promeut le membre à un nouveau rôle.

        Args:
            new_role: Le nouveau rôle à attribuer.
        """
        self.role = new_role

    def can_moderate(self) -> bool:
        """Vérifie si ce membre peut modérer le contenu."""
        return self.role.can_moderate()

    def can_manage_members(self) -> bool:
        """Vérifie si ce membre peut gérer les autres membres."""
        return self.role.can_manage_members()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Membership):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
