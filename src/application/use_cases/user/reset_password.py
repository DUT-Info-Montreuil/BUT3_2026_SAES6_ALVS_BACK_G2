# src/application/use_cases/user/reset_password.py
"""Use Case: Reinitialisation du mot de passe avec token."""

import re
from dataclasses import dataclass
from uuid import UUID

from src.domain.identity.repositories.user_repository import IUserRepository
from src.domain.identity.value_objects.hashed_password import HashedPassword
from src.application.exceptions import ValidationException, NotFoundException
from src.application.use_cases.user.forgot_password import (
    get_reset_token_data, 
    mark_token_as_used, 
    is_token_valid
)


@dataclass
class ResetPasswordCommand:
    """Commande pour reinitialiser le mot de passe."""
    token: str
    new_password: str
    confirm_password: str


@dataclass
class ResetPasswordResult:
    """Resultat de la reinitialisation."""
    success: bool
    message: str


class ResetPasswordUseCase:
    """
    Reinitialise le mot de passe avec un token valide.
    """
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository
    
    def execute(self, command: ResetPasswordCommand) -> ResetPasswordResult:
        """Execute la reinitialisation du mot de passe."""
        
        # Valider le token
        if not is_token_valid(command.token):
            raise ValidationException(
                "Token invalide ou expire",
                errors={"token": ["Le lien de reinitialisation est invalide ou a expire"]}
            )
        
        # Valider les mots de passe
        if command.new_password != command.confirm_password:
            raise ValidationException(
                "Les mots de passe ne correspondent pas",
                errors={"confirm_password": ["Les mots de passe ne correspondent pas"]}
            )
        
        if len(command.new_password) < 8:
            raise ValidationException(
                "Mot de passe trop court",
                errors={"new_password": ["Minimum 8 caracteres"]}
            )

        if not re.search(r'[A-Z]', command.new_password):
            raise ValidationException(
                "Mot de passe trop faible",
                errors={"new_password": ["Le mot de passe doit contenir au moins une majuscule"]}
            )

        if not re.search(r'[0-9]', command.new_password):
            raise ValidationException(
                "Mot de passe trop faible",
                errors={"new_password": ["Le mot de passe doit contenir au moins un chiffre"]}
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', command.new_password):
            raise ValidationException(
                "Mot de passe trop faible",
                errors={"new_password": ["Le mot de passe doit contenir au moins un caractere special"]}
            )

        # Recuperer les donnees du token
        token_data = get_reset_token_data(command.token)
        if not token_data:
            raise ValidationException("Token invalide")
        
        # Recuperer l'utilisateur
        user_id = UUID(token_data['user_id'])
        user = self._user_repo.find_by_id(user_id)
        
        if not user:
            raise NotFoundException("Utilisateur non trouve")
        
        # Mettre a jour le mot de passe
        user.password = HashedPassword.create(command.new_password)
        self._user_repo.save(user)
        
        # Marquer le token comme utilise
        mark_token_as_used(command.token)
        
        return ResetPasswordResult(
            success=True,
            message="Mot de passe reinitialise avec succes"
        )
