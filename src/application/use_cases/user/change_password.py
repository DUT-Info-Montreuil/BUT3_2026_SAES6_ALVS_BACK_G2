# src/application/use_cases/user/change_password.py
"""Use Case: Changement de mot de passe."""

from dataclasses import dataclass
from uuid import UUID

from src.application.exceptions import NotFoundException, UnauthorizedException, ValidationException
from src.domain.identity.repositories.user_repository import IUserRepository
from src.domain.identity.value_objects.hashed_password import HashedPassword


@dataclass
class ChangePasswordCommand:
    """Commande pour changer le mot de passe."""
    user_id: UUID
    current_password: str
    new_password: str
    new_password_confirm: str


class ChangePasswordUseCase:
    """
    Change le mot de passe de l'utilisateur.

    Valide l'ancien mot de passe avant de permettre le changement.
    """

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    def execute(self, command: ChangePasswordCommand) -> None:
        """Execute le changement de mot de passe."""
        # Validation des nouveaux mots de passe
        if command.new_password != command.new_password_confirm:
            raise ValidationException(
                "Les nouveaux mots de passe ne correspondent pas",
                errors={"new_password_confirm": ["Les mots de passe ne correspondent pas"]}
            )

        if len(command.new_password) < 8:
            raise ValidationException(
                "Le nouveau mot de passe doit contenir au moins 8 caracteres",
                errors={"new_password": ["Minimum 8 caracteres requis"]}
            )

        # Recuperer l'utilisateur
        user = self._user_repo.find_by_id(command.user_id)
        if not user:
            raise NotFoundException(f"Utilisateur {command.user_id} non trouve")

        # Verifier l'ancien mot de passe
        if not user.password.verify(command.current_password):
            raise UnauthorizedException("Mot de passe actuel incorrect")

        # Mettre a jour le mot de passe
        user.password = HashedPassword.create(command.new_password)
        self._user_repo.save(user)
