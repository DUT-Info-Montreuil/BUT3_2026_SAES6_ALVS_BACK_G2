# src/infrastructure/websocket/socket_manager.py
"""Gestionnaire de WebSocket avec Flask-SocketIO."""

import logging
import os
from typing import Dict, Optional, Set

from flask import request
from flask_jwt_extended import decode_token
from flask_socketio import SocketIO, emit, join_room, leave_room

logger = logging.getLogger(__name__)

# Instance SocketIO globale
socketio: Optional[SocketIO] = None

# Mapping user_id -> set of session_ids
_connected_users: Dict[str, Set[str]] = {}


def init_socketio(app) -> SocketIO:
    """
    Initialise Flask-SocketIO avec l'application Flask.

    Args:
        app: Application Flask

    Returns:
        Instance SocketIO configuree
    """
    global socketio

    # Configuration CORS avec origines restreintes
    cors_origin = os.getenv('CORS_ORIGIN', 'http://localhost:5173')
    cors_origins = [origin.strip() for origin in cors_origin.split(',')]

    socketio = SocketIO(
        app,
        cors_allowed_origins=cors_origins,
        async_mode='threading',  # Pour Windows, sinon 'eventlet'
        logger=True,
        engineio_logger=True
    )

    # Enregistrer les handlers
    register_handlers(socketio)

    logger.info("Flask-SocketIO initialise")
    return socketio


def get_socketio() -> Optional[SocketIO]:
    """Retourne l'instance SocketIO."""
    return socketio


def register_handlers(sio: SocketIO):
    """Enregistre les handlers d'evenements WebSocket."""

    @sio.on('connect')
    def handle_connect(auth=None):
        """Gere la connexion d'un client."""
        logger.info(f"Client connecte: {request.sid}")

        # Verifier l'authentification
        token = None
        if auth and isinstance(auth, dict):
            token = auth.get('token')

        if not token:
            # Essayer dans les headers
            token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if token:
            try:
                decoded = decode_token(token)
                user_id = decoded['sub']

                # Ajouter a la room de l'utilisateur
                join_room(f"user_{user_id}")

                # Tracker la connexion
                if user_id not in _connected_users:
                    _connected_users[user_id] = set()
                _connected_users[user_id].add(request.sid)

                logger.info(f"Utilisateur {user_id} authentifie via WebSocket")
                emit('authenticated', {'user_id': user_id})

            except Exception as e:
                logger.warning(f"Token WebSocket invalide: {e}")
                emit('error', {'message': 'Token invalide'})
        else:
            # Connexion anonyme (pour certains usages publics)
            emit('connected', {'message': 'Connexion etablie (non authentifiee)'})

    @sio.on('disconnect')
    def handle_disconnect():
        """Gere la deconnexion d'un client."""
        logger.info(f"Client deconnecte: {request.sid}")

        # Nettoyer le tracking
        for user_id, sessions in list(_connected_users.items()):
            if request.sid in sessions:
                sessions.discard(request.sid)
                if not sessions:
                    del _connected_users[user_id]
                break

    @sio.on('join_colli')
    def handle_join_colli(data):
        """Rejoindre la room d'un COLLI pour recevoir les updates."""
        colli_id = data.get('colli_id')
        if colli_id:
            join_room(f"colli_{colli_id}")
            emit('joined_colli', {'colli_id': colli_id})
            logger.info(f"Client {request.sid} rejoint le COLLI {colli_id}")

    @sio.on('leave_colli')
    def handle_leave_colli(data):
        """Quitter la room d'un COLLI."""
        colli_id = data.get('colli_id')
        if colli_id:
            leave_room(f"colli_{colli_id}")
            emit('left_colli', {'colli_id': colli_id})

    @sio.on('ping')
    def handle_ping():
        """Ping pour keepalive."""
        emit('pong')


def is_user_online(user_id: str) -> bool:
    """Verifie si un utilisateur est connecte."""
    return user_id in _connected_users and len(_connected_users[user_id]) > 0


def get_online_users() -> list:
    """Retourne la liste des utilisateurs connectes."""
    return list(_connected_users.keys())


# =============================================================================
# FONCTIONS D'EMISSION DE NOTIFICATIONS
# =============================================================================

def emit_to_user(user_id: str, event: str, data: dict):
    """
    Emet un evenement a un utilisateur specifique.

    Args:
        user_id: ID de l'utilisateur
        event: Nom de l'evenement
        data: Donnees a envoyer
    """
    if socketio:
        socketio.emit(event, data, room=f"user_{user_id}")
        logger.debug(f"Emit {event} to user {user_id}")


def emit_to_colli(colli_id: str, event: str, data: dict, skip_sid: str = None):
    """
    Emet un evenement a tous les membres d'un COLLI.

    Args:
        colli_id: ID du COLLI
        event: Nom de l'evenement
        data: Donnees a envoyer
        skip_sid: Session ID a exclure (pour ne pas notifier l'emetteur)
    """
    if socketio:
        socketio.emit(event, data, room=f"colli_{colli_id}", skip_sid=skip_sid)
        logger.debug(f"Emit {event} to COLLI {colli_id}")


def broadcast(event: str, data: dict):
    """
    Emet un evenement a tous les clients connectes.

    Args:
        event: Nom de l'evenement
        data: Donnees a envoyer
    """
    if socketio:
        socketio.emit(event, data, broadcast=True)
        logger.debug(f"Broadcast {event}")


# =============================================================================
# NOTIFICATIONS SPECIFIQUES
# =============================================================================

def notify_new_letter(colli_id: str, letter_data: dict, author_id: str = None):
    """Notifie les membres d'un COLLI d'une nouvelle lettre."""
    emit_to_colli(colli_id, 'new_letter', {
        'type': 'new_letter',
        'colli_id': colli_id,
        'letter': letter_data
    })


def notify_new_comment(colli_id: str, letter_id: str, comment_data: dict):
    """Notifie les membres d'un nouveau commentaire."""
    emit_to_colli(colli_id, 'new_comment', {
        'type': 'new_comment',
        'colli_id': colli_id,
        'letter_id': letter_id,
        'comment': comment_data
    })


def notify_colli_status_change(colli_id: str, status: str, colli_name: str):
    """Notifie du changement de statut d'un COLLI."""
    emit_to_colli(colli_id, 'colli_status_changed', {
        'type': 'colli_status_changed',
        'colli_id': colli_id,
        'status': status,
        'name': colli_name
    })


def notify_user_joined_colli(colli_id: str, user_data: dict):
    """Notifie qu'un utilisateur a rejoint le COLLI."""
    emit_to_colli(colli_id, 'user_joined', {
        'type': 'user_joined',
        'colli_id': colli_id,
        'user': user_data
    })


def push_notification(user_id: str, notification_data: dict):
    """
    Envoie une notification push a un utilisateur.

    Args:
        user_id: ID de l'utilisateur cible
        notification_data: Contenu de la notification
    """
    emit_to_user(user_id, 'notification', {
        'type': 'notification',
        **notification_data
    })
