# src/infrastructure/web/routes/colli_routes.py
"""Routes pour les COLLIs avec injection de dépendances."""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from uuid import UUID
from marshmallow import ValidationError
from dependency_injector.wiring import inject, Provide

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
    """Créer un nouveau COLLI."""
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
    """Lister les COLLIs avec pagination."""
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
    """Récupérer les détails d'un COLLI."""
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
    """Supprimer un COLLI (créateur uniquement)."""
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
    """Approuver un COLLI (admin uniquement)."""
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
    """Rejoindre un COLLI en tant que membre."""
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
    """Quitter un COLLI."""
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
    """Lister les membres d'un COLLI."""
    user_id = get_current_user_id()
    result = use_case.execute(colli_id, user_id)
    return jsonify(result), HTTPStatus.OK
