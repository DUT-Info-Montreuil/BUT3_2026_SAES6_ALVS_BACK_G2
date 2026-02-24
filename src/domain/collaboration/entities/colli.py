# src/domain/collaboration/entities/colli.py
"""
Aggregate Root Colli - Communauté de Lectrices et Lecteurs Internationaux.

Cette entité est le cœur du domaine métier ALVS. Elle encapsule toute
la logique métier liée aux COLLI : workflow d'approbation, gestion des
membres, et émission d'événements domaine.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.domain.collaboration.value_objects.member_role import MemberRole
from src.domain.collaboration.value_objects.membership_status import MembershipStatus
from src.domain.collaboration.entities.membership import Membership
from src.domain.collaboration.events import (
    DomainEvent,
    ColliApproved,
    ColliRejected,
    MemberAdded,
    MemberRemoved
)
from src.domain.shared.domain_exception import DomainException


class ColliAlreadyActiveException(DomainException):
    """Levée quand on tente d'approuver un COLLI déjà actif."""
    pass


class UserAlreadyMemberException(DomainException):
    """Levée quand un utilisateur est déjà membre du COLLI."""
    pass


class UserNotMemberException(DomainException):
    """Levée quand un utilisateur n'est pas membre du COLLI."""
    pass


class InactiveColliException(DomainException):
    """Levée quand on tente une opération sur un COLLI inactif."""
    pass


