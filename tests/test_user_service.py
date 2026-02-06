# -*- coding: utf-8 -*-
"""
Tests pour le service utilisateur
"""

import pytest
from app.services.user_service import UserService
from app.models.user import User
from app.extensions import db


class TestUserService:
    """Tests pour UserService"""
    
    def test_create_user_success(self, app):
        """Test de création d'utilisateur réussie"""
        with app.app_context():
            result = UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            
            assert result['success'] is True
            user = result['user']
            assert user is not None
            assert user.email == 'test@example.com'
            assert user.first_name == 'John'
            assert user.last_name == 'Doe'
            assert user.password_hash is not None
            assert user.password_hash != 'password123'  # Mot de passe hashé
    
    def test_create_user_duplicate_email(self, app):
        """Test de création d'utilisateur avec email existant"""
        with app.app_context():
            # Créer le premier utilisateur
            UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            
            # Tenter de créer un utilisateur avec le même email
            result = UserService.create_user(
                email='test@example.com',
                password='password456',
                first_name='Jane',
                last_name='Smith'
            )
            
            assert result['success'] is False
            assert result['user'] is None
    
    def test_authenticate_user_success(self, app):
        """Test d'authentification réussie"""
        with app.app_context():
            # Créer un utilisateur
            UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            
            # Tenter l'authentification
            result = UserService.authenticate_user('test@example.com', 'password123')
            
            assert result is not None
            assert result['success'] is True
            assert 'user' in result
            assert result['user'].email == 'test@example.com'
    
    def test_authenticate_user_invalid_credentials(self, app):
        """Test d'authentification avec identifiants invalides"""
        with app.app_context():
            # Créer un utilisateur
            UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            
            # Tenter l'authentification avec un mauvais mot de passe
            result = UserService.authenticate_user('test@example.com', 'wrongpassword')
            
            assert result['success'] is False
            assert result['user'] is None
    
    def test_get_user_by_id(self, app):
        """Test de récupération d'utilisateur par ID"""
        with app.app_context():
            # Créer un utilisateur
            result = UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            user = result['user']
            
            # Récupérer l'utilisateur par ID
            found_user = UserService.get_user_by_id(user.id)
            
            assert found_user is not None
            assert found_user.id == user.id
            assert found_user.email == 'test@example.com'
    
    def test_get_user_by_email(self, app):
        """Test de récupération d'utilisateur par email"""
        with app.app_context():
            # Créer un utilisateur
            result = UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            user = result['user']
            
            # Récupérer l'utilisateur par email
            found_user = UserService.get_user_by_email('test@example.com')
            
            assert found_user is not None
            assert found_user.id == user.id
            assert found_user.email == 'test@example.com'
    
    def test_update_user(self, app):
        """Test de mise à jour d'utilisateur"""
        with app.app_context():
            # Créer un utilisateur
            result = UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            user = result['user']
            
            # Mettre à jour l'utilisateur
            update_result = UserService.update_user(
                user.id,
                first_name='Jane',
                last_name='Smith'
            )
            
            assert update_result['success'] is True
            updated_user = update_result['user']
            assert updated_user is not None
            assert updated_user.first_name == 'Jane'
            assert updated_user.last_name == 'Smith'
            assert updated_user.email == 'test@example.com'  # Email inchangé
    
    def test_delete_user(self, app):
        """Test de suppression d'utilisateur"""
        with app.app_context():
            # Créer un utilisateur
            result = UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='John',
                last_name='Doe'
            )
            user = result['user']
            
            user_id = user.id
            
            # Supprimer l'utilisateur
            delete_result = UserService.delete_user(user_id)
            
            assert delete_result['success'] is True
            
            # Vérifier que l'utilisateur n'existe plus
            deleted_user = UserService.get_user_by_id(user_id)
            assert deleted_user is None
