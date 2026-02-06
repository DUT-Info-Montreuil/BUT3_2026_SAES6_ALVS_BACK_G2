from flask import jsonify
from typing import Any, Dict, Optional

def success_response(data: Any = None, status_code: int = 200) -> tuple:
    """Génère une réponse de succès standardisée"""
    response = {
        'success': True,
        'data': data
    }
    
    if isinstance(data, dict) and 'message' in data:
        response['message'] = data['message']
    
    return jsonify(response), status_code

def error_response(message: str, status_code: int = 400, details: Optional[Dict] = None) -> tuple:
    """Génère une réponse d'erreur standardisée"""
    response = {
        'success': False,
        'message': message,
        'error': {
            'code': status_code,
            'message': message
        }
    }
    
    if details:
        response['error']['details'] = details
    
    return jsonify(response), status_code

def validation_error_response(errors: Dict[str, str], status_code: int = 400) -> tuple:
    """Génère une réponse d'erreur de validation standardisée"""
    response = {
        'success': False,
        'message': 'Erreurs de validation',
        'error': {
            'code': status_code,
            'message': 'Erreurs de validation',
            'validation_errors': errors
        }
    }
    
    return jsonify(response), status_code

def paginated_response(data: list, page: int, per_page: int, total: int, status_code: int = 200) -> tuple:
    """Génère une réponse paginée standardisée"""
    total_pages = (total + per_page - 1) // per_page
    
    response = {
        'success': True,
        'data': data,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }
    
    return jsonify(response), status_code