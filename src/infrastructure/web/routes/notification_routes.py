# src/infrastructure/web/routes/notification_routes.py
"""Routes pour les notifications avec documentation OpenAPI."""

from http import HTTPStatus
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from flask import Blueprint, jsonify, request

from src.application.exceptions import ForbiddenException, NotFoundException
from src.infrastructure.container import Container
from src.infrastructure.web.middlewares.auth_middleware import get_current_user_id, require_auth

notification_bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')


@notification_bp.get('')
@require_auth
@inject
def list_notifications(
    notification_repo = Provide[Container.notification_repository]
):
    """
    Lister les notifications
    ---
    tags:
      - Notifications
    summary: Recuperer les notifications de l'utilisateur connecte
    security:
      - BearerAuth: []
    parameters:
      - name: unread_only
        in: query
        schema:
          type: boolean
          default: false
      - name: limit
        in: query
        schema:
          type: integer
          default: 50
          maximum: 100
    responses:
      200:
        description: Liste des notifications
        content:
          application/json:
            schema:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: string
                        format: uuid
                      type:
                        type: string
                      title:
                        type: string
                      message:
                        type: string
                      read:
                        type: boolean
                      created_at:
                        type: string
                        format: date-time
                unread_count:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    user_id = get_current_user_id()
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    limit = min(request.args.get('limit', 50, type=int), 100)

    notifications = notification_repo.find_by_user(user_id, unread_only, limit)
    unread_count = notification_repo.count_unread(user_id)

    return jsonify({
        'items': [n.to_dict() for n in notifications],
        'unread_count': unread_count
    }), HTTPStatus.OK


@notification_bp.get('/count')
@require_auth
@inject
def get_unread_count(
    notification_repo = Provide[Container.notification_repository]
):
    """
    Nombre de notifications non lues
    ---
    tags:
      - Notifications
    summary: Recuperer le nombre de notifications non lues
    security:
      - BearerAuth: []
    responses:
      200:
        description: Nombre de notifications
        content:
          application/json:
            schema:
              type: object
              properties:
                unread_count:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    user_id = get_current_user_id()
    count = notification_repo.count_unread(user_id)

    return jsonify({'unread_count': count}), HTTPStatus.OK


@notification_bp.patch('/<uuid:notification_id>/read')
@require_auth
@inject
def mark_as_read(
    notification_id: UUID,
    notification_repo = Provide[Container.notification_repository]
):
    """
    Marquer une notification comme lue
    ---
    tags:
      - Notifications
    summary: Marquer une notification comme lue
    security:
      - BearerAuth: []
    parameters:
      - name: notification_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      200:
        description: Notification marquee comme lue
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    notification = notification_repo.find_by_id(notification_id)

    if not notification:
        raise NotFoundException(f"Notification {notification_id} non trouvee")

    if notification.user_id != user_id:
        raise ForbiddenException("Cette notification ne vous appartient pas")

    notification_repo.mark_as_read(notification_id)

    return jsonify({'message': 'Notification marquee comme lue'}), HTTPStatus.OK


@notification_bp.post('/read-all')
@require_auth
@inject
def mark_all_as_read(
    notification_repo = Provide[Container.notification_repository]
):
    """
    Marquer toutes les notifications comme lues
    ---
    tags:
      - Notifications
    summary: Marquer toutes les notifications comme lues
    security:
      - BearerAuth: []
    responses:
      200:
        description: Notifications marquees comme lues
        content:
          application/json:
            schema:
              type: object
              properties:
                marked_count:
                  type: integer
      401:
        $ref: '#/components/responses/Unauthorized'
    """
    user_id = get_current_user_id()
    count = notification_repo.mark_all_as_read(user_id)

    return jsonify({'marked_count': count}), HTTPStatus.OK


@notification_bp.delete('/<uuid:notification_id>')
@require_auth
@inject
def delete_notification(
    notification_id: UUID,
    notification_repo = Provide[Container.notification_repository]
):
    """
    Supprimer une notification
    ---
    tags:
      - Notifications
    summary: Supprimer une notification
    security:
      - BearerAuth: []
    parameters:
      - name: notification_id
        in: path
        required: true
        schema:
          type: string
          format: uuid
    responses:
      204:
        description: Notification supprimee
      401:
        $ref: '#/components/responses/Unauthorized'
      403:
        $ref: '#/components/responses/Forbidden'
      404:
        $ref: '#/components/responses/NotFound'
    """
    user_id = get_current_user_id()
    notification = notification_repo.find_by_id(notification_id)

    if not notification:
        raise NotFoundException(f"Notification {notification_id} non trouvee")

    if notification.user_id != user_id:
        raise ForbiddenException("Cette notification ne vous appartient pas")

    notification_repo.delete(notification_id)

    return '', HTTPStatus.NO_CONTENT
