# -*- coding: utf-8 -*-
"""
Routes utilisateur
"""

from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from flask_jwt_extended import jwt_required, get_jwt_identity

bp = Blueprint('user', __name__, url_prefix='/api/users')


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Récupérer un utilisateur par son ID"""
    try:
        user = UserService.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Mettre à jour un utilisateur"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Vérifier que l'utilisateur ne peut modifier que ses propres données
        if current_user_id != user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400
        
        user = UserService.update_user(user_id, **data)
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({
            'message': 'Utilisateur mis à jour avec succès',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Supprimer un utilisateur"""
    try:
        current_user_id = int(get_jwt_identity())
        
        # Vérifier que l'utilisateur ne peut supprimer que son propre compte
        if current_user_id != user_id:
            return jsonify({'error': 'Non autorisé'}), 403
        
        success = UserService.delete_user(user_id)
        
        if not success:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
