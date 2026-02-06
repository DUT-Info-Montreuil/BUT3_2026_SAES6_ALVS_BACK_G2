# ALVS IA pipeline test - Fichier traité par le système multi-agent IA
# Ce commentaire valide le bon fonctionnement du pipeline de développement automatisé

from app.models.user import User
from app.extensions import db

class UserRepository:
    def get_all(self):
        """Récupère tous les utilisateurs"""
        users = User.query.all()
        return [user.to_dict() for user in users]
    
    def get_by_id(self, user_id):
        """Récupère un utilisateur par son ID"""
        user = User.query.get(user_id)
        return user.to_dict() if user else None
    
    def create(self, user_data):
        """Crée un nouvel utilisateur"""
        user = User(
            name=user_data['name'],
            email=user_data['email']
        )
        db.session.add(user)
        db.session.commit()
        return user.to_dict()
    
    def update(self, user_id, user_data):
        """Met à jour un utilisateur"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.session.commit()
        return user.to_dict()
    
    def delete(self, user_id):
        """Supprime un utilisateur"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True
