# src/application/use_cases/user/register_user.py
"""Use Case: Inscription d'un nouvel utilisateur."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.identity.entities.user import User
from src.domain.identity.value_objects.user_role import UserRole
from src.domain.identity.repositories.user_repository import IUserRepository
from src.application.dtos.user_dto import UserResponseDTO
from src.application.exceptions import ConflictException, ValidationException


@dataclass
class RegisterUserCommand:
    """Commande d'inscription."""
    email: str
    password: str
    first_name: str
    last_name: str


class RegisterUserUseCase:
    """
    Use Case: Inscrire un nouvel utilisateur.
    
    Règles métier:
    - L'email doit être unique
    - Le mot de passe doit respecter les règles de complexité
    - Le nouvel utilisateur a le rôle MEMBER par défaut
    """
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository
    
    def execute(self, command: RegisterUserCommand) -> UserResponseDTO:
        """
        Exécute l'inscription.
        
        Args:
            command: Commande d'inscription.
            
        Returns:
            UserResponseDTO: L'utilisateur créé.
            
        Raises:
            ConflictException: Si l'email existe déjà.
            ValidationException: Si les données sont invalides.
        """
        # Vérifier l'unicité de l'email
        if self._user_repo.email_exists(command.email):
            raise ConflictException(
                f"L'email {command.email} est déjà utilisé",
                details={"field": "email"}
            )
        
        # Créer l'entité User
        try:
            user = User.create(
                email=command.email,
                password=command.password,
                first_name=command.first_name,
                last_name=command.last_name,
                role=UserRole.MEMBER
            )
        except ValueError as e:
            raise ValidationException(str(e))
        
        # Persister
        saved_user = self._user_repo.save(user)
        
        return UserResponseDTO.from_entity(saved_user)
