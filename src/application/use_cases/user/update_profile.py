# src/application/use_cases/user/update_profile.py
"""Use Case: Mise à jour du profil utilisateur."""

from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from src.domain.identity.repositories.user_repository import IUserRepository
from src.application.dtos.user_dto import UserResponseDTO
from src.application.exceptions import NotFoundException


@dataclass
class UpdateProfileCommand:
    """Commande pour mettre a jour le profil."""
    user_id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UpdateUserProfileUseCase:
    """
    Met a jour le profil de l'utilisateur connecte.
    
    Seuls les champs fournis sont mis a jour.
    """
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository
    
    def execute(self, command: UpdateProfileCommand) -> UserResponseDTO:
        """Execute la mise a jour du profil."""
        user = self._user_repo.find_by_id(command.user_id)
        if not user:
            raise NotFoundException(f"Utilisateur {command.user_id} non trouve")
        
        # Mettre a jour les champs fournis
        if command.first_name is not None:
            user.first_name = command.first_name
        
        if command.last_name is not None:
            user.last_name = command.last_name
        
        # Note: avatar_url necessite un champ supplementaire dans User entity
        # Pour l'instant, on l'ignore si l'entite ne le supporte pas
        
        self._user_repo.save(user)
        
        return UserResponseDTO.from_entity(user)
