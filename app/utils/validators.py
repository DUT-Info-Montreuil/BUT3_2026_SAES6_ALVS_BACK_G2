import re
from typing import Dict, Any

def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Valide les données d'un utilisateur"""
    
    if not data:
        return {'valid': False, 'message': 'Aucune donnée fournie'}
    
    # Validation du nom d'utilisateur
    username = data.get('username', '').strip()
    if not username:
        return {'valid': False, 'message': 'Le nom d\'utilisateur est requis'}
    
    if len(username) < 3:
        return {'valid': False, 'message': 'Le nom d\'utilisateur doit contenir au moins 3 caractères'}
    
    if len(username) > 80:
        return {'valid': False, 'message': 'Le nom d\'utilisateur ne peut pas dépasser 80 caractères'}
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return {'valid': False, 'message': 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores'}
    
    # Validation de l'email
    email = data.get('email', '').strip().lower()
    if not email:
        return {'valid': False, 'message': 'L\'adresse email est requise'}
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return {'valid': False, 'message': 'Format d\'email invalide'}
    
    if len(email) > 120:
        return {'valid': False, 'message': 'L\'adresse email ne peut pas dépasser 120 caractères'}
    
    # Validation du mot de passe
    password = data.get('password', '')
    if not password:
        return {'valid': False, 'message': 'Le mot de passe est requis'}
    
    if len(password) < 8:
        return {'valid': False, 'message': 'Le mot de passe doit contenir au moins 8 caractères'}
    
    if len(password) > 128:
        return {'valid': False, 'message': 'Le mot de passe ne peut pas dépasser 128 caractères'}
    
    # Vérification de la complexité du mot de passe
    if not re.search(r'[A-Z]', password):
        return {'valid': False, 'message': 'Le mot de passe doit contenir au moins une majuscule'}
    
    if not re.search(r'[a-z]', password):
        return {'valid': False, 'message': 'Le mot de passe doit contenir au moins une minuscule'}
    
    if not re.search(r'\d', password):
        return {'valid': False, 'message': 'Le mot de passe doit contenir au moins un chiffre'}
    
    return {'valid': True, 'message': 'Données valides'}

def validate_email(email: str) -> bool:
    """Valide une adresse email"""
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip().lower()))

def validate_username(username: str) -> bool:
    """Valide un nom d'utilisateur"""
    if not username:
        return False
    
    username = username.strip()
    
    if len(username) < 3 or len(username) > 80:
        return False
    
    return bool(re.match(r'^[a-zA-Z0-9_-]+$', username))

def validate_password(password: str) -> bool:
    """Valide un mot de passe"""
    if not password:
        return False
    
    if len(password) < 8 or len(password) > 128:
        return False
    
    # Vérification de la complexité
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    return has_upper and has_lower and has_digit