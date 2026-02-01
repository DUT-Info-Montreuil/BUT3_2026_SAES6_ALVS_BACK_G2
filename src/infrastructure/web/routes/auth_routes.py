# src/infrastructure/web/routes/auth_routes.py
"""Routes d'authentification avec sécurité renforcée et documentation OpenAPI."""

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
    Authentification utilisateur
    ---
    tags:
      - Authentication
    summary: Connecter un utilisateur
    description: >
      Authentifie un utilisateur avec email et mot de passe.
      Retourne un access_token dans le body et un refresh_token en cookie HttpOnly.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/LoginRequest'
    responses:
      200:
        description: Connexion réussie
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginResponse'
        headers:
          Set-Cookie:
            description: Cookie HttpOnly contenant le refresh_token
            schema:
              type: string
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        description: Compte verrouillé (trop de tentatives)
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
      429:
        $ref: '#/components/responses/RateLimited'
    """
    ip = _get_client_ip()
    
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Données invalides", errors=err.messages)
    
    email = data['email']
    lockout = get_lockout_service()
    
    if lockout.is_locked(email):
        log_account_locked(email, ip)
        raise ForbiddenException("Compte temporairement bloqué. Réessayez plus tard.")
    
    try:
        result = use_case.execute(AuthenticateUserCommand(
            email=email,
            password=data['password']
        ))
        
        lockout.clear_lockout(email)
        log_login_success(str(result.user.id), ip)
        
        response = make_response(jsonify({
            'access_token': result.tokens.access_token,
            'token_type': 'Bearer',
            'user': result.user.to_dict()
        }))
        set_refresh_cookies(response, result.tokens.refresh_token)
        return response, HTTPStatus.OK
        
    except Exception as e:
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
    Inscription utilisateur
    ---
    tags:
      - Authentication
    summary: Créer un nouveau compte
    description: >
      Inscrit un nouvel utilisateur avec le rôle MEMBER par défaut.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/RegisterRequest'
    responses:
      201:
        description: Utilisateur créé
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      400:
        $ref: '#/components/responses/ValidationError'
      409:
        description: Email déjà utilisé
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Error'
      429:
        $ref: '#/components/responses/RateLimited'
    """
    schema = RegisterSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Données invalides", errors=err.messages)
    
    if data['password'] != data['password_confirm']:
        raise ValidationException(
            "Les mots de passe ne correspondent pas",
            errors={"password_confirm": ["Les mots de passe ne correspondent pas"]}
        )
    
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
    Rafraîchir les tokens
    ---
    tags:
      - Authentication
    summary: Obtenir un nouveau access_token
    description: >
      Utilise le refresh_token (depuis le cookie) pour générer un nouveau access_token.
      Le refresh_token est également renouvelé (rotation).
    security:
      - BearerAuth: []
    responses:
      200:
        description: Tokens rafraîchis
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                token_type:
                  type: string
                  example: Bearer
      401:
        $ref: '#/components/responses/Unauthorized'
      429:
        $ref: '#/components/responses/RateLimited'
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    old_jti = claims.get("jti")
    
    redis_client = get_redis_client()
    if redis_client:
        ttl = 2592000
        redis_client.setex(f"revoked:{old_jti}", ttl, "revoked")
    
    new_access_token = create_access_token(
        identity=identity,
        additional_claims={"role": claims.get("role", "member")}
    )
    new_refresh_token = create_refresh_token(
        identity=identity,
        additional_claims={"role": claims.get("role", "member")}
    )
    
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
    Déconnexion
    ---
    tags:
      - Authentication
    summary: Révoquer les tokens et déconnecter
    description: >
      Révoque le refresh_token et supprime les cookies d'authentification.
    security:
      - BearerAuth: []
    responses:
      200:
        description: Déconnexion réussie
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Déconnexion réussie
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    identity = get_jwt_identity()
    claims = get_jwt()
    jti = claims.get("jti")
    
    redis_client = get_redis_client()
    if redis_client:
        ttl = 2592000
        redis_client.setex(f"revoked:{jti}", ttl, "revoked")
    
    log_logout(identity)
    
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
    Profil utilisateur courant
    ---
    tags:
      - Authentication
    summary: Récupérer les informations de l'utilisateur connecté
    security:
      - BearerAuth: []
    responses:
      200:
        description: Profil utilisateur
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    user_id = get_current_user_id()
    result = use_case.execute(user_id)
    
    return jsonify(result.to_dict()), HTTPStatus.OK


