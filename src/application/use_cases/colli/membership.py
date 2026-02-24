# src/application/use_cases/colli/membership.py
"""Use Cases: Gestion des membres d'un COLLI."""

from uuid import UUID

from src.application.dtos.colli_dto import ColliResponseDTO
from src.application.exceptions import ForbiddenException, NotFoundException, ValidationException
from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.domain.collaboration.value_objects.member_role import MemberRole


class JoinColliUseCase:
    """
    Use Case: Rejoindre un COLLI.

    Règles métier:
    - Le COLLI doit être actif
    - L'utilisateur ne doit pas déjà être membre
    """

    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository

    def execute(self, colli_id: UUID, user_id: UUID) -> ColliResponseDTO:
        """Rejoindre un COLLI en tant que membre."""
        colli = self._colli_repo.find_by_id(colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {colli_id} introuvable")

        if not colli.is_active:
            raise ForbiddenException("Le COLLI n'est pas actif")

        if colli.is_member(user_id):
            raise ValidationException("Vous êtes déjà membre de ce COLLI")

        # Ajouter comme membre
        colli.add_member(user_id, MemberRole.MEMBER)
        saved = self._colli_repo.save(colli)

        return ColliResponseDTO.from_entity(saved)


class LeaveColliUseCase:
    """
    Use Case: Quitter un COLLI.

    Règles métier:
    - L'utilisateur doit être membre
    - Le créateur ne peut pas quitter son propre COLLI
    """

    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository

    def execute(self, colli_id: UUID, user_id: UUID) -> bool:
        """Quitter un COLLI."""
        colli = self._colli_repo.find_by_id(colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {colli_id} introuvable")

        if not colli.is_member(user_id):
            raise ValidationException("Vous n'êtes pas membre de ce COLLI")

        if colli.creator_id == user_id:
            raise ForbiddenException("Le créateur ne peut pas quitter son COLLI")

        # Retirer le membre
        colli.remove_member(user_id)
        self._colli_repo.save(colli)

        return True


class AddManagerUseCase:
    """
    Use Case: Ajouter un manager au COLLI.

    Règles métier:
    - Seul le créateur ou un manager peut ajouter un manager
    - L'utilisateur ajouté doit être membre
    """

    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository

    def execute(
        self,
        colli_id: UUID,
        requester_id: UUID,
        target_user_id: UUID
    ) -> ColliResponseDTO:
        """Ajoute un manager."""
        colli = self._colli_repo.find_by_id(colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {colli_id} introuvable")

        # Vérifier les droits
        if not colli.is_manager(requester_id):
            raise ForbiddenException("Vous devez être manager pour cette action")

        # Vérifier que la cible est membre
        if not colli.is_member(target_user_id):
            raise ValidationException("L'utilisateur doit d'abord être membre")

        # Changer le rôle
        colli.promote_to_manager(target_user_id, requester_id)
        saved = self._colli_repo.save(colli)

        return ColliResponseDTO.from_entity(saved)
