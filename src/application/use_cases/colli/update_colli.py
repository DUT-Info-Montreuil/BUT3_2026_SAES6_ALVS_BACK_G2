# src/application/use_cases/colli/update_colli.py
"""Use Case: Mise a jour d'un COLLI."""

from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.dtos.colli_dto import ColliResponseDTO
from src.application.exceptions import NotFoundException, ForbiddenException


@dataclass
class UpdateColliCommand:
    """Commande pour mettre a jour un COLLI."""
    colli_id: UUID
    user_id: UUID
    name: Optional[str] = None
    theme: Optional[str] = None
    description: Optional[str] = None


class UpdateColliUseCase:
    """
    Met a jour un COLLI existant.
    
    Seul le createur ou un admin peut modifier un COLLI.
    """
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(self, command: UpdateColliCommand) -> ColliResponseDTO:
        """Execute la mise a jour du COLLI."""
        colli = self._colli_repo.find_by_id(command.colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {command.colli_id} non trouve")
        
        # Verifier les permissions (createur uniquement pour l'instant)
        if colli.creator_id != command.user_id:
            raise ForbiddenException("Seul le createur peut modifier ce COLLI")
        
        # Mettre a jour les champs fournis
        if command.name is not None:
            colli.name = command.name
        
        if command.theme is not None:
            colli.theme = command.theme
        
        if command.description is not None:
            colli.description = command.description
        
        self._colli_repo.save(colli)
        
        return ColliResponseDTO.from_entity(colli)
