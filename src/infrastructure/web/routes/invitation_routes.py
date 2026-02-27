# src/infrastructure/web/routes/invitation_routes.py
"""Routes pour les invitations COLLI avec documentation OpenAPI."""

import secrets
from datetime import datetime, timedelta
from http import HTTPStatus
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify, request

from src.application.exceptions import ForbiddenException, NotFoundException, ValidationException
from src.infrastructure.container import Container
from src.infrastructure.web.middlewares.auth_middleware import (
    get_current_user_id,
    require_auth,
)
from src.infrastructure.web.middlewares.rate_limiter import limiter

invitation_bp = Blueprint('invitations', __name__, url_prefix='/api/v1')

# Storage in-memory pour les invitations (en production: utiliser Redis ou DB)
_invitations = {}


def _generate_invite_code() -> str:
    """Genere un code d'invitation unique."""
    return secrets.token_urlsafe(16)


@invitation_bp.post('/collis/<uuid:colli_id>/invite')
@limiter.limit("20 per hour")
@require_auth
@inject
def create_invitation(
    colli_id: UUID,
    colli_repo = Provide[Container.colli_repository]
):
    """
    Creer une invitation
    ---
    tags:
      - Invitations
    summary: Creer un lien d'invitation pour un COLLI
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
              email:
                type: string
                format: email
                description: Email optionnel du destinataire
              expires_in_hours:
                type: integer
                default: 72
                description: Duree de validite en heures
    responses:
      201:
        description: Invitation creee
        content:
          application/json:
            schema:
              type: object
              properties:
                code:
                  type: string
                invite_url:
                  type: string
                expires_at:
                  type: string
                  format: date-time
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    colli = colli_repo.find_by_id(colli_id)

    if not colli:
        raise NotFoundException(f"COLLI {colli_id} non trouve")

    # Verifier que l'utilisateur est createur ou membre
    if colli.creator_id != user_id and not colli.is_member(user_id):
        raise ForbiddenException("Vous n'etes pas membre de ce COLLI")

    data = request.get_json() or {}
    expires_in_hours = data.get('expires_in_hours', 72)
    target_email = data.get('email')

    code = _generate_invite_code()
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

    _invitations[code] = {
        'colli_id': str(colli_id),
        'created_by': str(user_id),
        'target_email': target_email,
        'expires_at': expires_at,
        'used': False
    }

    return jsonify({
        'code': code,
        'invite_url': f"/api/v1/invitations/{code}/accept",
        'expires_at': expires_at.isoformat()
    }), HTTPStatus.CREATED


@invitation_bp.get('/invitations/<code>')
@require_auth
def get_invitation(code: str):
    """
    Details d'une invitation
    ---
    tags:
      - Invitations
    summary: Recuperer les details d'une invitation
    security:
      - BearerAuth: []
    parameters:
      - name: code
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Details de l'invitation
        content:
          application/json:
            schema:
              type: object
              properties:
                colli_id:
                  type: string
                expires_at:
                  type: string
                valid:
                  type: boolean
      404:
        $ref: '#/components/responses/NotFound'
    """
    invitation = _invitations.get(code)

    if not invitation:
        raise NotFoundException("Invitation non trouvee ou expiree")

    is_valid = (
        not invitation['used'] and
        invitation['expires_at'] > datetime.utcnow()
    )

    return jsonify({
        'colli_id': invitation['colli_id'],
        'expires_at': invitation['expires_at'].isoformat(),
        'valid': is_valid
    }), HTTPStatus.OK


@invitation_bp.post('/invitations/<code>/accept')
@require_auth
@inject
def accept_invitation(
    code: str,
    colli_repo = Provide[Container.colli_repository]
):
    """
    Accepter une invitation
    ---
    tags:
      - Invitations
    summary: Accepter une invitation et rejoindre le COLLI
    security:
      - BearerAuth: []
    parameters:
      - name: code
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: Invitation acceptee
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                colli_id:
                  type: string
      400:
        description: Invitation invalide ou expiree
      404:
        $ref: '#/components/responses/NotFound'
    """
    invitation = _invitations.get(code)

    if not invitation:
        raise NotFoundException("Invitation non trouvee")

    if invitation['used']:
        raise ValidationException("Cette invitation a deja ete utilisee")

    if invitation['expires_at'] < datetime.utcnow():
        raise ValidationException("Cette invitation a expire")

    user_id = get_current_user_id()
    colli_id = UUID(invitation['colli_id'])

    colli = colli_repo.find_by_id(colli_id)
    if not colli:
        raise NotFoundException("COLLI non trouve")

    # Verifier si deja membre
    if colli.has_membership(user_id) or user_id == colli.creator_id:
        return jsonify({
            'message': 'Vous etes deja membre de ce COLLI',
            'colli_id': str(colli_id)
        }), HTTPStatus.OK

    # Ajouter comme membre
    colli.add_member(user_id)
    colli_repo.save(colli)

    # Marquer l'invitation comme utilisee
    invitation['used'] = True

    return jsonify({
        'message': 'Vous avez rejoint le COLLI avec succes',
        'colli_id': str(colli_id)
    }), HTTPStatus.OK
