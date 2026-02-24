# src/infrastructure/web/middlewares/auth_middleware.py
"""Middleware d'authentification et d'autorisation."""

from functools import wraps
from typing import Callable, List
from uuid import UUID

from flask import current_app, g
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from src.application.exceptions import ForbiddenException, UnauthorizedException
from src.domain.identity.value_objects.user_role import UserRole


def require_auth(fn: Callable) -> Callable:
    """
    Décorateur qui requiert une authentification JWT.

    Extrait automatiquement le user_id du token et le place dans g.current_user_id.
    JAMAIS depuis le body de la requête.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Configurer JWT si nécessaire
            if not hasattr(current_app.config, 'JWT_TOKEN_LOCATION'):
                current_app.config['JWT_TOKEN_LOCATION'] = ['headers']
                current_app.config['JWT_HEADER_NAME'] = 'Authorization'
                current_app.config['JWT_HEADER_TYPE'] = 'Bearer'

            verify_jwt_in_request()
        except Exception:
            raise UnauthorizedException("Token d'authentification invalide ou manquant")

        # Extraire l'identité depuis le JWT (JAMAIS depuis le body)
        identity = get_jwt_identity()
        if not identity:
            raise UnauthorizedException("Token invalide: identité manquante")

        # Stocker dans le contexte Flask pour accès ultérieur
        g.current_user_id = UUID(identity)
        g.current_user_role = get_jwt().get("role", "member")

        return fn(*args, **kwargs)

    return wrapper


def require_role(allowed_roles: List[UserRole]) -> Callable:
    """
    Décorateur factory qui vérifie le rôle de l'utilisateur.

    Usage:
        @colli_bp.post('')
        @require_role([UserRole.TEACHER, UserRole.ADMIN])
        def create_colli():
            ...

    Args:
        allowed_roles: Liste des rôles autorisés.

    Returns:
        Callable: Le décorateur configuré.
    """
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # D'abord vérifier l'authentification
            try:
                # Configurer JWT si nécessaire
                if not hasattr(current_app.config, 'JWT_TOKEN_LOCATION'):
                    current_app.config['JWT_TOKEN_LOCATION'] = ['headers']
                    current_app.config['JWT_HEADER_NAME'] = 'Authorization'
                    current_app.config['JWT_HEADER_TYPE'] = 'Bearer'

                verify_jwt_in_request()
            except Exception:
                raise UnauthorizedException("Authentification requise")

            # Extraire les informations du JWT
            identity = get_jwt_identity()
            claims = get_jwt()
            user_role_str = claims.get("role", "member")

            # Convertir en enum et vérifier
            try:
                user_role = UserRole(user_role_str)
            except ValueError:
                raise ForbiddenException(f"Rôle invalide: {user_role_str}")

            # Vérifier si le rôle est autorisé
            if user_role not in allowed_roles:
                raise ForbiddenException(
                    f"Action non autorisée pour le rôle {user_role.value}. "
                    f"Rôles requis: {[r.value for r in allowed_roles]}"
                )

            # Stocker dans le contexte
            g.current_user_id = UUID(identity)
            g.current_user_role = user_role

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user_id() -> UUID:
    """
    Récupère l'ID de l'utilisateur courant depuis le contexte Flask.

    À utiliser UNIQUEMENT après un décorateur @require_auth ou @require_role.

    Returns:
        UUID: L'ID de l'utilisateur authentifié.

    Raises:
        RuntimeError: Si appelé hors contexte authentifié.
    """
    user_id = getattr(g, 'current_user_id', None)
    if user_id is None:
        raise RuntimeError("Aucun utilisateur authentifié dans le contexte")
    return user_id


def get_current_user_role() -> UserRole:
    """
    Récupère le rôle de l'utilisateur courant depuis le contexte Flask.

    Returns:
        UserRole: Le rôle de l'utilisateur.
    """
    role = getattr(g, 'current_user_role', None)
    if role is None:
        return UserRole.MEMBER
    if isinstance(role, str):
        return UserRole(role)
    return role
