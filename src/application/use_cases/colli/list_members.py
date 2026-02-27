# src/application/use_cases/colli/list_members.py
"""Use Case: Lister les membres d'un COLLI."""

from uuid import UUID
from dataclasses import dataclass, asdict
from typing import Optional

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.domain.identity.repositories.user_repository import IUserRepository
from src.application.exceptions import NotFoundException


@dataclass
class MemberDTO:
    """DTO pour un membre."""
    id: str
    user_id: str
    colli_id: str
    role: str
    status: str
    joined_at: str
    user: Optional[dict] = None

    def to_dict(self) -> dict:
        return asdict(self)


class ListMembersUseCase:
    """Use Case: Lister les membres d'un COLLI."""

    def __init__(self, colli_repository: IColliRepository, user_repository: IUserRepository):
        self._colli_repo = colli_repository
        self._user_repo = user_repository

    def execute(self, colli_id: UUID, user_id: UUID) -> dict:
        """Liste les membres."""
        colli = self._colli_repo.find_by_id(colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {colli_id} introuvable")

        is_manager = colli.is_manager(user_id) or colli.creator_id == user_id

        members = []
        for membership in colli.members:
            # Les non-managers ne voient que les membres acceptés
            if not is_manager and not membership.is_accepted:
                continue

            # Récupérer les détails de l'utilisateur
            user_details = None
            user = self._user_repo.find_by_id(membership.user_id)
            if user:
                user_details = {
                    'id': str(user.id),
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': str(user.email),
                }

            members.append(MemberDTO(
                id=str(membership.id),
                user_id=str(membership.user_id),
                colli_id=str(colli_id),
                role=membership.role.value,
                status=membership.status.value,
                joined_at=membership.joined_at.isoformat(),
                user=user_details
            ).to_dict())

        return {
            'colli_id': str(colli_id),
            'members': members,
            'total': len(members)
        }
