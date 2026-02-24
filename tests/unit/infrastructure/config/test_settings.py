# tests/unit/infrastructure/config/test_settings.py
"""Tests pour la configuration de l'application."""

import os
import pytest
from unittest.mock import patch, MagicMock

from src.infrastructure.config.settings import (
    Config, DevelopmentConfig, TestConfig as SettingsTestConfig, ProductionConfig
)
from src.shared.domain_exception import ConfigurationError


class TestConfig:
    """Tests pour la classe Config de base."""
    
    def test_config_creation_with_required_fields(self):
        """Test la création d'une Config avec les champs requis."""
        config = Config(
            SECRET_KEY="test-secret-key-32-characters-long",
            JWT_SECRET_KEY="test-jwt-secret-key-32-characters"
        )
        
        assert config.SECRET_KEY == "test-secret-key-32-characters-long"
        assert config.JWT_SECRET_KEY == "test-jwt-secret-key-32-characters"
        assert config.DEBUG is False
        assert config.DATABASE_URL == "sqlite:///./data/alvs.db"
        assert config.JWT_ACCESS_TOKEN_EXPIRES == 900
        assert config.JWT_REFRESH_TOKEN_EXPIRES == 2592000
    
    def test_config_validate_success(self):
        """Test la validation réussie d'une Config."""
        config = Config(
            SECRET_KEY="test-secret-key-32-characters-long",
            JWT_SECRET_KEY="test-jwt-secret-key-32-characters"
        )
        
        # Ne doit pas lever d'exception
        config.validate()
    
    def test_config_validate_empty_secret_key(self):
        """Test la validation avec SECRET_KEY vide."""
        config = Config(
            SECRET_KEY="",
            JWT_SECRET_KEY="test-jwt-secret-key-32-characters"
        )
        
        with pytest.raises(ValueError, match="SECRET_KEY ne peut pas être vide"):
            config.validate()
    
    def test_config_validate_none_secret_key(self):
        """Test la validation avec SECRET_KEY None."""
        config = Config(
            SECRET_KEY=None,
            JWT_SECRET_KEY="test-jwt-secret-key-32-characters"
        )
        
        with pytest.raises(ValueError, match="SECRET_KEY ne peut pas être vide"):
            config.validate()
    
    def test_config_validate_empty_jwt_secret_key(self):
        """Test la validation avec JWT_SECRET_KEY vide."""
        config = Config(
            SECRET_KEY="test-secret-key-32-characters-long",
            JWT_SECRET_KEY=""
        )
        
        with pytest.raises(ValueError, match="JWT_SECRET_KEY ne peut pas être vide"):
            config.validate()
    
    def test_config_validate_none_jwt_secret_key(self):
        """Test la validation avec JWT_SECRET_KEY None."""
        config = Config(
            SECRET_KEY="test-secret-key-32-characters-long",
            JWT_SECRET_KEY=None
        )
        
        with pytest.raises(ValueError, match="JWT_SECRET_KEY ne peut pas être vide"):
            config.validate()
    
    def test_config_default_values(self):
        """Test les valeurs par défaut de Config."""
        config = Config(
            SECRET_KEY="test-secret",
            JWT_SECRET_KEY="test-jwt"
        )
        
        assert config.DEBUG is False
        assert config.DATABASE_URL == "sqlite:///./data/alvs.db"
        assert config.REDIS_URL is None
        assert config.JWT_ACCESS_TOKEN_EXPIRES == 900
        assert config.JWT_REFRESH_TOKEN_EXPIRES == 2592000
        assert config.JWT_COOKIE_SECURE is True
        assert config.JWT_COOKIE_HTTPONLY is True
        assert config.JWT_COOKIE_SAMESITE == "Strict"
        assert config.JWT_COOKIE_CSRF_PROTECT is True
        assert config.LOCKOUT_THRESHOLD == 5
        assert config.LOCKOUT_DURATION == 900
        assert config.UPLOAD_FOLDER == "static/uploads"
        assert config.MAX_CONTENT_LENGTH == 16 * 1024 * 1024
        assert "png" in config.ALLOWED_EXTENSIONS
        assert "pdf" in config.ALLOWED_EXTENSIONS


class TestDevelopmentConfig:
    """Tests pour DevelopmentConfig."""
    
    @patch.dict(os.environ, {
        "SECRET_KEY": "dev-secret-key-32-characters-long",
        "JWT_SECRET_KEY": "dev-jwt-secret-key-32-characters"
    })
    def test_development_config_with_env_vars(self):
        """Test DevelopmentConfig avec variables d'environnement."""
        config = DevelopmentConfig()
        
        assert config.SECRET_KEY == "dev-secret-key-32-characters-long"
        assert config.JWT_SECRET_KEY == "dev-jwt-secret-key-32-characters"
        assert config.DEBUG is True  # Par défaut en dev
        assert config.JWT_COOKIE_SECURE is False  # HTTP autorisé en dev
    
    @patch.dict(os.environ, {}, clear=True)
    @patch('src.infrastructure.config.settings.secrets.token_urlsafe')
    def test_development_config_without_env_vars(self, mock_token):
        """Test DevelopmentConfig sans variables d'environnement (fallback)."""
        mock_token.return_value = "generated-secret-32-characters-long"
        
        with patch('src.infrastructure.config.settings.logger') as mock_logger:
            config = DevelopmentConfig()

        assert config.SECRET_KEY == "generated-secret-32-characters-long"
        assert config.JWT_SECRET_KEY == "generated-secret-32-characters-long"

        # Vérifier les messages d'avertissement
        mock_logger.warning.assert_any_call("SECRET_KEY generee automatiquement (dev uniquement)")
        mock_logger.warning.assert_any_call("JWT_SECRET_KEY generee automatiquement (dev uniquement)")
    
    @patch.dict(os.environ, {"SECRET_KEY": "short"}, clear=True)
    def test_development_config_short_secret_key(self):
        """Test DevelopmentConfig avec SECRET_KEY trop courte."""
        with pytest.raises(ValueError, match="SECRET_KEY doit contenir au moins 32 caractères"):
            DevelopmentConfig()
    
    @patch.dict(os.environ, {
        "FLASK_DEBUG": "0",
        "DATABASE_URL": "postgresql://test",
        "REDIS_URL": "redis://localhost",
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:8080"
    })
    @patch('src.infrastructure.config.settings.secrets.token_urlsafe')
    def test_development_config_custom_env_vars(self, mock_token):
        """Test DevelopmentConfig avec variables personnalisées."""
        mock_token.return_value = "generated-secret-32-characters-long"
        
        config = DevelopmentConfig()
        
        assert config.DEBUG is False
        assert config.DATABASE_URL == "postgresql://test"
        assert config.REDIS_URL == "redis://localhost"
        assert config.CORS_ORIGINS == ["http://localhost:3000", "http://localhost:8080"]


