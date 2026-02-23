# src/infrastructure/web/routes/colli_routes.py
"""Routes pour les COLLIs avec documentation OpenAPI."""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from uuid import UUID
from marshmallow import ValidationError
from dependency_injector.wiring import inject, Provide
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.infrastructure.web.schemas.colli_schema import (
    CreateColliSchema,
    UpdateColliSchema,
    RejectColliSchema,
    AddMemberSchema,
    ColliListQuerySchema
)
from src.infrastructure.web.middlewares.auth_middleware import (
    require_auth,
    require_role,
    get_current_user_id
)
from src.domain.identity.value_objects.user_role import UserRole
from src.application.exceptions import ValidationException
from src.application.use_cases.colli.create_colli import CreateColliUseCase, CreateColliCommand
from src.application.use_cases.colli.approve_colli import ApproveColliUseCase, ApproveColliCommand
from src.application.use_cases.colli.get_colli import GetColliByIdUseCase, ListCollisUseCase
from src.application.use_cases.colli.delete_colli import DeleteColliUseCase
from src.application.use_cases.colli.membership import JoinColliUseCase, LeaveColliUseCase
from src.infrastructure.container import Container


colli_bp = Blueprint('collis', __name__, url_prefix='/api/v1/collis')


@colli_bp.post('')
@require_role([UserRole.TEACHER, UserRole.ADMIN])
@inject
def create_colli(
    use_case: CreateColliUseCase = Provide[Container.create_colli_use_case]
):
    """
    Créer un COLLI
    ---
    tags:
      - COLLI
    summary: Créer une nouvelle communauté littéraire
    description: Crée un COLLI en statut 'pending' (nécessite approbation admin)
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [name, theme]
            properties:
              name:
                type: string
                example: "Correspondances Romantiques"
              theme:
                type: string
                example: "Lettres d'amour du XIXe siècle"
              description:
                type: string
    responses:
      201:
        description: COLLI créé
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Colli'
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
    """
    schema = CreateColliSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Données invalides", errors=err.messages)
    
    creator_id = get_current_user_id()
    
    result = use_case.execute(CreateColliCommand(
        name=data['name'],
        theme=data['theme'],
        description=data.get('description'),
        creator_id=creator_id
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.CREATED


@colli_bp.get('')
@require_auth
@inject
def list_collis(
    use_case: ListCollisUseCase = Provide[Container.list_collis_use_case]
):
    """
    Lister les COLLIs
    ---
    tags:
      - COLLI
    summary: Récupérer la liste des COLLIs avec pagination
    security:
      - BearerAuth: []
    parameters:
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
          maximum: 100
    responses:
      200:
        description: Liste paginée des COLLIs
        content:
          application/json:
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/Colli'
                total:
                  type: integer
                page:
                  type: integer
                per_page:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    schema = ColliListQuerySchema()
    try:
        params = schema.load(request.args)
    except ValidationError as err:
        raise ValidationException("Paramètres invalides", errors=err.messages)
    
    page = params.get('page', 1)
    per_page = params.get('per_page', 20)
    
    result = use_case.execute(page, per_page)
    return jsonify(result), HTTPStatus.OK


@colli_bp.get('/<uuid:colli_id>')
@require_auth
@inject
def get_colli(
    colli_id: UUID,
    use_case: GetColliByIdUseCase = Provide[Container.get_colli_use_case]
):
    """
    Détails d'un COLLI
    ---
    tags:
      - COLLI
    summary: Récupérer les détails d'un COLLI
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: Détails du COLLI
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Colli'
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    result = use_case.execute(colli_id, user_id)
    return jsonify(result.to_dict()), HTTPStatus.OK


@colli_bp.delete('/<uuid:colli_id>')
@require_auth
@inject
def delete_colli(
    colli_id: UUID,
    use_case: DeleteColliUseCase = Provide[Container.delete_colli_use_case]
):
    """
    Supprimer un COLLI
    ---
    tags:
      - COLLI
    summary: Supprimer un COLLI (créateur uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: COLLI supprimé
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    use_case.execute(colli_id, user_id)
    return '', HTTPStatus.NO_CONTENT


@colli_bp.patch('/<uuid:colli_id>/approve')
@require_role([UserRole.ADMIN])
@inject
def approve_colli(
    colli_id: UUID,
    use_case: ApproveColliUseCase = Provide[Container.approve_colli_use_case]
):
    """
    Approuver un COLLI
    ---
    tags:
      - COLLI
    summary: Approuver un COLLI (admin uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: COLLI approuvé
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Colli'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    approver_id = get_current_user_id()
    
    result = use_case.execute(ApproveColliCommand(
        colli_id=colli_id,
        approver_id=approver_id
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.OK


@colli_bp.post('/<uuid:colli_id>/join')
@require_auth
@inject
def join_colli(
    colli_id: UUID,
    use_case: JoinColliUseCase = Provide[Container.join_colli_use_case]
):
    """
    Rejoindre un COLLI
    ---
    tags:
      - COLLI
    summary: Rejoindre un COLLI en tant que membre
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: Membre ajouté
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    result = use_case.execute(colli_id, user_id)
    return jsonify(result.to_dict()), HTTPStatus.OK


@colli_bp.post('/<uuid:colli_id>/leave')
@require_auth
@inject
def leave_colli(
    colli_id: UUID,
    use_case: LeaveColliUseCase = Provide[Container.leave_colli_use_case]
):
    """
    Quitter un COLLI
    ---
    tags:
      - COLLI
    summary: Quitter un COLLI
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: Membre retiré
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    use_case.execute(colli_id, user_id)
    return '', HTTPStatus.NO_CONTENT


@colli_bp.get('/<uuid:colli_id>/members')
@require_auth
@inject
def list_members(
    colli_id: UUID,
    use_case = Provide[Container.list_members_use_case]
):
    """
    Membres d'un COLLI
    ---
    tags:
      - COLLI
    summary: Lister les membres d'un COLLI
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: Liste des membres
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/User'
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    result = use_case.execute(colli_id, user_id)
    return jsonify(result), HTTPStatus.OK


@colli_bp.get('/mine')
@require_auth
@inject
def get_my_collis(
    use_case = Provide[Container.get_user_collis_use_case]
):
    """
    Mes COLLIs
    ---
    tags:
      - COLLI
    summary: Recuperer les COLLIs de l'utilisateur connecte
    security:
      - BearerAuth: []
    parameters:
      - name: role
        in: query
        schema:
          type: string
          enum: [creator, member, all]
          default: all
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
        description: Liste des COLLIs de l'utilisateur
        content:
          application/json:
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/Colli'
                total:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    from src.application.use_cases.colli.get_user_collis import ColliRoleFilter
    
    user_id = get_current_user_id()
    role_str = request.args.get('role', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    try:
        role_filter = ColliRoleFilter(role_str)
    except ValueError:
        role_filter = ColliRoleFilter.ALL
    
    result = use_case.execute(user_id, role_filter, page, per_page)
    return jsonify(result), HTTPStatus.OK


@colli_bp.patch('/<uuid:colli_id>')
@require_auth
@inject
def update_colli(
    colli_id: UUID,
    use_case = Provide[Container.update_colli_use_case]
):
    """
    Modifier un COLLI
    ---
    tags:
      - COLLI
    summary: Mettre a jour un COLLI (createur uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
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
            properties:
              name:
                type: string
              theme:
                type: string
              description:
                type: string
    responses:
      200:
        description: COLLI mis a jour
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Colli'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    from src.application.use_cases.colli.update_colli import UpdateColliCommand
    
    schema = UpdateColliSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        raise ValidationException("Donnees invalides", errors=err.messages)
    
    user_id = get_current_user_id()
    
    result = use_case.execute(UpdateColliCommand(
        colli_id=colli_id,
        user_id=user_id,
        name=data.get('name'),
        theme=data.get('theme'),
        description=data.get('description')
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.OK


@colli_bp.patch('/<uuid:colli_id>/reject')
@require_role([UserRole.ADMIN])
@inject
def reject_colli(
    colli_id: UUID,
    use_case = Provide[Container.reject_colli_use_case]
):
    """
    Rejeter un COLLI
    ---
    tags:
      - COLLI
    summary: Rejeter un COLLI en attente (admin uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              reason:
                type: string
                example: "Ne correspond pas aux criteres"
    responses:
      200:
        description: COLLI rejete
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Colli'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    from src.application.use_cases.colli.reject_colli import RejectColliCommand
    
    data = request.get_json() or {}
    admin_id = get_current_user_id()
    
    result = use_case.execute(RejectColliCommand(
        colli_id=colli_id,
        admin_id=admin_id,
        reason=data.get('reason')
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.OK