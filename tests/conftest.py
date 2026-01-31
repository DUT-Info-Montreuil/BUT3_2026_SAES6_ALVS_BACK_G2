# tests/conftest.py
"""Fixtures pytest partagées pour tous les tests."""

import pytest
from uuid import uuid4

from src.infrastructure.web.app import create_app


@pytest.fixture
def app():
    """Crée une instance de l'application pour les tests."""
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-minimum-32-characters',
        'JWT_SECRET_KEY': 'test-jwt-secret-key-minimum-32-characters',
    })
    
    yield app


@pytest.fixture
def client(app):
    """Client de test HTTP."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner pour les tests de commandes."""
    return app.test_cli_runner()


@pytest.fixture
def sample_user_id():
    """ID utilisateur de test."""
    return uuid4()


@pytest.fixture
def sample_colli_data():
    """Données de COLLI de test."""
    return {
        'name': 'Test COLLI',
        'theme': 'Littérature française',
        'description': 'Un COLLI de test pour les correspondances.'
    }


@pytest.fixture
def auth_headers(app, sample_user_id):
    """
    Génère des headers d'authentification JWT pour les tests.
    
    Usage:
        def test_protected_route(client, auth_headers):
            response = client.get('/api/v1/collis', headers=auth_headers)
    """
    from flask_jwt_extended import create_access_token
    
    with app.app_context():
        access_token = create_access_token(
            identity=str(sample_user_id),
            additional_claims={'role': 'teacher'}
        )
    
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def admin_auth_headers(app):
    """Headers d'authentification pour un admin."""
    from flask_jwt_extended import create_access_token
    
    with app.app_context():
        access_token = create_access_token(
            identity=str(uuid4()),
            additional_claims={'role': 'admin'}
        )
    
    return {'Authorization': f'Bearer {access_token}'}
