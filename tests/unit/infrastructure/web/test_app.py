"""Tests unitaires pour le factory Flask de l'application ALVS."""

import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from src.infrastructure.web.app import create_app, SWAGGER_TEMPLATE, SWAGGER_CONFIG


class TestCreateApp:
    """Tests pour la factory create_app."""

    @patch('src.infrastructure.web.app.get_settings')
    @patch('src.infrastructure.web.app.init_jwt')
    @patch('src.infrastructure.web.app.init_rate_limiter')
    @patch('src.infrastructure.web.app.register_error_handlers')
    @patch('src.infrastructure.web.app.CORS')
    @patch('src.infrastructure.web.app.Swagger')
    @patch('redis.Redis')
    def test_create_app_default_config(self, mock_redis, mock_swagger, mock_cors, 
                                     mock_error_handlers, mock_rate_limiter, 
                                     mock_init_jwt, mock_settings):
        """Test création d'app avec configuration par défaut."""
        # Arrange
        mock_settings.return_value = MagicMock(
            SECRET_KEY='test-secret',
            REDIS_URL='redis://localhost:6379/0'
        )
        
        # Act
        app = create_app()
        
        # Assert
        assert isinstance(app, Flask)
        assert app.config['SECRET_KEY'] == 'test-secret'
        mock_cors.assert_called_once_with(app, origins=['http://localhost:5173'])
        mock_swagger.assert_called_once_with(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)
        mock_init_jwt.assert_called_once_with(app)
        mock_rate_limiter.assert_called_once()
        mock_error_handlers.assert_called_once_with(app)

    @patch.dict(os.environ, {'CORS_ORIGIN': 'https://alvs.example.com'})
    @patch('src.infrastructure.web.app.get_settings')
    @patch('src.infrastructure.web.app.init_jwt')
    @patch('src.infrastructure.web.app.init_rate_limiter')
    @patch('src.infrastructure.web.app.register_error_handlers')
    @patch('src.infrastructure.web.app.CORS')
    @patch('src.infrastructure.web.app.Swagger')
    @patch('redis.Redis')
    def test_create_app_custom_cors_origin(self, mock_redis, mock_swagger, mock_cors,
                                         mock_error_handlers, mock_rate_limiter,
                                         mock_init_jwt, mock_settings):
        """Test création d'app avec origine CORS personnalisée."""
        # Arrange
        mock_settings.return_value = MagicMock(
            SECRET_KEY='test-secret',
            REDIS_URL='redis://localhost:6379/0'
        )
        
        # Act
        app = create_app()
        
        # Assert
        mock_cors.assert_called_once_with(app, origins=['https://alvs.example.com'])

    @patch.dict(os.environ, {'CORS_ORIGIN': 'http://localhost:5173,https://alvs.example.com'})
    @patch('src.infrastructure.web.app.get_settings')
    @patch('src.infrastructure.web.app.init_jwt')
    @patch('src.infrastructure.web.app.init_rate_limiter')
    @patch('src.infrastructure.web.app.register_error_handlers')
    @patch('src.infrastructure.web.app.CORS')
    @patch('src.infrastructure.web.app.Swagger')
    @patch('redis.Redis')
    def test_create_app_multiple_cors_origins(self, mock_redis, mock_swagger, mock_cors,
                                            mock_error_handlers, mock_rate_limiter,
                                            mock_init_jwt, mock_settings):
        """Test création d'app avec multiples origines CORS."""
        # Arrange
        mock_settings.return_value = MagicMock(
            SECRET_KEY='test-secret',
            REDIS_URL='redis://localhost:6379/0'
        )
        
        # Act
        app = create_app()
        
        # Assert
        expected_origins = ['http://localhost:5173', 'https://alvs.example.com']
        mock_cors.assert_called_once_with(app, origins=expected_origins)

    @patch('src.infrastructure.web.app.get_settings')
    @patch('src.infrastructure.web.app.init_jwt')
    @patch('src.infrastructure.web.app.init_rate_limiter')
    @patch('src.infrastructure.web.app.register_error_handlers')
    @patch('src.infrastructure.web.app.CORS')
    @patch('src.infrastructure.web.app.Swagger')
    @patch('redis.Redis')
    def test_create_app_with_config_override(self, mock_redis, mock_swagger, mock_cors,
                                           mock_error_handlers, mock_rate_limiter,
                                           mock_init_jwt, mock_settings):
        """Test création d'app avec configuration personnalisée."""
        # Arrange
        mock_settings.return_value = MagicMock(
            SECRET_KEY='test-secret',
            REDIS_URL='redis://localhost:6379/0'
        )
        custom_config = {'TESTING': True, 'DEBUG': False}
        
        # Act
        app = create_app(config_override=custom_config)
        
        # Assert
        assert app.config['TESTING'] is True
        assert app.config['DEBUG'] is False

    @patch('src.infrastructure.web.app.get_settings')
    @patch('src.infrastructure.web.app.init_jwt', side_effect=Exception('JWT init failed'))
    @patch('src.infrastructure.web.app.init_rate_limiter')
    @patch('src.infrastructure.web.app.register_error_handlers')
    @patch('src.infrastructure.web.app.CORS')
    @patch('src.infrastructure.web.app.Swagger')
    @patch('redis.Redis')
    def test_create_app_jwt_init_failure(self, mock_redis, mock_swagger, mock_cors,
                                       mock_error_handlers, mock_rate_limiter,
                                       mock_init_jwt, mock_settings):
        """Test gestion d'erreur lors de l'initialisation JWT."""
        # Arrange
        mock_settings.return_value = MagicMock(
            SECRET_KEY='test-secret',
            REDIS_URL='redis://localhost:6379/0'
        )
        
        # Act & Assert
        with pytest.raises(Exception, match='JWT init failed'):
            create_app()

    @patch('src.infrastructure.web.app.get_settings')
    @patch('src.infrastructure.web.app.init_jwt')
    @patch('src.infrastructure.web.app.init_rate_limiter', side_effect=Exception('Rate limiter failed'))
    @patch('src.infrastructure.web.app.register_error_handlers')
    @patch('src.infrastructure.web.app.CORS')
    @patch('src.infrastructure.web.app.Swagger')
    @patch('redis.Redis')
    def test_create_app_rate_limiter_failure(self, mock_redis, mock_swagger, mock_cors,
                                           mock_error_handlers, mock_rate_limiter,
                                           mock_init_jwt, mock_settings):
        """Test gestion d'erreur lors de l'initialisation du rate limiter."""
        # Arrange
        mock_settings.return_value = MagicMock(
            SECRET_KEY='test-secret',
            REDIS_URL='redis://localhost:6379/0'
        )
        
        # Act & Assert
        with pytest.raises(Exception, match='Rate limiter failed'):
            create_app()

    @patch.dict(os.environ, {}, clear=True)
    @patch('src.infrastructure.web.app.get_settings')
    @patch('src.infrastructure.web.app.init_jwt')
    @patch('src.infrastructure.web.app.init_rate_limiter')
    @patch('src.infrastructure.web.app.register_error_handlers')
    @patch('src.infrastructure.web.app.CORS')
    @patch('src.infrastructure.web.app.Swagger')
    @patch('redis.Redis')
    def test_create_app_no_cors_env_var(self, mock_redis, mock_swagger, mock_cors,
                                      mock_error_handlers, mock_rate_limiter,
                                      mock_init_jwt, mock_settings):
        """Test création d'app sans variable d'environnement CORS_ORIGIN."""
        # Arrange
        mock_settings.return_value = MagicMock(
            SECRET_KEY='test-secret',
            REDIS_URL='redis://localhost:6379/0'
        )
        
        # Act
        app = create_app()
        
        # Assert - doit utiliser la valeur par défaut
        mock_cors.assert_called_once_with(app, origins=['http://localhost:5173'])


