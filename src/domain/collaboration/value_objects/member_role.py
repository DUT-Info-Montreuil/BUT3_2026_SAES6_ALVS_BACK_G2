# src/domain/collaboration/value_objects/member_role.py
"""Value Object pour le rôle d'un membre dans un COLLI."""

from enum import Enum


class MemberRole(Enum):
    """
    Rôles possibles d'un membre dans un COLLI.

    Hiérarchie de permissions:
    MANAGER > MODERATOR > PATRON > MEMBER
    """
    MANAGER = "manager"       # Gérant du COLLI (créateur ou promu)
    MODERATOR = "moderator"   # Modérateur de contenu
    PATRON = "patron"         # Écrivain parrain
    MEMBER = "member"         # Membre standard

    def has_permission(self, required_role: "MemberRole") -> bool:
        """Vérifie si ce rôle a les permissions du rôle requis."""
        hierarchy = {
            MemberRole.MANAGER: 4,
            MemberRole.MODERATOR: 3,
            MemberRole.PATRON: 2,
            MemberRole.MEMBER: 1,
        }
        return hierarchy.get(self, 0) >= hierarchy.get(required_role, 0)

    def can_moderate(self) -> bool:
        """Vérifie si ce rôle peut modérer le contenu."""
        return self in [MemberRole.MANAGER, MemberRole.MODERATOR]

    def can_manage_members(self) -> bool:
        """Vérifie si ce rôle peut gérer les membres."""
        return self == MemberRole.MANAGER
