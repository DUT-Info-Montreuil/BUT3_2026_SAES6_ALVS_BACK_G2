# src/infrastructure/web/routes/auth_routes.py
"""Routes d'authentification avec sécurité renforcée."""

import os
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, get_jwt,
    create_access_token, create_refresh_token,
    set_refresh_cookies, unset_jwt_cookies
)
from http import HTTPStatus
from uuid import UUID
from marshmallow import ValidationError
from dependency_injector.wiring import inject, Provide

from src.infrastructure.web.schemas.auth_schema import LoginSchema, RegisterSchema
from src.infrastructure.web.middlewares.auth_middleware import require_auth, get_current_user_id
from src.infrastructure.web.middlewares.rate_limiter import limiter
from src.application.exceptions import ValidationException, ForbiddenException
from src.application.use_cases.user.register_user import RegisterUserUseCase, RegisterUserCommand
from src.application.use_cases.user.authenticate_user import AuthenticateUserUseCase, AuthenticateUserCommand
from src.application.use_cases.user.get_current_user import GetCurrentUserUseCase
from src.infrastructure.container import Container
from src.infrastructure.security.audit_logger import (
    log_login_success, log_login_failure, log_logout, log_account_locked
)
from src.infrastructure.security.account_lockout import get_lockout_service
from src.infrastructure.web.app import get_redis_client


auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


def _get_client_ip():
    """Récupère l'adresse IP du client."""
    return request.headers.get('X-Forwarded-For', request.remote_addr)


@auth_bp.post('/login')
@limiter.limit("5 per minute;100 per day")
@inject
def login(
    use_case: AuthenticateUserUseCase = Provide[Container.authenticate_user_use_case]
):
    """
    Authentification d'un utilisateur.
    
    Returns:
        - 200: Access token + refresh token en cookie HttpOnly
        - 400: Erreur de validation
        - 401: Identifiants invalides
        - 403: Compte verrouillé
    """
    ip = _get_client_ip()
    
    # Validation des données d'entrée
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Données invalides", errors=err.messages)
    
    email = data['email']
    lockout = get_lockout_service()
    
    # Vérifier le verrouillage
    if lockout.is_locked(email):
        log_account_locked(email, ip)
        raise ForbiddenException("Compte temporairement bloqué. Réessayez plus tard.")
    
    try:
        # Exécuter le use case
        result = use_case.execute(AuthenticateUserCommand(
            email=email,
            password=data['password']
        ))
        
        # Connexion réussie
        lockout.clear_lockout(email)
        log_login_success(str(result.user.id), ip)
        
        # Réponse avec cookie HttpOnly pour le refresh token
        response = make_response(jsonify({
            'access_token': result.tokens.access_token,
            'token_type': 'Bearer',
            'user': result.user.to_dict()
        }))
        set_refresh_cookies(response, result.tokens.refresh_token)
        return response, HTTPStatus.OK
        
    except Exception as e:
        # Échec de connexion
        attempts = lockout.increment_failure(email)
        remaining = lockout.get_remaining_attempts(email)
        log_login_failure(email, ip, str(e))
        
        if remaining == 0:
            log_account_locked(email, ip)
        
        raise


@auth_bp.post('/register')
@limiter.limit("3 per hour")
@inject
def register(
    use_case: RegisterUserUseCase = Provide[Container.register_user_use_case]
):
    """
    Inscription d'un nouvel utilisateur.
    
    Returns:
        - 201: Utilisateur créé
        - 400: Erreur de validation
        - 409: Email déjà utilisé
    """
    # Validation des données d'entrée
    schema = RegisterSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Données invalides", errors=err.messages)
    
    # Vérifier que les mots de passe correspondent
    if data['password'] != data['password_confirm']:
        raise ValidationException(
            "Les mots de passe ne correspondent pas",
            errors={"password_confirm": ["Les mots de passe ne correspondent pas"]}
        )
    
    # Exécuter le use case
    result = use_case.execute(RegisterUserCommand(
        email=data['email'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name']
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.CREATED


@auth_bp.post('/refresh')
@limiter.limit("10 per minute")
@jwt_required(refresh=True)
def refresh_token():
    """
    Rafraîchit le token d'accès avec rotation du refresh token.
    
    Returns:
        - 200: Nouveau access token + nouveau refresh token en cookie
        - 401: Token de rafraîchissement invalide ou révoqué
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    old_jti = claims.get("jti")
    
    # Révoquer l'ancien refresh token
    redis_client = get_redis_client()
    if redis_client:
        ttl = 2592000  # 30 jours
        redis_client.setex(f"revoked:{old_jti}", ttl, "revoked")
    
    # Créer de nouveaux tokens
    new_access_token = create_access_token(
        identity=identity,
        additional_claims={"role": claims.get("role", "member")}
    )
    new_refresh_token = create_refresh_token(
        identity=identity,
        additional_claims={"role": claims.get("role", "member")}
    )
    
    # Réponse avec nouveau refresh token en cookie
    response = make_response(jsonify({
        'access_token': new_access_token,
        'token_type': 'Bearer'
    }))
    set_refresh_cookies(response, new_refresh_token)
    return response, HTTPStatus.OK


@auth_bp.post('/logout')
@jwt_required(refresh=True)
def logout():
    """
    Déconnexion et révocation du refresh token.
    
    Returns:
        - 200: Déconnexion réussie
        - 401: Token invalide
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    jti = claims.get("jti")
    
    # Révoquer le token
    redis_client = get_redis_client()
    if redis_client:
        ttl = 2592000  # 30 jours
        redis_client.setex(f"revoked:{jti}", ttl, "revoked")
    
    log_logout(identity)
    
    # Supprimer les cookies
    response = make_response(jsonify({'message': 'Déconnexion réussie'}))
    unset_jwt_cookies(response)
    return response, HTTPStatus.OK


@auth_bp.get('/me')
@require_auth
@inject
def get_current_user(
    use_case: GetCurrentUserUseCase = Provide[Container.get_current_user_use_case]
):
    """
    Récupère les informations de l'utilisateur connecté.
    
    Nécessite authentification.
    """
    user_id = get_current_user_id()
    result = use_case.execute(user_id)
    
    return jsonify(result.to_dict()), HTTPStatus.OK
