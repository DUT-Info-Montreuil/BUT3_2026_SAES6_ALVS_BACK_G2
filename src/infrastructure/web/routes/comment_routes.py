# src/infrastructure/web/routes/comment_routes.py
"""Routes pour les Comments avec documentation OpenAPI."""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from uuid import UUID
from dependency_injector.wiring import inject, Provide
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.infrastructure.web.middlewares.auth_middleware import require_auth, get_current_user_id
from src.application.exceptions import ValidationException
from src.application.dtos.comment_dto import CreateCommentCommand
from src.application.use_cases.comment.create_comment import CreateCommentUseCase
from src.application.use_cases.comment.get_comments import GetCommentsForLetterUseCase
from src.application.use_cases.comment.delete_comment import DeleteCommentUseCase
from src.infrastructure.container import Container


comment_bp = Blueprint('comments', __name__, url_prefix='/api/v1/letters/<uuid:letter_id>/comments')


@comment_bp.post('')
@jwt_required()
@inject
def create_comment(
    letter_id: UUID,
    use_case: CreateCommentUseCase = Provide[Container.create_comment_use_case]
):
    """
    Créer un commentaire
    ---
    tags:
      - Comments
    summary: Ajouter un commentaire sur une lettre
    security:
      - BearerAuth: []
    parameters:
      - name: letter_id
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
            required: [content]
            properties:
              content:
                type: string
                example: "Très belle analyse !"
    responses:
      201:
        description: Commentaire créé
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Comment'
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    data = request.get_json() or {}
    sender_id = get_jwt_identity()
    
    if not data.get('content'):
        raise ValidationException("Le contenu est obligatoire")
    
    result = use_case.execute(CreateCommentCommand(
        letter_id=letter_id,
        sender_id=sender_id,
        content=data['content']
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.CREATED


@comment_bp.get('')
@jwt_required()
@inject
def list_comments(
    letter_id: UUID,
    use_case: GetCommentsForLetterUseCase = Provide[Container.get_comments_use_case]
):
    """
    Lister les commentaires
    ---
    tags:
      - Comments
    summary: Récupérer les commentaires d'une lettre
    security:
      - BearerAuth: []
    parameters:
      - name: letter_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
      - name: page
        in: query
        schema:
          type: integer
          default: 1
      - name: per_page
        in: query
        schema:
          type: integer
          default: 50
          maximum: 100
    responses:
      200:
        description: Liste paginée des commentaires
        content:
          application/json:
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/Comment'
                total:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    
    result = use_case.execute(letter_id, user_id, page, per_page)
    return jsonify(result.to_dict()), HTTPStatus.OK


@comment_bp.delete('/<uuid:comment_id>')
@jwt_required()
@inject
def delete_comment(
    letter_id: UUID,
    comment_id: UUID,
    use_case: DeleteCommentUseCase = Provide[Container.delete_comment_use_case]
):
    """
    Supprimer un commentaire
    ---
    tags:
      - Comments
    summary: Supprimer un commentaire (auteur uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: letter_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
      - name: comment_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: Commentaire supprimé
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_jwt_identity()
    use_case.execute(comment_id, user_id)
    return '', HTTPStatus.NO_CONTENT


@comment_bp.patch('/<uuid:comment_id>')
@jwt_required()
@inject
def update_comment(
    letter_id: UUID,
    comment_id: UUID,
    use_case = Provide[Container.update_comment_use_case]
):
    """
    Modifier un commentaire
    ---
    tags:
      - Comments
    summary: Modifier un commentaire (auteur uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: letter_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
      - name: comment_id
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
            required: [content]
            properties:
              content:
                type: string
    responses:
      200:
        description: Commentaire modifie
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Comment'
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    from src.application.use_cases.comment.update_comment import UpdateCommentCommand
    from src.application.exceptions import ValidationException
    
    data = request.get_json() or {}
    content = data.get('content')
    
    if not content:
        raise ValidationException("Le contenu est requis", errors={"content": ["Champ requis"]})
    
    user_id = get_jwt_identity()
    
    result = use_case.execute(UpdateCommentCommand(
        comment_id=comment_id,
        user_id=user_id,
        content=content
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.OK