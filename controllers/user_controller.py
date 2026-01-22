from flask import Blueprint, request, jsonify
from http import HTTPStatus
from services.user_service import UserService


user_bp = Blueprint('user', __name__)
user_service = UserService()


@user_bp.get('')
def get_all_users():
    users = user_service.get_all_users()
    return jsonify(users), HTTPStatus.OK


@user_bp.post('')
def create_user():
    data = request.get_json()
    if user_service.check_email_exists(data.get('email')):
        return jsonify({'error': 'Email already exists'}), HTTPStatus.CONFLICT
    
    new_user = user_service.create_user(data)
    return jsonify(new_user), HTTPStatus.CREATED


@user_bp.get('/<string:user_id>')
def get_user_by_id(user_id):
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), HTTPStatus.NOT_FOUND
    return jsonify(user), HTTPStatus.OK


@user_bp.put('/<string:user_id>')
def update_user_by_id(user_id):
    data = request.get_json()
    new_email = data.get('email')
    
    if new_email:
        existing_user = user_service.get_user_by_email(new_email)
        
        if existing_user and existing_user['id'] != user_id:
            return jsonify({'error': 'Email already exists'}), HTTPStatus.CONFLICT
        
    updated_user = user_service.update_user_by_id(user_id, data)
    
    if not updated_user:
        return jsonify({'error': 'User not found'}), HTTPStatus.NOT_FOUND
    
    return jsonify(updated_user), HTTPStatus.OK


@user_bp.delete('/<string:user_id>')
def delete_user_by_id(user_id):
    success = user_service.delete_user_by_id(user_id)
    
    if not success:
        return jsonify({'error': 'User not found'}), HTTPStatus.NOT_FOUND
    
    return '', HTTPStatus.NO_CONTENT


@user_bp.post('/login')
def login_user():
    data_from_service = user_service.login_user() # TO DO at end
    return data_from_service