# src/application/use_cases/user/forgot_password.py
"""Use Case: Demande de reinitialisation de mot de passe."""

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from src.domain.identity.repositories.user_repository import IUserRepository

# Storage in-memory pour les tokens de reset (en production: Redis)
_reset_tokens: dict[str, dict] = {}


def _generate_reset_token() -> str:
    """Genere un token de reset securise."""
    return secrets.token_urlsafe(32)


def _is_token_valid(token_data: dict) -> bool:
    """Verifie si un token est encore valide."""
    return datetime.utcnow() < token_data['expires_at']


@dataclass
class ForgotPasswordCommand:
    """Commande pour demander un reset de mot de passe."""
    email: str


@dataclass
class ForgotPasswordResult:
    """Resultat de la demande de reset."""
    success: bool
    message: str
    token: Optional[str] = None  # Uniquement en dev/test
    reset_url: Optional[str] = None


class ForgotPasswordUseCase:
    """
    Genere un token de reinitialisation et envoie un email.

    Le token expire apres 1 heure.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        email_service = None,
        base_url: str = "http://localhost:3000"
    ):
        self._user_repo = user_repository
        self._email_service = email_service
        self._base_url = base_url

    def execute(self, command: ForgotPasswordCommand) -> ForgotPasswordResult:
        """Execute la demande de reinitialisation."""

        # Toujours retourner succes pour ne pas reveler si l'email existe
        user = self._user_repo.find_by_email(command.email)

        if not user:
            # Ne pas reveler que l'email n'existe pas
            return ForgotPasswordResult(
                success=True,
                message="Si un compte existe avec cet email, un lien de reinitialisation a ete envoye."
            )

        # Generer le token
        token = _generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # Stocker le token
        _reset_tokens[token] = {
            'user_id': str(user.id),
            'email': command.email,
            'expires_at': expires_at,
            'used': False
        }

        reset_url = f"{self._base_url}/reset-password?token={token}"

        # Envoyer l'email
        if self._email_service and self._email_service.is_enabled():
            self._email_service.send_password_reset(
                to_email=command.email,
                reset_token=token,
                reset_url=reset_url
            )

        return ForgotPasswordResult(
            success=True,
            message="Si un compte existe avec cet email, un lien de reinitialisation a ete envoye.",
            token=token,  # En dev: retourne le token pour tests
            reset_url=reset_url
        )


def get_reset_token_data(token: str) -> Optional[dict]:
    """Recupere les donnees d'un token de reset."""
    return _reset_tokens.get(token)


def mark_token_as_used(token: str) -> None:
    """Marque un token comme utilise."""
    if token in _reset_tokens:
        _reset_tokens[token]['used'] = True


def is_token_valid(token: str) -> bool:
    """Verifie si un token est valide (existe, non expire, non utilise)."""
    token_data = _reset_tokens.get(token)
    if not token_data:
        return False
    if token_data['used']:
        return False
    return _is_token_valid(token_data)
