# src/infrastructure/web/routes/letter_routes.py
"""Routes pour les Letters avec documentation OpenAPI."""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from uuid import UUID
from dependency_injector.wiring import inject, Provide
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.infrastructure.web.middlewares.auth_middleware import require_auth, get_current_user_id
from src.application.exceptions import ValidationException
from src.application.dtos.letter_dto import CreateTextLetterCommand, CreateFileLetterCommand
from src.application.use_cases.letter.create_letter import CreateTextLetterUseCase, CreateFileLetterUseCase
from src.application.use_cases.letter.get_letters import GetLettersForColliUseCase, GetLetterByIdUseCase
from src.application.use_cases.letter.delete_letter import DeleteLetterUseCase
from src.infrastructure.container import Container


letter_bp = Blueprint('letters', __name__, url_prefix='/api/v1/collis/<uuid:colli_id>/letters')


@letter_bp.post('')
@require_auth
@inject
def create_letter(
    colli_id: UUID,
    use_case_text: CreateTextLetterUseCase = Provide[Container.create_text_letter_use_case],
    use_case_file: CreateFileLetterUseCase = Provide[Container.create_file_letter_use_case]
):
    """
    Créer une lettre
    ---
    tags:
      - Letters
    summary: Créer une nouvelle lettre dans un COLLI
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
            required: [letter_type]
            properties:
              letter_type:
                type: string
                enum: [text, file]
                example: text
              content:
                type: string
                description: Requis si letter_type=text
              file_url:
                type: string
                description: Requis si letter_type=file
              file_name:
                type: string
                description: Requis si letter_type=file
              description:
                type: string
    responses:
      201:
        description: Lettre créée
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Letter'
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    data = request.get_json() or {}
    sender_id = get_current_user_id()
    letter_type = data.get('letter_type', 'text').lower()

    if letter_type == 'text':
        if not data.get('content'):
            raise ValidationException("Le contenu est obligatoire pour une lettre texte")

        result = use_case_text.execute(CreateTextLetterCommand(
            colli_id=colli_id,
            sender_id=sender_id,
            content=data['content'],
            title=data.get('title')
        ))
    elif letter_type == 'file':
        if not data.get('file_url') or not data.get('file_name'):
            raise ValidationException("file_url et file_name sont obligatoires")

        result = use_case_file.execute(CreateFileLetterCommand(
            colli_id=colli_id,
            sender_id=sender_id,
            file_url=data['file_url'],
            file_name=data['file_name'],
            description=data.get('description'),
            title=data.get('title')
        ))
    else:
        raise ValidationException(f"Type de lettre invalide: {letter_type}")
    
    return jsonify(result.to_dict()), HTTPStatus.CREATED


@letter_bp.get('')
@require_auth
@inject
def list_letters(
    colli_id: UUID,
    use_case: GetLettersForColliUseCase = Provide[Container.get_letters_use_case]
):
    """
    Lister les lettres
    ---
    tags:
      - Letters
    summary: Récupérer les lettres d'un COLLI
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
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
          default: 20
          maximum: 100
    responses:
      200:
        description: Liste paginée des lettres
        content:
          application/json:
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/Letter'
                total:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    
    result = use_case.execute(colli_id, user_id, page, per_page)
    return jsonify(result.to_dict()), HTTPStatus.OK


@letter_bp.get('/<uuid:letter_id>')
@require_auth
@inject
def get_letter(
    colli_id: UUID,
    letter_id: UUID,
    use_case: GetLetterByIdUseCase = Provide[Container.get_letter_use_case]
):
    """
    Détails d'une lettre
    ---
    tags:
      - Letters
    summary: Récupérer une lettre
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
      - name: letter_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: Détails de la lettre
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Letter'
      401:
        $ref: '#/components/responses/Unauthorized'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    result = use_case.execute(letter_id, user_id)
    return jsonify(result.to_dict()), HTTPStatus.OK


@letter_bp.delete('/<uuid:letter_id>')
@require_auth
@inject
def delete_letter(
    colli_id: UUID,
    letter_id: UUID,
    use_case: DeleteLetterUseCase = Provide[Container.delete_letter_use_case]
):
    """
    Supprimer une lettre
    ---
    tags:
      - Letters
    summary: Supprimer une lettre (auteur uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
      - name: letter_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: Lettre supprimée
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    use_case.execute(letter_id, user_id)
    return '', HTTPStatus.NO_CONTENT


@letter_bp.patch('/<uuid:letter_id>')
@require_auth
@inject
def update_letter(
    colli_id: UUID,
    letter_id: UUID,
    use_case = Provide[Container.update_letter_use_case]
):
    """
    Modifier une lettre
    ---
    tags:
      - Letters
    summary: Modifier une lettre (auteur uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: colli_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
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
            properties:
              content:
                type: string
              description:
                type: string
    responses:
      200:
        description: Lettre modifiee
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Letter'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    from src.application.use_cases.letter.update_letter import UpdateLetterCommand
    
    data = request.get_json() or {}
    user_id = get_current_user_id()
    
    result = use_case.execute(UpdateLetterCommand(
        letter_id=letter_id,
        user_id=user_id,
        content=data.get('content'),
        description=data.get('description')
    ))
    
    return jsonify(result.to_dict()), HTTPStatus.OK