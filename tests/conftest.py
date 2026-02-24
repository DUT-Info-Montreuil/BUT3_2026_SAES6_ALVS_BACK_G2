# tests/conftest.py
"""Fixtures pytest partagées pour tous les tests."""

import os
import pytest
from uuid import uuid4

# Force l'environnement de test AVANT tout import de settings
os.environ['FLASK_ENV'] = 'testing'

from src.infrastructure.config.settings import reset_settings


@pytest.fixture(autouse=True)
def _reset_state():
    """Réinitialise l'état global entre chaque test."""
    reset_settings()
    yield
    reset_settings()


@pytest.fixture
def app():
    """Crée une instance de l'application pour les tests."""
    from src.infrastructure.web.app import create_app
    from src.infrastructure.container import container
    from src.infrastructure.persistence.sqlalchemy.database import Base

    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-minimum-32-characters',
        'JWT_SECRET_KEY': 'test-jwt-secret-key-minimum-32-characters',
    })

    # S'assurer que les tables existent
    with app.app_context():
        engine = container.engine()
        Base.metadata.create_all(bind=engine)

    yield app

    # Nettoyage : supprimer toutes les tables après le test
    with app.app_context():
        engine = container.engine()
        Base.metadata.drop_all(bind=engine)

    # Reset container singletons pour le prochain test
    container.engine.reset()
    container.session_factory.reset()
    container.db_session.reset()


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


@pytest.fixture
def admin_headers(admin_auth_headers):
    """Alias pour admin_auth_headers (compatibilite)."""
    return admin_auth_headers


@pytest.fixture
def registered_user(app, client):
    """Cree un utilisateur enregistre pour les tests."""
    user_data = {
        'email': f'test_{uuid4().hex[:8]}@example.com',
        'password': 'TestPassword123!',
        'password_confirm': 'TestPassword123!',
        'first_name': 'Test',
        'last_name': 'User'
    }

    with app.app_context():
        response = client.post('/api/v1/auth/register', json=user_data)
        if response.status_code == 201:
            data = response.get_json()
            return {
                'email': user_data['email'],
                'password': user_data['password'],
                'user_id': data.get('user', {}).get('id'),
                'access_token': data.get('access_token')
            }

    # Fallback si l'endpoint échoue
    return {
        'email': user_data['email'],
        'password': user_data['password'],
        'user_id': str(uuid4())
    }


@pytest.fixture
def setup_colli(app, client, auth_headers, sample_colli_data):
    """Cree un COLLI pour les tests."""
    with app.app_context():
        response = client.post(
            '/api/v1/collis',
            headers=auth_headers,
            json=sample_colli_data
        )

        if response.status_code == 201:
            data = response.get_json()
            return {
                'colli_id': data.get('id'),
                'name': sample_colli_data['name']
            }

    # Fallback
    return {
        'colli_id': str(uuid4()),
        'name': sample_colli_data['name']
    }