class TestSwaggerTemplate:
    """Tests pour la configuration Swagger."""

    def test_swagger_template_structure(self):
        """Test structure du template Swagger."""
        # Assert
        assert SWAGGER_TEMPLATE['openapi'] == '3.0.3'
        assert SWAGGER_TEMPLATE['info']['title'] == 'ALVS API'
        assert SWAGGER_TEMPLATE['info']['version'] == '1.0.0'
        assert 'components' in SWAGGER_TEMPLATE
        assert 'securitySchemes' in SWAGGER_TEMPLATE['components']
        assert 'schemas' in SWAGGER_TEMPLATE['components']
        assert 'responses' in SWAGGER_TEMPLATE['components']

    def test_swagger_security_schemes(self):
        """Test configuration des schémas de sécurité Swagger."""
        # Assert
        bearer_auth = SWAGGER_TEMPLATE['components']['securitySchemes']['BearerAuth']
        assert bearer_auth['type'] == 'http'
        assert bearer_auth['scheme'] == 'bearer'
        assert bearer_auth['bearerFormat'] == 'JWT'

    def test_swagger_schemas_presence(self):
        """Test présence des schémas essentiels dans Swagger."""
        # Assert
        schemas = SWAGGER_TEMPLATE['components']['schemas']
        required_schemas = ['Error', 'LoginRequest', 'LoginResponse', 'User', 'Colli', 'Letter', 'Comment']
        
        for schema in required_schemas:
            assert schema in schemas, f"Schéma {schema} manquant"

    def test_swagger_responses_presence(self):
        """Test présence des réponses standard dans Swagger."""
        # Assert
        responses = SWAGGER_TEMPLATE['components']['responses']
        required_responses = ['NotFound', 'Unauthorized', 'Forbidden', 'RateLimited', 'ValidationError']
        
        for response in required_responses:
            assert response in responses, f"Réponse {response} manquante"

    def test_swagger_user_schema_properties(self):
        """Test propriétés du schéma User."""
        # Assert
        user_schema = SWAGGER_TEMPLATE['components']['schemas']['User']
        assert 'properties' in user_schema
        
        properties = user_schema['properties']
        assert 'id' in properties
        assert 'email' in properties
        assert 'role' in properties
        
        # Vérification des rôles autorisés
        role_enum = properties['role']['enum']
        expected_roles = ['member', 'teacher', 'patron', 'admin', 'relie']
        assert set(role_enum) == set(expected_roles)

    def test_swagger_login_request_validation(self):
        """Test validation du schéma LoginRequest."""
        # Assert
        login_schema = SWAGGER_TEMPLATE['components']['schemas']['LoginRequest']
        assert 'required' in login_schema
        assert set(login_schema['required']) == {'email', 'password'}
        
        properties = login_schema['properties']
        assert properties['email']['format'] == 'email'
        assert properties['password']['format'] == 'password'
