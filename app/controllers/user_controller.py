# ALVS IA pipeline test - Fichier traité par le système multi-agent IA
# Ce commentaire valide le bon fonctionnement du pipeline de développement automatisé

from flask import Blueprint, request, jsonify
from app.services.user_service import UserService

user_bp = Blueprint('users', __name__)
user_service = UserService()

class UserController:
    def __init__(self):
        self.user_service = UserService()
    
    def get_users(self):
        """Récupère tous les utilisateurs"""
        try:
            users = self.user_service.get_all_users()
            return jsonify({'users': users}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def get_user(self, user_id):
        """Récupère un utilisateur par son ID"""
        try:
            user = self.user_service.get_user_by_id(user_id)
            if user:
                return jsonify({'user': user}), 200
            return jsonify({'error': 'User not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def create_user(self, user_data):
        """Crée un nouvel utilisateur"""
        try:
            user = self.user_service.create_user(user_data)
            return jsonify({'user': user}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 400

# Instance du contrôleur
user_controller = UserController()

@user_bp.route('/', methods=['GET'])
def get_users():
    return user_controller.get_users()

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return user_controller.get_user(user_id)

@user_bp.route('/', methods=['POST'])
def create_user():
    user_data = request.get_json()
    return user_controller.create_user(user_data)
