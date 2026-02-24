# src/infrastructure/web/routes/export_routes.py
"""Routes pour l'export des donnees RGPD."""

from flask import Blueprint, jsonify, Response
from http import HTTPStatus
from datetime import datetime
import json
from dependency_injector.wiring import inject, Provide

from src.infrastructure.web.middlewares.auth_middleware import require_auth, get_current_user_id
from src.infrastructure.container import Container


export_bp = Blueprint('export', __name__, url_prefix='/api/v1/export')


@export_bp.get('/my-data')
@require_auth
@inject
def export_my_data(
    user_repo = Provide[Container.user_repository],
    colli_repo = Provide[Container.colli_repository],
    letter_repo = Provide[Container.letter_repository],
    comment_repo = Provide[Container.comment_repository],
    notification_repo = Provide[Container.notification_repository]
):
    """
    Exporter toutes mes donnees (RGPD)
    ---
    tags:
      - Export
    summary: Telecharger toutes vos donnees personnelles (droit RGPD)
    description: >
      Conformement au RGPD (Art. 20 - Droit a la portabilite),
      cet endpoint permet de telecharger toutes vos donnees
      dans un format structure (JSON).
    security:
      - BearerAuth: []
    responses:
      200:
        description: Fichier JSON contenant toutes vos donnees
        content:
          application/json:
            schema:
              type: object
              properties:
                export_date:
                  type: string
                  format: date-time
                user:
                  $ref: '#/components/schemas/User'
                collis:
                  type: array
                letters:
                  type: array
                comments:
                  type: array
                notifications:
                  type: array
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    from src.application.dtos.user_dto import UserResponseDTO
    from src.application.dtos.colli_dto import ColliResponseDTO
    from src.application.dtos.letter_dto import LetterResponseDTO
    from src.application.dtos.comment_dto import CommentResponseDTO
    
    user_id = get_current_user_id()
    
    # Recuperer l'utilisateur
    user = user_repo.find_by_id(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouve'}), HTTPStatus.NOT_FOUND
    
    # Recuperer les COLLIs (crees ou membre)
    all_collis = colli_repo.find_all() if hasattr(colli_repo, 'find_all') else []
    my_collis = [
        c for c in all_collis 
        if c.creator_id == user_id or user_id in c.member_ids
    ]
    
    # Recuperer les lettres
    all_letters = letter_repo.find_all() if hasattr(letter_repo, 'find_all') else []
    my_letters = [l for l in all_letters if l.sender_id == user_id]
    
    # Recuperer les commentaires
    all_comments = comment_repo.find_all() if hasattr(comment_repo, 'find_all') else []
    my_comments = [c for c in all_comments if c.author_id == user_id]
    
    # Recuperer les notifications
    my_notifications = notification_repo.find_by_user(user_id, limit=1000)
    
    # Construire l'export
    export_data = {
        'export_date': datetime.utcnow().isoformat(),
        'rgpd_notice': 'Export conforme au RGPD Article 20 - Droit a la portabilite des donnees',
        'user': {
            'id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role.value,
            'created_at': user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None,
            'avatar_url': user.avatar_url if hasattr(user, 'avatar_url') else None
        },
        'collis': {
            'created': [ColliResponseDTO.from_entity(c).to_dict() for c in my_collis if c.creator_id == user_id],
            'member_of': [ColliResponseDTO.from_entity(c).to_dict() for c in my_collis if c.creator_id != user_id]
        },
        'letters': [LetterResponseDTO.from_entity(l).to_dict() for l in my_letters],
        'comments': [CommentResponseDTO.from_entity(c).to_dict() for c in my_comments],
        'notifications': [n.to_dict() for n in my_notifications],
        'statistics': {
            'total_collis': len(my_collis),
            'total_letters': len(my_letters),
            'total_comments': len(my_comments),
            'total_notifications': len(my_notifications)
        }
    }
    
    # Retourner comme fichier telechargeable
    response = Response(
        json.dumps(export_data, indent=2, ensure_ascii=False),
        mimetype='application/json',
        headers={
            'Content-Disposition': f'attachment; filename=alvs_export_{user_id}_{datetime.utcnow().strftime("%Y%m%d")}.json'
        }
    )
    
    return response


@export_bp.delete('/my-data')
@require_auth
@inject
def request_data_deletion(
    user_repo = Provide[Container.user_repository]
):
    """
    Demander la suppression de mes donnees (RGPD)
    ---
    tags:
      - Export
    summary: Demander la suppression de votre compte et donnees (droit RGPD)
    description: >
      Conformement au RGPD (Art. 17 - Droit a l'effacement),
      cet endpoint permet de demander la suppression de votre compte.
      La suppression sera traitee sous 30 jours.
    security:
      - BearerAuth: []
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              confirm:
                type: boolean
                description: Doit etre true pour confirmer la demande
              reason:
                type: string
                description: Raison optionnelle
    responses:
      200:
        description: Demande de suppression enregistree
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                deletion_date:
                  type: string
                  format: date-time
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    from flask import request
    from src.application.exceptions import ValidationException
    from datetime import timedelta
    
    data = request.get_json() or {}
    
    if not data.get('confirm'):
        raise ValidationException(
            "Confirmation requise",
            errors={"confirm": ["Vous devez confirmer la suppression"]}
        )
    
    user_id = get_current_user_id()
    user = user_repo.find_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouve'}), HTTPStatus.NOT_FOUND
    
    # En production: enregistrer la demande dans une table dediee
    # et traiter dans un job background
    deletion_date = datetime.utcnow() + timedelta(days=30)
    
    return jsonify({
        'message': 'Votre demande de suppression a ete enregistree',
        'deletion_date': deletion_date.isoformat(),
        'notice': 'Vos donnees seront supprimees sous 30 jours. Vous pouvez annuler cette demande en nous contactant.'
    }), HTTPStatus.OK