@dataclass
class Colli:
    """
    Aggregate Root pour les Communautés de Lectrices et Lecteurs Internationaux.

    Invariants métier protégés :
    - Un COLLI ne peut être approuvé que si son statut est PENDING
    - Un utilisateur ne peut avoir qu'une seule adhésion (quel que soit le statut)
    - L'approbation crée automatiquement le créateur comme MANAGER (ACCEPTED)
    - Les lettres ne peuvent être créées que dans un COLLI actif par un membre ACCEPTED
    """
    id: UUID
    name: str
    theme: str
    description: Optional[str]
    creator_id: UUID
    status: ColliStatus = ColliStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Relations internes à l'agrégat
    _members: List[Membership] = field(default_factory=list)

    # Événements domaine collectés
    _domain_events: List[DomainEvent] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        theme: str,
        creator_id: UUID,
        description: Optional[str] = None
    ) -> "Colli":
        """
        Factory method avec validation.

        Args:
            name: Nom du COLLI (min 3 caractères).
            theme: Thème littéraire du COLLI.
            creator_id: ID de l'utilisateur créateur.
            description: Description optionnelle.

        Returns:
            Colli: Une nouvelle instance de COLLI en statut PENDING.

        Raises:
            ValueError: Si les validations échouent.
        """
        if not name or len(name.strip()) < 3:
            raise ValueError("Le nom du COLLI doit contenir au moins 3 caractères")
        if not theme or len(theme.strip()) < 2:
            raise ValueError("Le thème du COLLI est obligatoire")

        return cls(
            id=uuid4(),
            name=name.strip(),
            theme=theme.strip(),
            description=description.strip() if description else None,
            creator_id=creator_id
        )

    # =========================================================================
    # WORKFLOW D'APPROBATION
    # =========================================================================

    def approve(self, approved_by: Optional[UUID] = None) -> None:
        """
        Approuve le COLLI et crée automatiquement le créateur comme manager.

        Args:
            approved_by: ID de l'administrateur qui approuve.

        Raises:
            ColliAlreadyActiveException: Si le COLLI n'est pas en attente.
        """
        if self.status != ColliStatus.PENDING:
            raise ColliAlreadyActiveException(
                f"Le COLLI {self.id} ne peut pas être approuvé (statut: {self.status.value})"
            )

        self.status = ColliStatus.ACTIVE
        self._touch()

        # Ajouter le créateur comme manager (directement ACCEPTED)
        self._add_member_internal(self.creator_id, MemberRole.MANAGER, MembershipStatus.ACCEPTED)

        # Émettre l'événement
        self._domain_events.append(ColliApproved(colli_id=self.id, approved_by=approved_by))

    def reject(self, reason: Optional[str] = None, rejected_by: Optional[UUID] = None) -> None:
        """
        Rejette le COLLI.

        Args:
            reason: Raison du rejet (optionnelle).
            rejected_by: ID de l'administrateur qui rejette.

        Raises:
            DomainException: Si le COLLI n'est pas en attente.
        """
        if self.status != ColliStatus.PENDING:
            raise DomainException(
                f"Le COLLI {self.id} ne peut pas être rejeté (statut: {self.status.value})"
            )

        self.status = ColliStatus.REJECTED
        self._touch()

        self._domain_events.append(ColliRejected(
            colli_id=self.id,
            rejected_by=rejected_by,
            reason=reason
        ))

    def complete(self) -> None:
        """
        Marque le COLLI comme terminé.

        Raises:
            DomainException: Si le COLLI n'est pas actif.
        """
        if self.status != ColliStatus.ACTIVE:
            raise DomainException(
                f"Le COLLI {self.id} ne peut pas être terminé (statut: {self.status.value})"
            )

        self.status = ColliStatus.COMPLETED
        self._touch()

    # =========================================================================
    # GESTION DES MEMBRES
    # =========================================================================

    def add_member(
        self,
        user_id: UUID,
        role: MemberRole = MemberRole.MEMBER
    ) -> Membership:
        """
        Ajoute un membre au COLLI (en statut PENDING par défaut).

        Args:
            user_id: ID de l'utilisateur à ajouter.
            role: Rôle à attribuer (défaut: MEMBER).

        Returns:
            Membership: L'appartenance créée.

        Raises:
            InactiveColliException: Si le COLLI n'est pas actif.
            UserAlreadyMemberException: Si l'utilisateur a déjà une adhésion.
        """
        self._ensure_active()

        if self.has_membership(user_id):
            raise UserAlreadyMemberException(
                f"L'utilisateur {user_id} a déjà une adhésion au COLLI {self.id}"
            )

        return self._add_member_internal(user_id, role, MembershipStatus.PENDING)

    def _add_member_internal(
        self,
        user_id: UUID,
        role: MemberRole,
        status: MembershipStatus = MembershipStatus.PENDING
    ) -> Membership:
        """Méthode interne pour ajouter un membre (bypass des vérifications)."""
        membership = Membership.create(
            user_id=user_id,
            colli_id=self.id,
            role=role,
            status=status
        )
        self._members.append(membership)
        self._domain_events.append(MemberAdded(
            colli_id=self.id,
            user_id=user_id,
            role=role.value
        ))
        self._touch()
        return membership

    def accept_member(self, user_id: UUID) -> None:
        """
        Accepte la demande d'adhésion d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur dont la demande est acceptée.

        Raises:
            UserNotMemberException: Si l'utilisateur n'a pas de demande.
            DomainException: Si la demande n'est pas en attente.
        """
        membership = self._get_membership(user_id)
        if not membership:
            raise UserNotMemberException(
                f"L'utilisateur {user_id} n'a pas de demande d'adhésion au COLLI {self.id}"
            )
        if not membership.is_pending:
            raise DomainException(
                f"La demande de l'utilisateur {user_id} n'est pas en attente"
            )
        membership.accept()
        self._touch()

    def reject_member(self, user_id: UUID) -> None:
        """
        Rejette la demande d'adhésion d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur dont la demande est rejetée.

        Raises:
            UserNotMemberException: Si l'utilisateur n'a pas de demande.
            DomainException: Si la demande n'est pas en attente.
        """
        membership = self._get_membership(user_id)
        if not membership:
            raise UserNotMemberException(
                f"L'utilisateur {user_id} n'a pas de demande d'adhésion au COLLI {self.id}"
            )
        if not membership.is_pending:
            raise DomainException(
                f"La demande de l'utilisateur {user_id} n'est pas en attente"
            )
        membership.reject()
        self._touch()

    def remove_member(self, user_id: UUID) -> None:
        """
        Retire un membre du COLLI.

        Args:
            user_id: ID de l'utilisateur à retirer.

        Raises:
            UserNotMemberException: Si l'utilisateur n'est pas membre.
        """
        membership = self._get_membership(user_id)
        if not membership:
            raise UserNotMemberException(
                f"L'utilisateur {user_id} n'est pas membre du COLLI {self.id}"
            )

        self._members.remove(membership)
        self._domain_events.append(MemberRemoved(colli_id=self.id, user_id=user_id))
        self._touch()

    def promote_member(self, user_id: UUID, new_role: MemberRole) -> None:
        """
        Promeut un membre à un nouveau rôle.

        Args:
            user_id: ID du membre à promouvoir.
            new_role: Nouveau rôle à attribuer.

        Raises:
            UserNotMemberException: Si l'utilisateur n'est pas membre accepté.
        """
        membership = self.get_member(user_id)
        if not membership:
            raise UserNotMemberException(
                f"L'utilisateur {user_id} n'est pas membre accepté du COLLI {self.id}"
            )

        membership.promote_to(new_role)
        self._touch()

    # =========================================================================
    # QUERIES
    # =========================================================================

    def is_member(self, user_id: UUID) -> bool:
        """Vérifie si un utilisateur est membre ACCEPTED."""
        return any(
            m.user_id == user_id and m.is_accepted
            for m in self._members
        )

    def is_pending_member(self, user_id: UUID) -> bool:
        """Vérifie si un utilisateur a une demande en attente."""
        return any(
            m.user_id == user_id and m.is_pending
            for m in self._members
        )

    def has_membership(self, user_id: UUID) -> bool:
        """Vérifie si un utilisateur a une adhésion (quel que soit le statut)."""
        return any(m.user_id == user_id for m in self._members)

    def is_manager(self, user_id: UUID) -> bool:
        """Vérifie si un utilisateur est manager (et accepté)."""
        member = self.get_member(user_id)
        return member is not None and member.role == MemberRole.MANAGER

    def get_member(self, user_id: UUID) -> Optional[Membership]:
        """Récupère l'appartenance d'un utilisateur ACCEPTED."""
        return next(
            (m for m in self._members if m.user_id == user_id and m.is_accepted),
            None
        )

    def _get_membership(self, user_id: UUID) -> Optional[Membership]:
        """Récupère l'adhésion d'un utilisateur (quel que soit le statut)."""
        return next((m for m in self._members if m.user_id == user_id), None)

    def can_user_write(self, user_id: UUID) -> bool:
        """Vérifie si un utilisateur peut écrire dans ce COLLI."""
        if not self.is_active:
            return False
        return self.is_member(user_id)

    def get_managers(self) -> List[Membership]:
        """Retourne la liste des managers du COLLI."""
        return [m for m in self._members if m.role == MemberRole.MANAGER and m.is_accepted]

    @property
    def is_active(self) -> bool:
        """Vérifie si le COLLI est actif."""
        return self.status == ColliStatus.ACTIVE

    @property
    def is_pending(self) -> bool:
        """Vérifie si le COLLI est en attente."""
        return self.status == ColliStatus.PENDING

    @property
    def member_count(self) -> int:
        """Retourne le nombre de membres ACCEPTED."""
        return sum(1 for m in self._members if m.is_accepted)

    @property
    def members(self) -> List[Membership]:
        """Retourne une copie de la liste de toutes les adhésions (immutabilité)."""
        return self._members.copy()

    @property
    def accepted_members(self) -> List[Membership]:
        """Retourne uniquement les membres acceptés."""
        return [m for m in self._members if m.is_accepted]

    @property
    def pending_members(self) -> List[Membership]:
        """Retourne uniquement les demandes en attente."""
        return [m for m in self._members if m.is_pending]

    # =========================================================================
    # DOMAIN EVENTS
    # =========================================================================

    def collect_events(self) -> List[DomainEvent]:
        """Récupère et vide les événements collectés."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _ensure_active(self) -> None:
        """Vérifie que le COLLI est actif."""
        if not self.is_active:
            raise InactiveColliException(
                f"Le COLLI {self.id} n'est pas actif (statut: {self.status.value})"
            )

    def _touch(self) -> None:
        """Met à jour le timestamp updated_at."""
        self.updated_at = datetime.utcnow()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Colli):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
