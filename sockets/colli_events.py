from flask import request
from flask_socketio import join_room, leave_room
from shared.socketio import socketio


@socketio.on('join_colli')
def handle_join_colli(data):
    colli_id = data.get('colli_id') if isinstance(data, dict) else data
    
    if colli_id:
        join_room(colli_id)
        print(f'Client {request.sid} joined room {colli_id}')
        
        
@socketio.on('leave_colli')
def handle_leave_colli(data):
    colli_id = data.get('colli_id') if isinstance(data, dict) else data
    if colli_id:
        leave_room(colli_id)
        print(f'Client {request.sid} left room {colli_id}')
        

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client {request.sid} disconnected')
    