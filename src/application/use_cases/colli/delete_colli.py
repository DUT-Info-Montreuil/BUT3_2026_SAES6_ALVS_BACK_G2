# src/application/use_cases/colli/delete_colli.py
"""Use Case: Supprimer un COLLI."""

from uuid import UUID

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.exceptions import NotFoundException, ForbiddenException


class DeleteColliUseCase:
    """
    Use Case: Supprimer un COLLI.
    
    Règles métier:
    - Seul le créateur peut supprimer le COLLI
    """
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(self, colli_id: UUID, user_id: UUID) -> bool:
        """Supprime un COLLI."""
        colli = self._colli_repo.find_by_id(colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {colli_id} introuvable")
        
        # Vérifier que l'utilisateur est le créateur
        if colli.creator_id != user_id:
            raise ForbiddenException("Seul le créateur peut supprimer le COLLI")
        
        return self._colli_repo.delete(colli)
