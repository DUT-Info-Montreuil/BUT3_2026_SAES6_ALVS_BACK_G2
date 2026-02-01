# src/application/use_cases/colli/reject_colli.py
"""Use Case: Rejet d'un COLLI par un administrateur."""

from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.domain.collaboration.value_objects.colli_status import ColliStatus
from src.application.dtos.colli_dto import ColliResponseDTO
from src.application.exceptions import NotFoundException, ValidationException


@dataclass
class RejectColliCommand:
    """Commande pour rejeter un COLLI."""
    colli_id: UUID
    admin_id: UUID
    reason: Optional[str] = None


class RejectColliUseCase:
    """
    Rejette un COLLI en attente d'approbation.
    
    Seul un administrateur peut rejeter un COLLI.
    Le COLLI passe au statut 'rejected'.
    """
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(self, command: RejectColliCommand) -> ColliResponseDTO:
        """Execute le rejet du COLLI."""
        colli = self._colli_repo.find_by_id(command.colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {command.colli_id} non trouve")
        
        # Verifier que le COLLI est en attente
        if colli.status != ColliStatus.PENDING:
            raise ValidationException(
                f"Impossible de rejeter un COLLI au statut {colli.status.value}"
            )
        
        # Rejeter le COLLI
        colli.status = ColliStatus.REJECTED
        # Note: on pourrait stocker la raison dans un champ supplementaire
        
        self._colli_repo.save(colli)
        
        return ColliResponseDTO.from_entity(colli)