class TestTestConfig:
    """Tests pour TestConfig."""
    
    @patch.dict(os.environ, {
        "SECRET_KEY": "test-secret-key-32-characters-long",
        "JWT_SECRET_KEY": "test-jwt-secret-key-32-characters"
    })
    def test_test_config_with_env_vars(self):
        """Test TestConfig avec variables d'environnement."""
        config = SettingsTestConfig()
        
        assert config.SECRET_KEY == "test-secret-key-32-characters-long"
        assert config.JWT_SECRET_KEY == "test-jwt-secret-key-32-characters"
        assert config.DEBUG is False
        assert config.DATABASE_URL == "sqlite:///:memory:"
        assert config.JWT_COOKIE_SECURE is False
        assert config.UPLOAD_FOLDER == "test_uploads"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_test_config_without_env_vars(self):
        """Test TestConfig sans variables d'environnement (fallback)."""
        config = SettingsTestConfig()
        
        assert config.SECRET_KEY == "test-secret-key-32-characters-long"
        assert config.JWT_SECRET_KEY == "test-jwt-secret-key-32-characters"
        assert config.DATABASE_URL == "sqlite:///:memory:"
        assert config.REDIS_URL is None
        assert config.CORS_ORIGINS is None


class TestProductionConfig:
    """Tests pour ProductionConfig."""
    
    @patch.dict(os.environ, {
        "SECRET_KEY": "prod-secret-key-32-characters-long",
        "JWT_SECRET_KEY": "prod-jwt-secret-key-32-characters"
    })
    def test_production_config_with_valid_env_vars(self):
        """Test ProductionConfig avec variables d'environnement valides."""
        config = ProductionConfig()
        
        assert config.SECRET_KEY == "prod-secret-key-32-characters-long"
        assert config.JWT_SECRET_KEY == "prod-jwt-secret-key-32-characters"
        assert config.DEBUG is False
        assert config.JWT_COOKIE_SECURE is True  # HTTPS obligatoire
    
    @patch.dict(os.environ, {}, clear=True)
    def test_production_config_missing_secret_key(self):
        """Test ProductionConfig sans SECRET_KEY."""
        with pytest.raises(ConfigurationError):
            ProductionConfig()
    
    @patch.dict(os.environ, {"SECRET_KEY": "prod-secret-key-32-characters-long"}, clear=True)
    def test_production_config_missing_jwt_secret_key(self):
        """Test ProductionConfig sans JWT_SECRET_KEY."""
        with pytest.raises(ConfigurationError):
            ProductionConfig()
    
    @patch.dict(os.environ, {
        "SECRET_KEY": "short",
        "JWT_SECRET_KEY": "prod-jwt-secret-key-32-characters"
    })
    def test_production_config_short_secret_key(self):
        """Test ProductionConfig avec SECRET_KEY trop courte."""
        with pytest.raises(ValueError, match="SECRET_KEY doit contenir au moins 32 caractères"):
            ProductionConfig()
    
    @patch.dict(os.environ, {
        "SECRET_KEY": "prod-secret-key-32-characters-long",
        "JWT_SECRET_KEY": "prod-jwt-secret-key-32-characters",
        "DATABASE_URL": "postgresql://prod",
        "REDIS_URL": "redis://prod",
        "CORS_ORIGINS": "https://alvs.naraction.org"
    })
    def test_production_config_custom_env_vars(self):
        """Test ProductionConfig avec variables personnalisées."""
        config = ProductionConfig()
        
        assert config.DATABASE_URL == "postgresql://prod"
        assert config.REDIS_URL == "redis://prod"
        assert config.CORS_ORIGINS == ["https://alvs.naraction.org"]
        assert config.RATELIMIT_STORAGE_URL == "redis://prod"
    
    @patch.dict(os.environ, {
        "SECRET_KEY": "prod-secret-key-32-characters-long",
        "JWT_SECRET_KEY": "prod-jwt-secret-key-32-characters",
        "JWT_ACCESS_TOKEN_EXPIRES": "1800",
        "JWT_REFRESH_TOKEN_EXPIRES": "604800"
    })
    def test_production_config_custom_jwt_expires(self):
        """Test ProductionConfig avec durées JWT personnalisées."""
        config = ProductionConfig()
        
        assert config.JWT_ACCESS_TOKEN_EXPIRES == 1800  # 30 min
        assert config.JWT_REFRESH_TOKEN_EXPIRES == 604800  # 7 jours