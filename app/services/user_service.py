# ALVS IA pipeline test

# =============================================================================
# ALVS IA pipeline test - Processed by multi-agent AI system
# Timestamp: 2024-12-19 14:30:45 UTC
# Purpose: Validate AI pipeline coordination between backend and frontend
# =============================================================================

from app.extensions import db
from app.models.user import User
from sqlalchemy.exc import IntegrityError

class UserService:
    @staticmethod
    def create_user(email, password, first_name, last_name, role='user'):
        try:
            user = User(email=email, password=password, first_name=first_name, last_name=last_name, role=role)
            db.session.add(user)
            db.session.commit()
            return {'success': True, 'message': 'Utilisateur créé avec succès', 'user': user}
        except IntegrityError:
            db.session.rollback()
            return {'success': False, 'message': 'Un utilisateur avec cet email existe déjà', 'user': None}

    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return {'success': True, 'message': 'Connexion réussie', 'user': user}
        return {'success': False, 'message': 'Email ou mot de passe incorrect', 'user': None}

    @staticmethod
    def change_password(user_id, old_password, new_password):
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'Utilisateur non trouvé'}
        if not user.check_password(old_password):
            return {'success': False, 'message': 'Ancien mot de passe incorrect'}
        user.set_password(new_password)
        db.session.commit()
        return {'success': True, 'message': 'Mot de passe changé avec succès'}

    @staticmethod
    def update_user(user_id, **kwargs):
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'Utilisateur non trouvé', 'user': None}
        for key, value in kwargs.items():
            if key == 'password':
                user.set_password(value)
            elif hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return {'success': True, 'message': 'Utilisateur mis à jour avec succès', 'user': user}

    @staticmethod
    def delete_user(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'message': 'Utilisateur non trouvé'}
        db.session.delete(user)
        db.session.commit()
        return {'success': True, 'message': 'Utilisateur supprimé avec succès'}

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all_users():
        return User.query.all()