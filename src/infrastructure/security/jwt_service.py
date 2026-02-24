# src/infrastructure/security/jwt_service.py
"""Service JWT pour l'authentification."""

from datetime import timedelta
from typing import Tuple
from uuid import UUID

from flask import Flask
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
)

jwt = JWTManager()


def init_jwt(app: Flask) -> None:
    """Initialise le gestionnaire JWT avec Flask."""
    jwt.init_app(app)


class JWTService:
    """
    Service pour la gestion des tokens JWT.

    Responsabilités:
    - Création de tokens d'accès et de rafraîchissement
    - Extraction de l'identité utilisateur
    """

    def __init__(
        self,
        access_expires: int = 3600,
        refresh_expires: int = 2592000
    ):
        self._access_expires = timedelta(seconds=access_expires)
        self._refresh_expires = timedelta(seconds=refresh_expires)

    def create_tokens(
        self,
        user_id: UUID,
        role: str,
        additional_claims: dict = None
    ) -> Tuple[str, str]:
        """
        Crée une paire de tokens (access + refresh).

        Args:
            user_id: L'identifiant de l'utilisateur.
            role: Le rôle de l'utilisateur.
            additional_claims: Claims additionnels optionnels.

        Returns:
            Tuple[str, str]: (access_token, refresh_token)
        """
        identity = str(user_id)
        claims = {"role": role}

        if additional_claims:
            claims.update(additional_claims)

        access_token = create_access_token(
            identity=identity,
            additional_claims=claims,
            expires_delta=self._access_expires
        )

        refresh_token = create_refresh_token(
            identity=identity,
            additional_claims={"role": role},
            expires_delta=self._refresh_expires
        )

        return access_token, refresh_token

    def create_access_token_only(
        self,
        user_id: UUID,
        role: str
    ) -> str:
        """Crée uniquement un token d'accès."""
        identity = str(user_id)
        return create_access_token(
            identity=identity,
            additional_claims={"role": role},
            expires_delta=self._access_expires
        )

    @staticmethod
    def get_current_user_id() -> UUID:
        """
        Récupère l'ID de l'utilisateur courant depuis le JWT.

        Returns:
            UUID: L'identifiant de l'utilisateur.

        Raises:
            RuntimeError: Si appelé hors contexte de requête authentifiée.
        """
        identity = get_jwt_identity()
        if not identity:
            raise RuntimeError("Aucun utilisateur authentifié")
        return UUID(identity)

    @staticmethod
    def get_current_user_role() -> str:
        """
        Récupère le rôle de l'utilisateur courant depuis le JWT.

        Returns:
            str: Le rôle de l'utilisateur.
        """
        claims = get_jwt()
        return claims.get("role", "member")
