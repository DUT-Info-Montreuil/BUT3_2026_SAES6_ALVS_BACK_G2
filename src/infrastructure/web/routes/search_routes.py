# src/infrastructure/web/routes/search_routes.py
"""Routes de recherche globale avec documentation OpenAPI."""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from dependency_injector.wiring import inject, Provide

from src.infrastructure.web.middlewares.auth_middleware import require_auth
from src.infrastructure.container import Container


search_bp = Blueprint('search', __name__, url_prefix='/api/v1/search')


@search_bp.get('')
@require_auth
@inject
def global_search(
    user_repo = Provide[Container.user_repository],
    colli_repo = Provide[Container.colli_repository],
    letter_repo = Provide[Container.letter_repository]
):
    """
    Recherche globale
    ---
    tags:
      - Search
    summary: Rechercher dans les COLLIs, lettres et utilisateurs
    security:
      - BearerAuth: []
    parameters:
      - name: q
        in: query
        required: true
        schema:
          type: string
          minLength: 2
        description: Terme de recherche (minimum 2 caracteres)
      - name: type
        in: query
        schema:
          type: string
          enum: [all, collis, letters, users]
          default: all
      - name: limit
        in: query
        schema:
          type: integer
          default: 10
          maximum: 50
    responses:
      200:
        description: Resultats de recherche
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                collis:
                  type: array
                  items:
                    $ref: '#/components/schemas/Colli'
                letters:
                  type: array
                  items:
                    $ref: '#/components/schemas/Letter'
                users:
                  type: array
                  items:
                    $ref: '#/components/schemas/User'
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    from src.application.dtos.colli_dto import ColliResponseDTO
    from src.application.dtos.letter_dto import LetterResponseDTO
    from src.application.dtos.user_dto import UserResponseDTO
    from src.application.exceptions import ValidationException
    
    query = request.args.get('q', '').strip().lower()
    search_type = request.args.get('type', 'all')
    limit = min(request.args.get('limit', 10, type=int), 50)
    
    if len(query) < 2:
        raise ValidationException(
            "Le terme de recherche doit contenir au moins 2 caracteres",
            errors={"q": ["Minimum 2 caracteres"]}
        )
    
    results = {'query': query}
    
    # Recherche COLLIs
    if search_type in ['all', 'collis']:
        all_collis = colli_repo.find_all() if hasattr(colli_repo, 'find_all') else []
        matching_collis = [
            c for c in all_collis
            if query in c.name.lower() 
            or query in c.theme.lower()
            or (c.description and query in c.description.lower())
        ][:limit]
        results['collis'] = [ColliResponseDTO.from_entity(c).to_dict() for c in matching_collis]
    
    # Recherche Lettres
    if search_type in ['all', 'letters']:
        all_letters = letter_repo.find_all() if hasattr(letter_repo, 'find_all') else []
        matching_letters = [
            l for l in all_letters
            if (l.content and query in l.content.lower())
            or (hasattr(l, 'description') and l.description and query in l.description.lower())
        ][:limit]
        results['letters'] = [LetterResponseDTO.from_entity(l).to_dict() for l in matching_letters]
    
    # Recherche Utilisateurs
    if search_type in ['all', 'users']:
        all_users = user_repo.find_all() if hasattr(user_repo, 'find_all') else []
        matching_users = [
            u for u in all_users
            if query in u.email.lower()
            or query in u.first_name.lower()
            or query in u.last_name.lower()
        ][:limit]
        results['users'] = [UserResponseDTO.from_entity(u).to_dict() for u in matching_users]
    
    return jsonify(results), HTTPStatus.OK
