# src/infrastructure/web/routes/auth_routes.py
"""Routes d'authentification avec injection de dépendances."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from uuid import UUID
from marshmallow import ValidationError
from dependency_injector.wiring import inject, Provide

from src.infrastructure.web.schemas.auth_schema import LoginSchema, RegisterSchema
from src.infrastructure.web.middlewares.auth_middleware import require_auth, get_current_user_id
from src.application.exceptions import ValidationException
from src.application.use_cases.user.register_user import RegisterUserUseCase, RegisterUserCommand
from src.application.use_cases.user.authenticate_user import AuthenticateUserUseCase, AuthenticateUserCommand
from src.application.use_cases.user.get_current_user import GetCurrentUserUseCase
from src.infrastructure.container import Container


auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_bp.post('/login')
@inject
def login(
    use_case: AuthenticateUserUseCase = Provide[Container.authenticate_user_use_case]
):
    """
    Authentification d'un utilisateur.
    
    Returns:
        - 200: Tokens JWT (access_token, refresh_token) + user info
        - 400: Erreur de validation
        - 401: Identifiants invalides
    """
    # Validation des données d'entrée
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Données invalides", errors=err.messages)
    
    # Exécuter le use case
    result = use_case.execute(AuthenticateUserCommand(
        email=data['email'],
        password=data['password']
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.OK


@auth_bp.post('/register')
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
@jwt_required(refresh=True)
def refresh_token():
    """
    Rafraîchit le token d'accès.
    
    Returns:
        - 200: Nouveau token d'accès
        - 401: Token de rafraîchissement invalide
    """
    from flask_jwt_extended import create_access_token, get_jwt
    
    identity = get_jwt_identity()
    claims = get_jwt()
    
    new_access_token = create_access_token(
        identity=identity,
        additional_claims={"role": claims.get("role", "member")}
    )
    
    return jsonify({
        'access_token': new_access_token,
        'token_type': 'Bearer'
    }), HTTPStatus.OK


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
