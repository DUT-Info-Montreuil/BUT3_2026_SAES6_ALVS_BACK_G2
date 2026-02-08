# src/infrastructure/web/routes/admin_routes.py
"""Routes d'administration avec documentation OpenAPI."""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from uuid import UUID
from dependency_injector.wiring import inject, Provide

from src.infrastructure.web.middlewares.auth_middleware import require_role, get_current_user_id
from src.domain.identity.value_objects.user_role import UserRole
from src.application.exceptions import ValidationException, NotFoundException
from src.infrastructure.container import Container


admin_bp = Blueprint('admin', __name__, url_prefix='/api/v1/admin')


@admin_bp.get('/users')
@require_role([UserRole.ADMIN])
@inject
def list_users(
    user_repo = Provide[Container.user_repository]
):
    """
    Lister les utilisateurs
    ---
    tags:
      - Admin
    summary: Recuperer la liste des utilisateurs (admin uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: role
        in: query
        schema:
          type: string
          enum: [member, teacher, patron, admin, relie]
      - name: search
        in: query
        schema:
          type: string
        description: Recherche par email ou nom
      - name: page
        in: query
        schema:
          type: integer
          default: 1
      - name: per_page
        in: query
        schema:
          type: integer
          default: 20
    responses:
      200:
        description: Liste des utilisateurs
        content:
          application/json:
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/User'
                total:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
    """
    role_filter = request.args.get('role')
    search = request.args.get('search', '').lower()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    # Recuperer tous les users (in-memory)
    all_users = user_repo.find_all() if hasattr(user_repo, 'find_all') else []
    
    # Filtrer par role
    if role_filter:
        try:
            target_role = UserRole(role_filter)
            all_users = [u for u in all_users if u.role == target_role]
        except ValueError:
            pass
    
    # Filtrer par recherche
    if search:
        all_users = [
            u for u in all_users 
            if search in u.email.lower() 
            or search in u.first_name.lower() 
            or search in u.last_name.lower()
        ]
    
    # Pagination
    total = len(all_users)
    start = (page - 1) * per_page
    end = start + per_page
    paginated = all_users[start:end]
    
    from src.application.dtos.user_dto import UserResponseDTO
    
    return jsonify({
        'items': [UserResponseDTO.from_entity(u).to_dict() for u in paginated],
        'total': total,
        'page': page,
        'per_page': per_page
    }), HTTPStatus.OK


@admin_bp.get('/users/<uuid:user_id>')
@require_role([UserRole.ADMIN])
@inject
def get_user(
    user_id: UUID,
    user_repo = Provide[Container.user_repository]
):
    """
    Details d'un utilisateur
    ---
    tags:
      - Admin
    summary: Recuperer les details d'un utilisateur (admin uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: Details utilisateur
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user = user_repo.find_by_id(user_id)
    if not user:
        raise NotFoundException(f"Utilisateur {user_id} non trouve")
    
    from src.application.dtos.user_dto import UserResponseDTO
    return jsonify(UserResponseDTO.from_entity(user).to_dict()), HTTPStatus.OK


@admin_bp.patch('/users/<uuid:user_id>')
@require_role([UserRole.ADMIN])
@inject
def update_user_role(
    user_id: UUID,
    user_repo = Provide[Container.user_repository]
):
    """
    Modifier le role d'un utilisateur
    ---
    tags:
      - Admin
    summary: Changer le role d'un utilisateur (admin uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [role]
            properties:
              role:
                type: string
                enum: [member, teacher, patron, admin, relie]
    responses:
      200:
        description: Role mis a jour
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    data = request.get_json() or {}
    new_role_str = data.get('role')
    
    if not new_role_str:
        raise ValidationException("Le role est requis", errors={"role": ["Champ requis"]})
    
    try:
        new_role = UserRole(new_role_str)
    except ValueError:
        raise ValidationException(
            f"Role invalide: {new_role_str}",
            errors={"role": [f"Valeurs valides: {', '.join(r.value for r in UserRole)}"]}
        )
    
    user = user_repo.find_by_id(user_id)
    if not user:
        raise NotFoundException(f"Utilisateur {user_id} non trouve")
    
    # Empecher de se retirer soi-meme le role admin
    current_user_id = get_current_user_id()
    if user_id == current_user_id and new_role != UserRole.ADMIN:
        raise ValidationException("Vous ne pouvez pas retirer votre propre role admin")
    
    user.role = new_role
    user_repo.save(user)
    
    from src.application.dtos.user_dto import UserResponseDTO
    return jsonify(UserResponseDTO.from_entity(user).to_dict()), HTTPStatus.OK