@auth_bp.patch('/me')
@require_auth
@inject
def update_profile(
    use_case = Provide[Container.update_profile_use_case]
):
    """
    Modifier le profil
    ---
    tags:
      - Authentication
    summary: Mettre a jour le profil de l'utilisateur connecte
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              first_name:
                type: string
                example: Jean
              last_name:
                type: string
                example: Dupont
              avatar_url:
                type: string
                format: uri
    responses:
      200:
        description: Profil mis a jour
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    from src.infrastructure.web.schemas.auth_schema import UpdateProfileSchema
    from src.application.use_cases.user.update_profile import UpdateProfileCommand
    
    schema = UpdateProfileSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Donnees invalides", errors=err.messages)
    
    user_id = get_current_user_id()
    
    result = use_case.execute(UpdateProfileCommand(
        user_id=user_id,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        avatar_url=data.get('avatar_url')
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.OK


@auth_bp.post('/change-password')
@require_auth
@inject
def change_password(
    use_case = Provide[Container.change_password_use_case]
):
    """
    Changer le mot de passe
    ---
    tags:
      - Authentication
    summary: Modifier le mot de passe de l'utilisateur connecte
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [current_password, new_password, new_password_confirm]
            properties:
              current_password:
                type: string
                format: password
              new_password:
                type: string
                format: password
                minLength: 8
              new_password_confirm:
                type: string
                format: password
    responses:
      200:
        description: Mot de passe modifie
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Mot de passe modifie avec succes
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    from src.infrastructure.web.schemas.auth_schema import ChangePasswordSchema
    from src.application.use_cases.user.change_password import ChangePasswordCommand
    
    schema = ChangePasswordSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Donnees invalides", errors=err.messages)
    
    user_id = get_current_user_id()
    
    use_case.execute(ChangePasswordCommand(
        user_id=user_id,
        current_password=data['current_password'],
        new_password=data['new_password'],
        new_password_confirm=data['new_password_confirm']
    ))
    
    return jsonify({'message': 'Mot de passe modifie avec succes'}), HTTPStatus.OK


@auth_bp.post('/forgot-password')
@limiter.limit("3 per minute;10 per hour")
@inject
def forgot_password(
    user_repo = Provide[Container.user_repository]
):
    """
    Demander une reinitialisation de mot de passe
    ---
    tags:
      - Authentication
    summary: Envoyer un email de reinitialisation de mot de passe
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [email]
            properties:
              email:
                type: string
                format: email
    responses:
      200:
        description: Email envoye (si le compte existe)
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                token:
                  type: string
                  description: Token pour dev/test uniquement
      400:
        $ref: '#/components/responses/ValidationError'
    """
    from src.application.use_cases.user.forgot_password import (
        ForgotPasswordUseCase, ForgotPasswordCommand
    )
    from src.infrastructure.services.email_service import get_email_service
    
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    
    if not email:
        raise ValidationException("Email requis", errors={"email": ["Champ requis"]})
    
    use_case = ForgotPasswordUseCase(
        user_repository=user_repo,
        email_service=get_email_service(),
        base_url=os.getenv('FRONTEND_URL', 'http://localhost:3000')
    )
    
    result = use_case.execute(ForgotPasswordCommand(email=email))
    
    response = {'message': result.message}
    
    # En dev: retourner le token pour faciliter les tests
    if os.getenv('FLASK_ENV') == 'development' and result.token:
        response['token'] = result.token
        response['reset_url'] = result.reset_url
    
    return jsonify(response), HTTPStatus.OK


@auth_bp.post('/reset-password')
@limiter.limit("5 per minute")
@inject
def reset_password(
    user_repo = Provide[Container.user_repository]
):
    """
    Reinitialiser le mot de passe avec un token
    ---
    tags:
      - Authentication
    summary: Definir un nouveau mot de passe avec le token recu par email
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [token, new_password, confirm_password]
            properties:
              token:
                type: string
                description: Token recu par email
              new_password:
                type: string
                format: password
                minLength: 8
              confirm_password:
                type: string
                format: password
    responses:
      200:
        description: Mot de passe reinitialise
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      400:
        $ref: '#/components/responses/ValidationError'
    """
    from src.application.use_cases.user.reset_password import (
        ResetPasswordUseCase, ResetPasswordCommand
    )
    
    data = request.get_json() or {}
    
    token = data.get('token', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')
    
    errors = {}
    if not token:
        errors['token'] = ["Token requis"]
    if not new_password:
        errors['new_password'] = ["Nouveau mot de passe requis"]
    if not confirm_password:
        errors['confirm_password'] = ["Confirmation requise"]
    
    if errors:
        raise ValidationException("Donnees invalides", errors=errors)
    
    use_case = ResetPasswordUseCase(user_repository=user_repo)
    
    result = use_case.execute(ResetPasswordCommand(
        token=token,
        new_password=new_password,
        confirm_password=confirm_password
    ))
    
    return jsonify({'message': result.message}), HTTPStatus.OK
