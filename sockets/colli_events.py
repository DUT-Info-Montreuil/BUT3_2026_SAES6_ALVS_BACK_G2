import logging
from flask import request
from flask_socketio import join_room, leave_room
from shared.socketio import socketio

logger = logging.getLogger(__name__)


@socketio.on('join_colli')
def handle_join_colli(data):
    colli_id = data.get('colli_id') if isinstance(data, dict) else data
    
    if colli_id:
        join_room(colli_id)
        logger.debug(f'Client {request.sid} joined room {colli_id}')
        
        
@socketio.on('leave_colli')
def handle_leave_colli(data):
    colli_id = data.get('colli_id') if isinstance(data, dict) else data
    if colli_id:
        leave_room(colli_id)
        logger.debug(f'Client {request.sid} left room {colli_id}')
        

@socketio.on('join_letter')
def handle_join_letter(data):
    letter_id = data.get('letter_id') if isinstance(data, dict) else data
    
    if letter_id:
        join_room(f'letter_{letter_id}')
        logger.debug(f'Client {request.sid} joined room {letter_id}')
        
        
@socketio.on('leave_letter')
def handle_leave_letter(data):
    letter_id = data.get('letter_id') if isinstance(data, dict) else data
    
    if letter_id:
        leave_room(f'letter_{letter_id}')
        logger.debug(f'Client {request.sid} left room {letter_id}')
        

@socketio.on('disconnect')
def handle_disconnect():
    logger.debug(f'Client {request.sid} disconnected')
    