# src/infrastructure/config/settings.py
"""Configuration de l'application avec validation."""

import os
import secrets
from dataclasses import dataclass
from typing import Optional

from src.shared.domain_exception import ConfigurationError


@dataclass
class Config:
    """Configuration de base."""
    # Flask
    SECRET_KEY: str
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/alvs.db"
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: str = None
    JWT_ACCESS_TOKEN_EXPIRES: int = 900  # 15 min (sécurité renforcée)
    JWT_REFRESH_TOKEN_EXPIRES: int = 2592000  # 30 jours
    
    # JWT Cookies (Refresh Token)
    JWT_TOKEN_LOCATION: list = None  # Configuré dans app.py
    JWT_COOKIE_SECURE: bool = True
    JWT_COOKIE_HTTPONLY: bool = True
    JWT_COOKIE_SAMESITE: str = "Strict"
    JWT_COOKIE_CSRF_PROTECT: bool = True
    
    # CORS
    CORS_ORIGINS: list = None  # ["https://alvs.naraction.org"]
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL: Optional[str] = None  # Redis URL
    RATELIMIT_DEFAULT: str = "200 per day"
    
    # Account Lockout
    LOCKOUT_THRESHOLD: int = 5
    LOCKOUT_DURATION: int = 900  # 15 min
    
    # File Upload
    UPLOAD_FOLDER: str = "static/uploads"
    MAX_CONTENT_LENGTH: int = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS: frozenset = frozenset({'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'm4a', 'pdf'})
    
    def validate(self) -> None:
        """Valide la configuration au démarrage."""
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY ne peut pas être vide")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY ne peut pas être vide")


class DevelopmentConfig(Config):
    """Configuration pour le développement."""
    
    def __init__(self):
        secret_key = os.getenv("SECRET_KEY")
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        
        # Fallbacks pour le développement
        if not secret_key:
            secret_key = secrets.token_urlsafe(32)
            print("[WARN] SECRET_KEY generee automatiquement (dev uniquement)")

        if not jwt_secret:
            jwt_secret = secrets.token_urlsafe(32)
            print("[WARN] JWT_SECRET_KEY generee automatiquement (dev uniquement)")
        
        # Validation de la force des clés
        if len(secret_key) < 32:
            raise ValueError("SECRET_KEY doit contenir au moins 32 caractères")
        
        super().__init__(
            SECRET_KEY=secret_key,
            DEBUG=os.getenv("FLASK_DEBUG", "1") == "1",
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./data/alvs.db"),
            REDIS_URL=os.getenv("REDIS_URL"),
            JWT_SECRET_KEY=jwt_secret,
            JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900")),
            JWT_REFRESH_TOKEN_EXPIRES=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000")),
            JWT_COOKIE_SECURE=False,  # HTTP autorisé en dev
            CORS_ORIGINS=os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else None,
            RATELIMIT_STORAGE_URL=os.getenv("REDIS_URL"),
            UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", "static/uploads"),
            MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024))),
        )


class TestConfig(Config):
    """Configuration pour les tests."""
    
    def __init__(self):
        secret_key = os.getenv("SECRET_KEY")
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        
        # Fallbacks pour les tests
        if not secret_key:
            secret_key = "test-secret-key-32-characters-long"
        
        if not jwt_secret:
            jwt_secret = "test-jwt-secret-key-32-characters"
        
        super().__init__(
            SECRET_KEY=secret_key,
            DEBUG=False,
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///:memory:"),
            REDIS_URL=None,
            JWT_SECRET_KEY=jwt_secret,
            JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900")),
            JWT_REFRESH_TOKEN_EXPIRES=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000")),
            JWT_COOKIE_SECURE=False,  # HTTP autorisé en test
            CORS_ORIGINS=None,
            RATELIMIT_STORAGE_URL=None,
            UPLOAD_FOLDER="test_uploads",
            MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024))),
        )


class ProductionConfig(Config):
    """Configuration pour la production."""
    
    def __init__(self):
        self._validate_required_secrets()
        
        secret_key = os.getenv("SECRET_KEY")
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        
        # Validation de la force des clés
        if len(secret_key) < 32:
            raise ValueError("SECRET_KEY doit contenir au moins 32 caractères")
        
        super().__init__(
            SECRET_KEY=secret_key,
            DEBUG=False,
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./data/alvs.db"),
            REDIS_URL=os.getenv("REDIS_URL"),
            JWT_SECRET_KEY=jwt_secret,
            JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900")),
            JWT_REFRESH_TOKEN_EXPIRES=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000")),
            JWT_COOKIE_SECURE=True,  # HTTPS obligatoire en production
            CORS_ORIGINS=os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else None,
            RATELIMIT_STORAGE_URL=os.getenv("REDIS_URL"),
            UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", "static/uploads"),
            MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024))),
        )
    
    def _validate_required_secrets(self):
        """Valide que les secrets requis sont présents en production."""
        missing_vars = []
        if not os.getenv('SECRET_KEY'):
            missing_vars.append('SECRET_KEY')
        if not os.getenv('JWT_SECRET_KEY'):
            missing_vars.append('JWT_SECRET_KEY')
        
        if missing_vars:
            raise ConfigurationError(
                f"Required environment variables missing in production: {', '.join(missing_vars)}. "
                f"Please set these variables before starting the application."
            )


# Mapping des configurations par environnement
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


# Instance globale (lazy loading)
_settings: Optional[Config] = None


def get_settings() -> Config:
    """Récupère la configuration (singleton pattern)."""
    global _settings
    if _settings is None:
        env = os.getenv('FLASK_ENV', 'development')
        config_class = config_by_name.get(env, DevelopmentConfig)
        _settings = config_class()
        _settings.validate()
    return _settings


def reset_settings() -> None:
    """Réinitialise le singleton de configuration (utile pour les tests)."""
    global _settings
    _settings = None


# Alias pour compatibilité avec l'ancien code
Settings = Config