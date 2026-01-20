from flask import Blueprint
from services.user_service import UserService


user_bp = Blueprint('user', __name__)
user_service = UserService()


@user_bp.get('')
def get_all_users():
    data_from_service = user_service.get_all_users()
    return data_from_service


@user_bp.post('')
def create_user():
    data_from_service = user_service.create_user()
    return data_from_service


@user_bp.get('/<int:user_id>')
def get_user_by_id(user_id):
    data_from_service = user_service.get_user_by_id(user_id)
    return data_from_service


@user_bp.put('/<int:user_id>')
def update_user_by_id(user_id):
    data_from_service = user_service.update_user_by_id(user_id)
    return data_from_service


@user_bp.delete('/<int:user_id>')
def delete_user_by_id(user_id):
    data_from_service = user_service.delete_user_by_id(user_id)
    return data_from_service


@user_bp.post('/login')
def login_user():
    data_from_service = user_service.login_user()
    return data_from_service