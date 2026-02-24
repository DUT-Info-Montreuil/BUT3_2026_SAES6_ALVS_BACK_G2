# src/application/use_cases/user/authenticate_user.py
"""Use Case: Authentification d'un utilisateur."""

from dataclasses import dataclass
from typing import Tuple

from src.domain.identity.entities.user import User, InvalidCredentialsException
from src.domain.identity.repositories.user_repository import IUserRepository
from src.infrastructure.security.jwt_service import JWTService
from src.application.dtos.user_dto import UserResponseDTO, AuthTokensDTO, LoginResponseDTO
from src.application.exceptions import UnauthorizedException


@dataclass
class AuthenticateUserCommand:
    """Commande d'authentification."""
    email: str
    password: str


class AuthenticateUserUseCase:
    """
    Use Case: Authentifier un utilisateur.
    
    Règles métier:
    - Vérifier que le compte existe
    - Vérifier que le compte est actif
    - Vérifier le mot de passe
    - Générer les tokens JWT
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        jwt_service: JWTService
    ):
        self._user_repo = user_repository
        self._jwt_service = jwt_service
    
    def execute(self, command: AuthenticateUserCommand) -> LoginResponseDTO:
        """
        Exécute l'authentification.
        
        Args:
            command: Commande d'authentification.
            
        Returns:
            LoginResponseDTO: Utilisateur et tokens.
            
        Raises:
            UnauthorizedException: Si les identifiants sont invalides.
        """
        # Récupérer l'utilisateur par email
        user = self._user_repo.find_by_email_str(command.email)
        if not user:
            raise UnauthorizedException("Identifiants invalides")
        
        # Authentifier (vérifie mot de passe + compte actif)
        try:
            user.authenticate(command.password)
        except InvalidCredentialsException as e:
            raise UnauthorizedException(str(e))
        
        # Sauvegarder (met à jour last_login_at)
        self._user_repo.save(user)
        
        # Générer les tokens
        access_token, refresh_token = self._jwt_service.create_tokens(
            user_id=user.id,
            role=user.role.value
        )
        
        # Construire la réponse
        user_dto = UserResponseDTO.from_entity(user)
        tokens_dto = AuthTokensDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )
        
        return LoginResponseDTO(user=user_dto, tokens=tokens_dto)
