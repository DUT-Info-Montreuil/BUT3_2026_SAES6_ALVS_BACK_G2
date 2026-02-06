# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Tests pour l'application Flask principale
"""

import pytest
from app import create_app
from app.extensions import db
from config import Config, TestConfig


class TestAppFactory:
    """Tests pour la factory de création d'application"""
    
    def test_create_app_with_default_config(self):
        """Test la création d'app avec la config par défaut"""
        app = create_app()
        assert app is not None
        assert app.config['SECRET_KEY'] is not None
    
    def test_create_app_with_test_config(self):
        """Test la création d'app avec la config de test"""
        app = create_app(TestConfig)
        assert app is not None
        assert app.config['TESTING'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    
    def test_app_has_db_extension(self):
        """Test que l'application a bien l'extension de base de données"""
        app = create_app(TestConfig)
        with app.app_context():
            assert db is not None
            # Test que la base de données est bien initialisée
            db.create_all()
            db.drop_all()


class TestAppConfiguration:
    """Tests pour la configuration de l'application"""
    
    def test_config_classes_exist(self):
        """Test que les classes de configuration existent"""
        assert Config is not None
        assert TestConfig is not None
    
    def test_test_config_inherits_from_config(self):
        """Test que TestConfig hérite bien de Config"""
        assert issubclass(TestConfig, Config)
    
    def test_test_config_has_correct_values(self):
        """Test que TestConfig a les bonnes valeurs"""
        config = TestConfig()
        assert config.TESTING is True
        assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
        assert config.SQLALCHEMY_TRACK_MODIFICATIONS is False


class TestAppIntegration:
    """Tests d'intégration de l'application"""
    
    def test_app_starts_successfully(self, app):
        """Test que l'application démarre avec succès"""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_app_context_works(self, app):
        """Test que le contexte d'application fonctionne"""
        with app.app_context():
            # Test qu'on peut accéder à la base de données
            assert db is not None
    
    def test_client_can_be_created(self, client):
        """Test qu'un client de test peut être créé"""
        assert client is not None
        # Test une requête basique (même si aucune route n'est définie)
        response = client.get('/')
        # On s'attend à une 404 car aucune route n'est définie
        assert response.status_code == 404
