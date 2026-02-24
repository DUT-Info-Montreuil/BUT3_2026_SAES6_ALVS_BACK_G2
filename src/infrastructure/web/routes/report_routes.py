# src/infrastructure/web/routes/report_routes.py
"""Routes pour les signalements avec documentation OpenAPI."""

from flask import Blueprint, request, jsonify
from http import HTTPStatus
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from dependency_injector.wiring import inject, Provide

from src.infrastructure.web.middlewares.auth_middleware import require_auth, require_role, get_current_user_id
from src.infrastructure.web.middlewares.rate_limiter import limiter
from src.domain.identity.value_objects.user_role import UserRole
from src.application.exceptions import ValidationException, NotFoundException
from src.infrastructure.container import Container


report_bp = Blueprint('reports', __name__, url_prefix='/api/v1/reports')

# Storage in-memory pour les signalements
_reports = {}


class ReportType(Enum):
    """Types de signalement."""
    SPAM = "spam"
    HARASSMENT = "harassment"
    INAPPROPRIATE = "inappropriate"
    COPYRIGHT = "copyright"
    OTHER = "other"


class ReportStatus(Enum):
    """Statuts de signalement."""
    PENDING = "pending"
    REVIEWING = "reviewing"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


@report_bp.post('')
@limiter.limit("10 per hour")
@require_auth
def create_report():
    """
    Creer un signalement
    ---
    tags:
      - Reports
    summary: Signaler un contenu inapproprie
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [target_type, target_id, reason]
            properties:
              target_type:
                type: string
                enum: [letter, comment, colli, user]
              target_id:
                type: string
                format: uuid
              reason:
                type: string
                enum: [spam, harassment, inappropriate, copyright, other]
              description:
                type: string
                maxLength: 1000
    responses:
      201:
        description: Signalement cree
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: string
                  format: uuid
                message:
                  type: string
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    user_id = get_current_user_id()
    data = request.get_json() or {}
    
    # Validation
    required = ['target_type', 'target_id', 'reason']
    errors = {}
    for field in required:
        if not data.get(field):
            errors[field] = ["Champ requis"]
    
    if errors:
        raise ValidationException("Donnees invalides", errors=errors)
    
    target_type = data['target_type']
    if target_type not in ['letter', 'comment', 'colli', 'user']:
        raise ValidationException(
            "Type de cible invalide",
            errors={"target_type": ["Valeurs: letter, comment, colli, user"]}
        )
    
    reason = data['reason']
    try:
        ReportType(reason)
    except ValueError:
        raise ValidationException(
            "Raison invalide",
            errors={"reason": [f"Valeurs: {', '.join(r.value for r in ReportType)}"]}
        )
    
    report_id = uuid4()
    _reports[report_id] = {
        'id': str(report_id),
        'reporter_id': str(user_id),
        'target_type': target_type,
        'target_id': data['target_id'],
        'reason': reason,
        'description': data.get('description', ''),
        'status': ReportStatus.PENDING.value,
        'created_at': datetime.utcnow().isoformat(),
        'resolved_at': None,
        'resolved_by': None
    }
    
    return jsonify({
        'id': str(report_id),
        'message': 'Signalement enregistre, merci pour votre vigilance'
    }), HTTPStatus.CREATED


@report_bp.get('')
@require_role([UserRole.ADMIN])
def list_reports():
    """
    Lister les signalements (admin)
    ---
    tags:
      - Reports
    summary: Recuperer tous les signalements (admin uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: status
        in: query
        schema:
          type: string
          enum: [pending, reviewing, resolved, dismissed]
      - name: target_type
        in: query
        schema:
          type: string
          enum: [letter, comment, colli, user]
    responses:
      200:
        description: Liste des signalements
        content:
          application/json:
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                total:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    status_filter = request.args.get('status')
    type_filter = request.args.get('target_type')

    reports = list(_reports.values())

    if status_filter:
        reports = [r for r in reports if r['status'] == status_filter]

    if type_filter:
        reports = [r for r in reports if r['target_type'] == type_filter]

    # Trier par date (plus recent en premier)
    reports.sort(key=lambda r: r['created_at'], reverse=True)

    total = len(reports)
    start = (page - 1) * per_page
    paginated = reports[start:start + per_page]

    return jsonify({
        'items': paginated,
        'total': total,
        'page': page,
        'per_page': per_page
    }), HTTPStatus.OK


@report_bp.patch('/<uuid:report_id>')
@require_role([UserRole.ADMIN])
def update_report_status(report_id: UUID):
    """
    Mettre a jour le statut d'un signalement
    ---
    tags:
      - Reports
    summary: Changer le statut d'un signalement (admin uniquement)
    security:
      - BearerAuth: []
    parameters:
      - name: report_id
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
            required: [status]
            properties:
              status:
                type: string
                enum: [reviewing, resolved, dismissed]
              resolution_note:
                type: string
    responses:
      200:
        description: Statut mis a jour
      400:
        $ref: '#/components/responses/ValidationError'
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    report = _reports.get(report_id)
    
    if not report:
        raise NotFoundException(f"Signalement {report_id} non trouve")
    
    data = request.get_json() or {}
    new_status = data.get('status')
    
    if not new_status:
        raise ValidationException("Le statut est requis", errors={"status": ["Champ requis"]})
    
    try:
        ReportStatus(new_status)
    except ValueError:
        raise ValidationException(
            "Statut invalide",
            errors={"status": [f"Valeurs: {', '.join(s.value for s in ReportStatus)}"]}
        )
    
    user_id = get_current_user_id()
    
    report['status'] = new_status
    if new_status in ['resolved', 'dismissed']:
        report['resolved_at'] = datetime.utcnow().isoformat()
        report['resolved_by'] = str(user_id)
    
    if data.get('resolution_note'):
        report['resolution_note'] = data['resolution_note']
    
    return jsonify(report), HTTPStatus.OK
