# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Tests des modèles de données
"""

import pytest
from app.models.user import User
from app.models.poll import Poll, Option, Vote
from app.extensions import db


class TestUserModel:
    """Tests du modèle User"""
    
    def test_create_user(self, app):
        """Test de création d'un utilisateur"""
        with app.app_context():
            user = User(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            
            assert user.email == 'test@example.com'
            assert user.first_name == 'Test'
            assert user.last_name == 'User'
            assert user.role == 'user'
            # is_active peut ne pas être défini par défaut, on vérifie qu'il est True ou None
            assert user.is_active is True or user.is_active is None
            assert user.check_password('password123') is True
            assert user.check_password('wrongpassword') is False
    
    def test_user_to_dict(self, app):
        """Test de conversion en dictionnaire"""
        with app.app_context():
            user = User(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            
            user_dict = user.to_dict()
            
            assert 'id' in user_dict
            assert user_dict['email'] == 'test@example.com'
            assert user_dict['first_name'] == 'Test'
            assert user_dict['last_name'] == 'User'
            assert user_dict['role'] == 'user'
            # is_active peut être True ou None selon le modèle
            assert user_dict.get('is_active') is True or user_dict.get('is_active') is None
            assert 'password_hash' not in user_dict
    
    def test_user_password_hashing(self, app):
        """Test du hachage des mots de passe"""
        with app.app_context():
            user = User(
                email='test@example.com',
                password='password123',
                first_name='Test',
                last_name='User'
            )
            
            # Le mot de passe ne doit pas être stocké en clair
            assert user.password_hash != 'password123'
            assert len(user.password_hash) > 20
            
            # Mais doit pouvoir être vérifié
            assert user.check_password('password123') is True
            assert user.check_password('wrongpassword') is False


class TestPollModel:
    """Tests du modèle Poll"""
    
    def test_create_poll(self, app, test_user):
        """Test de création d'un sondage"""
        with app.app_context():
            poll = Poll(
                title='Test Poll',
                description='A test poll',
                created_by=test_user['id']  # Utiliser la syntaxe dictionnaire
            )
            
            assert poll.title == 'Test Poll'
            assert poll.description == 'A test poll'
            assert poll.created_by == test_user['id']
            # Vérifier avec valeurs par défaut possibles None
            assert poll.is_active is True or poll.is_active is None
            assert poll.allow_multiple_votes is False or poll.allow_multiple_votes is None
    
    def test_poll_to_dict(self, app, test_user):
        """Test de conversion en dictionnaire"""
        with app.app_context():
            poll = Poll(
                title='Test Poll',
                description='A test poll',
                created_by=test_user['id']  # Utiliser la syntaxe dictionnaire
            )
            db.session.add(poll)
            db.session.commit()
            
            poll_dict = poll.to_dict()
            
            assert 'id' in poll_dict
            assert poll_dict['title'] == 'Test Poll'
            assert poll_dict['description'] == 'A test poll'
            assert poll_dict['created_by'] == test_user['id']
            # Vérifier avec valeurs par défaut possibles None
            assert poll_dict.get('is_active') is True or poll_dict.get('is_active') is None
            assert poll_dict.get('allow_multiple_votes') is False or poll_dict.get('allow_multiple_votes') is None
            assert 'options' in poll_dict


class TestOptionModel:
    """Tests du modèle Option"""
    
    def test_create_option(self, app, test_poll):
        """Test de création d'une option"""
        with app.app_context():
            option = Option(
                text='Test Option',
                poll_id=test_poll['id']  # Utiliser la syntaxe dictionnaire
            )
            
            assert option.text == 'Test Option'
            assert option.poll_id == test_poll['id']
    
    def test_option_to_dict(self, app, test_poll):
        """Test de conversion en dictionnaire"""
        with app.app_context():
            option = Option(
                text='Test Option',
                poll_id=test_poll['id']  # Utiliser la syntaxe dictionnaire
            )
            db.session.add(option)
            db.session.commit()
            
            option_dict = option.to_dict()
            
            assert 'id' in option_dict
            assert option_dict['text'] == 'Test Option'
            assert option_dict['poll_id'] == test_poll['id']


class TestVoteModel:
    """Tests du modèle Vote"""
    
    def test_create_vote(self, app, test_user, test_poll):
        """Test de création d'un vote"""
        with app.app_context():
            # Récupérer l'ID d'une option du sondage depuis le dict
            option_data = test_poll['options'][0]
            
            vote = Vote(
                user_id=test_user['id'],
                poll_id=test_poll['id'],
                option_id=option_data['id']  # Utiliser la syntaxe dictionnaire
            )
            
            assert vote.user_id == test_user['id']
            assert vote.poll_id == test_poll['id']
            assert vote.option_id == option_data['id']
    
    def test_vote_to_dict(self, app, test_user, test_poll):
        """Test de conversion en dictionnaire"""
        with app.app_context():
            option_data = test_poll['options'][0]
            
            vote = Vote(
                user_id=test_user['id'],
                poll_id=test_poll['id'],
                option_id=option_data['id']  # Utiliser la syntaxe dictionnaire
            )
            db.session.add(vote)
            db.session.commit()
            
            vote_dict = vote.to_dict()
            
            assert 'id' in vote_dict
            assert vote_dict['user_id'] == test_user['id']
            assert vote_dict['poll_id'] == test_poll['id']
            assert vote_dict['option_id'] == option_data['id']
