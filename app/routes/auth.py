# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Routes d'authentification
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.services.user_service import UserService

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Le champ {field} est requis'
                }), 400
        
        # Créer l'utilisateur
        result = UserService.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data.get('role', 'user')
        )
        
        if result['success']:
            user = result['user']
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 201
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


@auth_bp.route('/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    try:
        data = request.get_json()
        
        # Validation des données
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'message': 'Email et mot de passe requis'
            }), 400
        
        # Authentifier l'utilisateur
        result = UserService.authenticate_user(
            email=data['email'],
            password=data['password']
        )
        
        if result['success']:
            user = result['user']
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Rafraîchit le token d'accès"""
    try:
        current_user_id = int(get_jwt_identity())
        user = UserService.get_user_by_id(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Utilisateur non trouvé'
            }), 404
        
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'success': True,
            'message': 'Token rafraîchi avec succès',
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Récupère les informations de l'utilisateur connecté"""
    try:
        current_user_id = int(get_jwt_identity())
        user = UserService.get_user_by_id(current_user_id)
        
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
