# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Tests des services
"""

import pytest
from app.services.user_service import UserService
from app.services.poll_service import PollService
from app.models.user import User
from app.models.poll import Poll, Option, Vote
from app.extensions import db


class TestUserService:
    """Tests du service UserService"""
    
    def test_create_user_success(self, app):
        """Test de création d'utilisateur réussie"""
        with app.app_context():
            result = UserService.create_user(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            
            assert result['success'] is True
            assert result['user'] is not None
            assert result['user'].email == 'test@example.com'
            assert result['user'].first_name == 'Test'
            assert result['user'].last_name == 'User'
    
    def test_create_user_duplicate_email(self, app, test_user):
        """Test de création d'utilisateur avec email existant"""
        with app.app_context():
            result = UserService.create_user(
                email=test_user['email'],
                password='password123',
                first_name='Test',
                last_name='User'
            )
            
            assert result['success'] is False
            assert 'existe déjà' in result['message']
            assert result['user'] is None
    
    def test_authenticate_user_success(self, app, test_user):
        """Test d'authentification réussie"""
        with app.app_context():
            result = UserService.authenticate_user(
                email=test_user['email'],
                password=test_user['password']
            )
            
            assert result['success'] is True
            assert result['user'] is not None
            assert result['user'].id == test_user['id']
    
    def test_authenticate_user_invalid_credentials(self, app, test_user):
        """Test d'authentification avec mauvais identifiants"""
        with app.app_context():
            result = UserService.authenticate_user(
                email=test_user['email'],
                password='wrongpassword'
            )
            
            assert result['success'] is False
            assert 'incorrect' in result['message']
            assert result['user'] is None
    
    def test_get_user_by_id(self, app, test_user):
        """Test de récupération d'utilisateur par ID"""
        with app.app_context():
            user = UserService.get_user_by_id(test_user['id'])
            
            assert user is not None
            assert user.id == test_user['id']
            assert user.email == test_user['email']
    
    def test_get_user_by_email(self, app, test_user):
        """Test de récupération d'utilisateur par email"""
        with app.app_context():
            user = UserService.get_user_by_email(test_user['email'])
            
            assert user is not None
            assert user.id == test_user['id']
            assert user.email == test_user['email']
    
    def test_update_user(self, app, test_user):
        """Test de mise à jour d'utilisateur"""
        with app.app_context():
            result = UserService.update_user(
                user_id=test_user['id'],
                first_name='Updated',
                last_name='Name'
            )
            
            assert result['success'] is True
            assert result['user'].first_name == 'Updated'
            assert result['user'].last_name == 'Name'
    
    def test_change_password(self, app, test_user):
        """Test de changement de mot de passe"""
        with app.app_context():
            result = UserService.change_password(
                user_id=test_user['id'],
                old_password=test_user['password'],
                new_password='newpassword123'
            )
            
            assert result['success'] is True
            
            # Vérifier que le nouveau mot de passe fonctionne
            updated_user = UserService.get_user_by_id(test_user['id'])
            assert updated_user.check_password('newpassword123') is True
            assert updated_user.check_password('password123') is False


class TestPollService:
    """Tests du service PollService"""
    
    def test_create_poll_success(self, app, test_user):
        """Test de création de sondage réussie"""
        with app.app_context():
            result = PollService.create_poll(
                title='Test Poll',
                description='A test poll',
                created_by=test_user['id'],
                options=['Option 1', 'Option 2']
            )
            
            assert result['success'] is True
            assert result['poll'] is not None
            assert result['poll'].title == 'Test Poll'
            assert len(result['poll'].options) == 2
    
    def test_get_poll_by_id(self, app, test_poll):
        """Test de récupération de sondage par ID"""
        with app.app_context():
            poll = PollService.get_poll_by_id(test_poll['id'])
            
            assert poll is not None
            assert poll.id == test_poll['id']
            assert poll.title == test_poll['title']
    
    def test_vote_on_poll_success(self, app, test_user, test_poll):
        """Test de vote réussi"""
        with app.app_context():
            option = test_poll['options'][0]
            
            result = PollService.vote_on_poll(
                user_id=test_user['id'],
                poll_id=test_poll['id'],
                option_id=option['id']
            )
            
            assert result['success'] is True
            assert result['vote'] is not None
    
    def test_vote_on_poll_twice_not_allowed(self, app, test_user, test_poll):
        """Test de vote multiple non autorisé"""
        with app.app_context():
            option = test_poll['options'][0]
            
            # Premier vote
            PollService.vote_on_poll(
                user_id=test_user['id'],
                poll_id=test_poll['id'],
                option_id=option['id']
            )
            
            # Deuxième vote (doit échouer)
            result = PollService.vote_on_poll(
                user_id=test_user['id'],
                poll_id=test_poll['id'],
                option_id=option['id']
            )
            
            assert result['success'] is False
            assert 'déjà voté' in result['message']
    
    def test_has_user_voted(self, app, test_user, test_poll):
        """Test de vérification de vote"""
        with app.app_context():
            # Avant le vote
            has_voted = PollService.has_user_voted(test_user['id'], test_poll['id'])
            assert has_voted is False
            
            # Après le vote
            option = test_poll['options'][0]
            PollService.vote_on_poll(
                user_id=test_user['id'],
                poll_id=test_poll['id'],
                option_id=option['id']
            )
            
            has_voted = PollService.has_user_voted(test_user['id'], test_poll['id'])
            assert has_voted is True
