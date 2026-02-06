# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Routes de gestion des utilisateurs
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.user_service import UserService

users_bp = Blueprint('users', __name__)


def admin_required(f):
    """Décorateur pour vérifier les droits admin"""
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = UserService.get_user_by_id(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Droits administrateur requis'
            }), 403
            
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function


@users_bp.route('/', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Récupère tous les utilisateurs (admin uniquement)"""
    try:
        users = UserService.get_all_users()
        return jsonify({
            'success': True,
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Récupère un utilisateur par son ID"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = UserService.get_user_by_id(current_user_id)
        
        # Vérifier les droits (utilisateur lui-même ou admin)
        if current_user_id != user_id and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Accès non autorisé'
            }), 403
        
        user = UserService.get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'message': 'Utilisateur non trouvé'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Met à jour un utilisateur"""
    try:
        current_user_id = int(get_jwt_identity())
        current_user = UserService.get_user_by_id(current_user_id)
        
        # Vérifier les droits (utilisateur lui-même ou admin)
        if current_user_id != user_id and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Accès non autorisé'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Données requises'
            }), 400
        
        # Empêcher les utilisateurs non-admin de changer le rôle
        if 'role' in data and current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Seuls les administrateurs peuvent modifier les rôles'
            }), 403
        
        result = UserService.update_user(user_id, **data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'user': result['user'].to_dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Supprime un utilisateur (admin uniquement)"""
    try:
        result = UserService.delete_user(user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@users_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change le mot de passe de l'utilisateur connecté"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation des données
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({
                'success': False,
                'message': 'Ancien et nouveau mot de passe requis'
            }), 400
        
        result = UserService.change_password(
            user_id=current_user_id,
            old_password=data['old_password'],
            new_password=data['new_password']
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500
