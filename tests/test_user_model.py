# ALVS IA pipeline test - Fichier traité par le système multi-agent IA
# Ce commentaire valide le bon fonctionnement du pipeline de développement automatisé

import pytest
from datetime import datetime
from app.models.user import User
from app.extensions import db

class TestUserModel:
    """Tests pour le modèle utilisateur"""
    
    def test_user_creation(self, app):
        """Test la création d'un utilisateur"""
        with app.app_context():
            user = User(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            assert user.first_name == 'Test'
            assert user.last_name == 'User'
            assert user.email == 'test@example.com'
            assert user.id is None  # Pas encore sauvé
    
    def test_user_save(self, app):
        """Test la sauvegarde d'un utilisateur"""
        with app.app_context():
            user = User(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert isinstance(user.created_at, datetime)
            assert isinstance(user.updated_at, datetime)
    
    def test_user_to_dict(self, app):
        """Test la conversion d'un utilisateur en dictionnaire"""
        with app.app_context():
            user = User(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            assert isinstance(user_dict, dict)
            assert user_dict['id'] == user.id
            assert user_dict['first_name'] == 'Test'
            assert user_dict['last_name'] == 'User'
            assert user_dict['email'] == 'test@example.com'
            assert 'created_at' in user_dict
            assert 'updated_at' in user_dict
    
    def test_user_repr(self, app):
        """Test la représentation string d'un utilisateur"""
        with app.app_context():
            user = User(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            assert str(user) == '<User test@example.com>'
    
    def test_user_unique_email(self, app):
        """Test l'unicité de l'email"""
        with app.app_context():
            user1 = User(
                email='test@example.com',
                password='password123',
                first_name='User',
                last_name='One'
            )
            user2 = User(
                email='test@example.com',
                password='password456',
                first_name='User',
                last_name='Two'
            )
            
            db.session.add(user1)
            db.session.commit()
            
            db.session.add(user2)
            
            with pytest.raises(Exception):  # Violation de contrainte d'unicité
                db.session.commit()
