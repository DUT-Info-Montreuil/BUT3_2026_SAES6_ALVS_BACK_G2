# src/application/use_cases/colli/get_colli.py
"""Use Cases: Récupérer un ou plusieurs Collis."""

from uuid import UUID
from typing import List

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.dtos.colli_dto import ColliResponseDTO
from src.application.exceptions import NotFoundException, ForbiddenException


class GetColliByIdUseCase:
    """Use Case: Récupérer un COLLI par ID."""
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(self, colli_id: UUID, user_id: UUID) -> ColliResponseDTO:
        """Récupère un COLLI."""
        colli = self._colli_repo.find_by_id(colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {colli_id} introuvable")
        
        # Vérifier que l'utilisateur a accès au COLLI
        # Accès autorisé si :
        # - Le COLLI est actif (approuvé)
        # - OU l'utilisateur est le créateur
        # - OU l'utilisateur est membre du COLLI
        has_access = (
            colli.is_active or 
            colli.creator_id == user_id or 
            colli.is_member(user_id)
        )
        
        if not has_access:
            # Retourner 404 au lieu de 403 pour ne pas révéler l'existence du COLLI
            raise NotFoundException(f"COLLI {colli_id} introuvable")
        
        return ColliResponseDTO.from_entity(colli)


class ListCollisUseCase:
    """Use Case: Lister les COLLIs avec pagination."""
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(self, page: int = 1, per_page: int = 20) -> dict:
        """Liste les COLLIs paginés."""
        # Pour l'instant, on liste tous les COLLIs actifs
        collis = self._colli_repo.find_all(page, per_page)
        total = self._colli_repo.count()
        
        return {
            'items': [ColliResponseDTO.from_entity(c).to_dict() for c in collis],
            'total': total,
            'page': page,
            'per_page': per_page,
            'has_more': (page * per_page) < total
        }


class ListMyCollisUseCase:
    """Use Case: Lister les COLLIs d'un utilisateur."""
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(self, user_id: UUID) -> List[ColliResponseDTO]:
        """Liste les COLLIs de l'utilisateur."""
        collis = self._colli_repo.find_by_creator(user_id)
        return [ColliResponseDTO.from_entity(c) for c in collis]