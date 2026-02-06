# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Routes de gestion des sondages
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.poll_service import PollService
from app.services.user_service import UserService

polls_bp = Blueprint('polls', __name__)


@polls_bp.route('/', methods=['GET'])
def get_all_polls():
    """Récupère tous les sondages actifs"""
    try:
        polls = PollService.get_all_polls()
        return jsonify({
            'success': True,
            'polls': [poll.to_dict(include_votes=True) for poll in polls]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@polls_bp.route('/', methods=['POST'])
@jwt_required()
def create_poll():
    """Crée un nouveau sondage"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation des données
        required_fields = ['title', 'options']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Le champ {field} est requis'
                }), 400
        
        if not isinstance(data['options'], list) or len(data['options']) < 2:
            return jsonify({
                'success': False,
                'message': 'Au moins 2 options sont requises'
            }), 400
        
        result = PollService.create_poll(
            title=data['title'],
            description=data.get('description', ''),
            created_by=current_user_id,
            options=data['options'],
            allow_multiple_votes=data.get('allow_multiple_votes', False)
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'poll': result['poll'].to_dict(include_votes=True)
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


@polls_bp.route('/<int:poll_id>', methods=['GET'])
def get_poll(poll_id):
    """Récupère un sondage par son ID"""
    try:
        poll = PollService.get_poll_by_id(poll_id)
        if not poll:
            return jsonify({
                'success': False,
                'message': 'Sondage non trouvé'
            }), 404
        
        return jsonify({
            'success': True,
            'poll': poll.to_dict(include_votes=True)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@polls_bp.route('/<int:poll_id>/vote', methods=['POST'])
@jwt_required()
def vote_on_poll(poll_id):
    """Vote sur un sondage"""
    try:
        current_user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Validation des données
        if not data.get('option_id'):
            return jsonify({
                'success': False,
                'message': 'ID de l\'option requis'
            }), 400
        
        result = PollService.vote_on_poll(
            user_id=current_user_id,
            poll_id=poll_id,
            option_id=data['option_id']
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
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


@polls_bp.route('/<int:poll_id>/results', methods=['GET'])
def get_poll_results(poll_id):
    """Récupère les résultats d'un sondage"""
    try:
        result = PollService.get_poll_results(poll_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'results': result['results']
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


@polls_bp.route('/<int:poll_id>/has-voted', methods=['GET'])
@jwt_required()
def has_user_voted(poll_id):
    """Vérifie si l'utilisateur connecté a voté sur le sondage"""
    try:
        current_user_id = int(get_jwt_identity())
        has_voted = PollService.has_user_voted(current_user_id, poll_id)
        
        return jsonify({
            'success': True,
            'has_voted': has_voted
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500


@polls_bp.route('/<int:poll_id>', methods=['DELETE'])
@jwt_required()
def delete_poll(poll_id):
    """Supprime un sondage"""
    try:
        current_user_id = int(get_jwt_identity())
        
        result = PollService.delete_poll(poll_id, current_user_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 403 if 'droits' in result['message'] else 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500
