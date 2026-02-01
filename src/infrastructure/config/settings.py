# src/infrastructure/config/settings.py
"""Configuration de l'application avec validation."""

import os
import secrets
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    """
    Configuration de l'application.
    
    Validée au démarrage pour éviter les erreurs de runtime.
    """
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
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Charge la configuration depuis les variables d'environnement."""
        secret_key = os.getenv("SECRET_KEY")
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        
        # Validation critique des clés de sécurité
        if not secret_key:
            if os.getenv("FLASK_ENV") == "production":
                raise ValueError("SECRET_KEY est obligatoire en production")
            secret_key = secrets.token_urlsafe(32)
            print("⚠️  SECRET_KEY générée automatiquement (dev uniquement)")
        
        if not jwt_secret:
            if os.getenv("FLASK_ENV") == "production":
                raise ValueError("JWT_SECRET_KEY est obligatoire en production")
            jwt_secret = secrets.token_urlsafe(32)
            print("⚠️  JWT_SECRET_KEY générée automatiquement (dev uniquement)")
        
        # Validation de la force des clés
        if len(secret_key) < 32:
            raise ValueError("SECRET_KEY doit contenir au moins 32 caractères")
        
        is_production = os.getenv("FLASK_ENV") == "production"
        
        return cls(
            SECRET_KEY=secret_key,
            DEBUG=os.getenv("FLASK_DEBUG", "0") == "1",
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./data/alvs.db"),
            REDIS_URL=os.getenv("REDIS_URL"),
            JWT_SECRET_KEY=jwt_secret,
            JWT_ACCESS_TOKEN_EXPIRES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900")),
            JWT_REFRESH_TOKEN_EXPIRES=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000")),
            JWT_COOKIE_SECURE=is_production,
            CORS_ORIGINS=os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else None,
            RATELIMIT_STORAGE_URL=os.getenv("REDIS_URL"),
            UPLOAD_FOLDER=os.getenv("UPLOAD_FOLDER", "static/uploads"),
            MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024))),
        )
    
    def validate(self) -> None:
        """Valide la configuration au démarrage."""
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY ne peut pas être vide")
        if not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY ne peut pas être vide")


# Instance globale (lazy loading)
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Récupère la configuration (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
        _settings.validate()
    return _settings
