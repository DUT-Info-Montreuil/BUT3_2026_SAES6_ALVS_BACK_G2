# src/domain/identity/value_objects/user_role.py
"""Value Object pour le rôle global d'un utilisateur."""

from enum import Enum


class UserRole(Enum):
    """
    Rôles globaux d'un utilisateur dans l'application ALVS.

    Ces rôles déterminent les permissions au niveau de l'application,
    indépendamment des rôles dans les COLLI individuels.
    """
    MEMBER = "member"       # Membre standard (lecteur/correspondant)
    TEACHER = "teacher"     # Enseignant (peut créer des COLLI)
    PATRON = "patron"       # Écrivain parrain
    ADMIN = "admin"         # Administrateur (peut approuver/rejeter COLLI)
    RELIE = "relie"         # Réseau des Lecteurs Internationaux (lecture seule)

    def can_create_colli(self) -> bool:
        """Vérifie si ce rôle peut créer un COLLI."""
        return self in [UserRole.TEACHER, UserRole.ADMIN]

    def can_approve_colli(self) -> bool:
        """Vérifie si ce rôle peut approuver/rejeter un COLLI."""
        return self == UserRole.ADMIN

    def can_manage_users(self) -> bool:
        """Vérifie si ce rôle peut gérer les utilisateurs."""
        return self == UserRole.ADMIN

    def is_admin(self) -> bool:
        """Vérifie si ce rôle est administrateur."""
        return self == UserRole.ADMIN
