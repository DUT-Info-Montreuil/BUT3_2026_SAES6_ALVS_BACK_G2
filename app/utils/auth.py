from functools import wraps
from flask import request, jsonify, current_app
from app.services.user_service import UserService

def token_required(f):
    """Décorateur pour vérifier l'authentification JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Récupération du token depuis l'en-tête Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Format: "Bearer <token>"
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Format du token invalide'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token manquant'
            }), 401
        
        try:
            user_service = UserService()
            current_user = user_service.verify_token(token)
            
            if not current_user:
                return jsonify({
                    'success': False,
                    'message': 'Token invalide ou expiré'
                }), 401
                
        except Exception as e:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de la vérification du token'
            }), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated