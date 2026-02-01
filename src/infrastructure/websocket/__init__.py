# src/infrastructure/websocket/__init__.py
"""Module WebSocket avec Flask-SocketIO."""

from src.infrastructure.websocket.socket_manager import (
    init_socketio,
    get_socketio,
    emit_to_user,
    emit_to_colli,
    broadcast,
    is_user_online,
    get_online_users,
    notify_new_letter,
    notify_new_comment,
    notify_colli_status_change,
    notify_user_joined_colli,
    push_notification
)

__all__ = [
    'init_socketio',
    'get_socketio',
    'emit_to_user',
    'emit_to_colli',
    'broadcast',
    'is_user_online',
    'get_online_users',
    'notify_new_letter',
    'notify_new_comment',
    'notify_colli_status_change',
    'notify_user_joined_colli',
    'push_notification'
]
