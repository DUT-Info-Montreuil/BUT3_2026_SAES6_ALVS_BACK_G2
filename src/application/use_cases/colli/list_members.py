# src/application/use_cases/colli/list_members.py
"""Use Case: Lister les membres d'un COLLI."""

from uuid import UUID
from typing import List
from dataclasses import dataclass, asdict

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.exceptions import NotFoundException, ForbiddenException


@dataclass
class MemberDTO:
    """DTO pour un membre."""
    user_id: str
    role: str
    joined_at: str
    
    def to_dict(self) -> dict:
        return asdict(self)


class ListMembersUseCase:
    """Use Case: Lister les membres d'un COLLI."""
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(self, colli_id: UUID, user_id: UUID) -> dict:
        """Liste les membres."""
        colli = self._colli_repo.find_by_id(colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {colli_id} introuvable")
        
        # Vérifier que l'utilisateur est membre
        if not colli.is_member(user_id):
            raise ForbiddenException("Vous n'êtes pas membre de ce COLLI")
        
        members = []
        for membership in colli.members:
            members.append(MemberDTO(
                user_id=str(membership.user_id),
                role=membership.role.value,
                joined_at=membership.joined_at.isoformat()
            ).to_dict())
        
        return {
            'colli_id': str(colli_id),
            'members': members,
            'total': len(members)
        }
