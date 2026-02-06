# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Configuration des tests pytest
"""

import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models.user import User
from app.models.poll import Poll, Option


@pytest.fixture(scope='function')
def app():
    """Crée une instance de l'application pour les tests"""
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Client de test Flask"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Runner CLI pour les tests"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def test_user(app):
    """
    Utilisateur de test - Retourne un dictionnaire avec les infos essentielles
    pour éviter DetachedInstanceError
    """
    with app.app_context():
        user = User(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )
        db.session.add(user)
        db.session.commit()
        # Retourner un dict avec les infos nécessaires au lieu de l'objet SQLAlchemy
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'password': 'password123'  # Le mot de passe en clair pour les tests
        }
    return user_data


@pytest.fixture(scope='function')
def admin_user(app):
    """
    Utilisateur admin de test - Retourne un dictionnaire avec les infos essentielles
    """
    with app.app_context():
        user = User(
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        db.session.add(user)
        db.session.commit()
        user_data = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'password': 'admin123'
        }
    return user_data


@pytest.fixture(scope='function')
def test_poll(app, test_user):
    """Sondage de test - Retourne un dictionnaire"""
    with app.app_context():
        poll = Poll(
            title='Test Poll',
            description='A test poll',
            created_by=test_user['id']  # Utiliser la clé du dict
        )
        db.session.add(poll)
        db.session.flush()
        
        # Ajouter des options
        option1 = Option(text='Option 1', poll_id=poll.id)
        option2 = Option(text='Option 2', poll_id=poll.id)
        db.session.add(option1)
        db.session.add(option2)
        db.session.commit()
        
        poll_data = {
            'id': poll.id,
            'title': poll.title,
            'description': poll.description,
            'created_by': poll.created_by,
            'options': [
                {'id': option1.id, 'text': option1.text},
                {'id': option2.id, 'text': option2.text}
            ]
        }
    return poll_data


@pytest.fixture(scope='function')
def sample_user_data():
    """Données utilisateur pour les tests d'inscription"""
    return {
        'email': 'newuser@example.com',
        'password': 'newpassword123',
        'first_name': 'New',
        'last_name': 'User'
    }


@pytest.fixture(scope='function')
def auth_headers(client, test_user):
    """Headers d'authentification pour les tests"""
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],  # Utiliser la clé du dict
        'password': test_user['password']
    })
    
    data = response.get_json()
    if data and 'access_token' in data:
        token = data['access_token']
        return {'Authorization': f'Bearer {token}'}
    return {}


@pytest.fixture(scope='function')
def admin_auth_headers(client, admin_user):
    """Headers d'authentification admin pour les tests"""
    response = client.post('/api/auth/login', json={
        'email': admin_user['email'],  # Utiliser la clé du dict
        'password': admin_user['password']
    })
    
    data = response.get_json()
    if data and 'access_token' in data:
        token = data['access_token']
        return {'Authorization': f'Bearer {token}'}
    return {}
