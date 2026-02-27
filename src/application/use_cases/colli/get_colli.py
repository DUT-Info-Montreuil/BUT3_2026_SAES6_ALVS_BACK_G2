# src/application/use_cases/colli/get_colli.py
"""Use Cases: Récupérer un ou plusieurs Collis."""

from uuid import UUID
from typing import List, Optional

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.domain.collaboration.value_objects.colli_status import ColliStatus
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
        
        return ColliResponseDTO.from_entity(colli)


class ListCollisUseCase:
    """Use Case: Lister les COLLIs avec pagination et filtre optionnel."""

    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository

    def execute(self, page: int = 1, per_page: int = 20, status: Optional[str] = None) -> dict:
        """Liste les COLLIs paginés, avec filtre par statut optionnel."""
        if status:
            colli_status = ColliStatus(status)
            collis = self._colli_repo.find_by_status(colli_status, page, per_page)
            total = self._colli_repo.count_by_status(colli_status)
        else:
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
