# src/application/use_cases/user/get_current_user.py
"""Use Case: Récupérer l'utilisateur courant."""

from uuid import UUID

from src.domain.identity.repositories.user_repository import IUserRepository
from src.application.dtos.user_dto import UserResponseDTO
from src.application.exceptions import NotFoundException


class GetCurrentUserUseCase:
    """
    Use Case: Récupérer les informations de l'utilisateur connecté.
    """
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository
    
    def execute(self, user_id: UUID) -> UserResponseDTO:
        """
        Récupère l'utilisateur par son ID.
        
        Args:
            user_id: ID de l'utilisateur (depuis le JWT).
            
        Returns:
            UserResponseDTO: Les informations de l'utilisateur.
            
        Raises:
            NotFoundException: Si l'utilisateur n'existe pas.
        """
        user = self._user_repo.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"Utilisateur {user_id} introuvable")
        
        return UserResponseDTO.from_entity(user)