@admin_bp.get('/stats')
@require_role([UserRole.ADMIN])
@inject
def get_stats(
    user_repo = Provide[Container.user_repository],
    colli_repo = Provide[Container.colli_repository],
    letter_repo = Provide[Container.letter_repository],
    comment_repo = Provide[Container.comment_repository]
):
    """
    Statistiques dashboard
    ---
    tags:
      - Admin
    summary: Recuperer les statistiques globales (admin uniquement)
    security:
      - BearerAuth: []
    responses:
      200:
        description: Statistiques
        content:
          application/json:
            schema:
              type: object
              properties:
                users:
                  type: object
                  properties:
                    total:
                      type: integer
                    by_role:
                      type: object
                collis:
                  type: object
                  properties:
                    total:
                      type: integer
                    by_status:
                      type: object
                letters:
                  type: integer
                comments:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
    """
    # Comptage utilisateurs
    all_users = user_repo.find_all() if hasattr(user_repo, 'find_all') else []
    users_by_role = {}
    for user in all_users:
        role = user.role.value
        users_by_role[role] = users_by_role.get(role, 0) + 1
    
    # Comptage COLLIs
    all_collis = colli_repo.find_all() if hasattr(colli_repo, 'find_all') else []
    collis_by_status = {}
    for colli in all_collis:
        status = colli.status.value
        collis_by_status[status] = collis_by_status.get(status, 0) + 1
    
    # Comptage lettres et commentaires
    all_letters = letter_repo.find_all() if hasattr(letter_repo, 'find_all') else []
    all_comments = comment_repo.find_all() if hasattr(comment_repo, 'find_all') else []
    
    return jsonify({
        'users': {
            'total': len(all_users),
            'by_role': users_by_role
        },
        'collis': {
            'total': len(all_collis),
            'by_status': collis_by_status
        },
        'letters': len(all_letters),
        'comments': len(all_comments)
    }), HTTPStatus.OK


@admin_bp.post('/users')
@require_role([UserRole.ADMIN])
@inject
def create_user(
    user_repo = Provide[Container.user_repository]
):
    """
    Creer un utilisateur
    ---
    tags:
      - Admin
    summary: Creer un nouvel utilisateur (admin uniquement)
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [email, password, first_name, last_name]
            properties:
              email:
                type: string
                format: email
              password:
                type: string
                format: password
                minLength: 8
              first_name:
                type: string
              last_name:
                type: string
              role:
                type: string
                enum: [member, teacher, patron, admin, relie]
                default: member
    responses:
      201:
        description: Utilisateur cree
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      409:
        description: Email deja utilise
    """
    from src.domain.identity.entities.user import User
    from src.domain.identity.value_objects.hashed_password import HashedPassword
    from src.application.dtos.user_dto import UserResponseDTO
    
    data = request.get_json() or {}
    
    # Validation
    required = ['email', 'password', 'first_name', 'last_name']
    errors = {}
    for field in required:
        if not data.get(field):
            errors[field] = ["Champ requis"]
    
    if errors:
        raise ValidationException("Donnees invalides", errors=errors)
    
    if len(data['password']) < 8:
        raise ValidationException(
            "Mot de passe trop court",
            errors={"password": ["Minimum 8 caracteres"]}
        )
    
    # Verifier email unique
    if user_repo.find_by_email(data['email']):
        raise ValidationException(
            "Email deja utilise",
            errors={"email": ["Un compte existe deja avec cet email"]}
        )
    
    # Determiner le role
    role_str = data.get('role', 'member')
    try:
        role = UserRole(role_str)
    except ValueError:
        role = UserRole.MEMBER
    
    # Creer l'utilisateur
    user = User(
        email=data['email'],
        password=HashedPassword.create(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=role
    )
    
    user_repo.save(user)
    
    return jsonify(UserResponseDTO.from_entity(user).to_dict()), HTTPStatus.CREATED


@admin_bp.delete('/users/<uuid:user_id>')
@require_role([UserRole.ADMIN])
@inject
def delete_user(
    user_id: UUID,
    user_repo = Provide[Container.user_repository]
):
    """
    Supprimer un utilisateur
    ---
    tags:
      - Admin
    summary: Supprimer un utilisateur (admin uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: Utilisateur supprime
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user = user_repo.find_by_id(user_id)
    if not user:
        raise NotFoundException(f"Utilisateur {user_id} non trouve")
    
    # Empecher de se supprimer soi-meme
    current_user_id = get_current_user_id()
    if user_id == current_user_id:
        raise ValidationException("Vous ne pouvez pas supprimer votre propre compte")
    
    user_repo.delete(user_id)
    
    return '', HTTPStatus.NO_CONTENT
