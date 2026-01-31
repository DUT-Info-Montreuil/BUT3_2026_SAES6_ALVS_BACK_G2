# src/infrastructure/web/routes/comment_routes.py
"""Routes pour les Comments avec injection de dépendances."""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from uuid import UUID
from dependency_injector.wiring import inject, Provide

from src.infrastructure.web.middlewares.auth_middleware import require_auth, get_current_user_id
from src.application.exceptions import ValidationException
from src.application.dtos.comment_dto import CreateCommentCommand
from src.application.use_cases.comment.create_comment import CreateCommentUseCase
from src.application.use_cases.comment.get_comments import GetCommentsForLetterUseCase
from src.application.use_cases.comment.delete_comment import DeleteCommentUseCase
from src.infrastructure.container import Container


comment_bp = Blueprint('comments', __name__, url_prefix='/api/v1/letters/<uuid:letter_id>/comments')


@comment_bp.post('')
@require_auth
@inject
def create_comment(
    letter_id: UUID,
    use_case: CreateCommentUseCase = Provide[Container.create_comment_use_case]
):
    """Créer un commentaire sur une lettre."""
    data = request.get_json() or {}
    sender_id = get_current_user_id()
    
    if not data.get('content'):
        raise ValidationException("Le contenu est obligatoire")
    
    result = use_case.execute(CreateCommentCommand(
        letter_id=letter_id,
        sender_id=sender_id,
        content=data['content']
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.CREATED


@comment_bp.get('')
@require_auth
@inject
def list_comments(
    letter_id: UUID,
    use_case: GetCommentsForLetterUseCase = Provide[Container.get_comments_use_case]
):
    """Lister les commentaires d'une lettre."""
    user_id = get_current_user_id()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    
    result = use_case.execute(letter_id, user_id, page, per_page)
    return jsonify(result.to_dict()), HTTPStatus.OK


@comment_bp.delete('/<uuid:comment_id>')
@require_auth
@inject
def delete_comment(
    letter_id: UUID,
    comment_id: UUID,
    use_case: DeleteCommentUseCase = Provide[Container.delete_comment_use_case]
):
    """Supprimer un commentaire."""
    user_id = get_current_user_id()
    use_case.execute(comment_id, user_id)
    return '', HTTPStatus.NO_CONTENT
