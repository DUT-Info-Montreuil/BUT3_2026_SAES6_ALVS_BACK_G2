# src/application/use_cases/colli/get_user_collis.py
"""Use Case: Recuperation des COLLIs d'un utilisateur."""

from uuid import UUID
from typing import List, Optional
from enum import Enum

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.dtos.colli_dto import ColliResponseDTO


class ColliRoleFilter(Enum):
    """Filtre par role dans le COLLI."""
    CREATOR = "creator"
    MEMBER = "member"
    ALL = "all"


class GetUserCollisUseCase:
    """
    Recupere les COLLIs auxquels un utilisateur participe.
    
    Peut filtrer par role (createur, membre, ou tous).
    """
    
    def __init__(self, colli_repository: IColliRepository):
        self._colli_repo = colli_repository
    
    def execute(
        self,
        user_id: UUID,
        role_filter: ColliRoleFilter = ColliRoleFilter.ALL,
        page: int = 1,
        per_page: int = 20
    ) -> dict:
        """
        Execute la recuperation des COLLIs de l'utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            role_filter: Filtrer par role (creator, member, all)
            page: Numero de page
            per_page: Elements par page
            
        Returns:
            Dict avec items, total, page, per_page
        """
        all_collis = self._colli_repo.find_all()
        
        # Filtrer selon le role
        user_collis = []
        for colli in all_collis:
            is_creator = colli.creator_id == user_id
            is_member = colli.has_membership(user_id)
            
            if role_filter == ColliRoleFilter.CREATOR and is_creator:
                user_collis.append(colli)
            elif role_filter == ColliRoleFilter.MEMBER and is_member and not is_creator:
                user_collis.append(colli)
            elif role_filter == ColliRoleFilter.ALL and (is_creator or is_member):
                user_collis.append(colli)
        
        # Pagination
        total = len(user_collis)
        start = (page - 1) * per_page
        end = start + per_page
        paginated = user_collis[start:end]
        
        return {
            'items': [ColliResponseDTO.from_entity(c).to_dict() for c in paginated],
            'total': total,
            'page': page,
            'per_page': per_page
        }
