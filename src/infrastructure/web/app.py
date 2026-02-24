# src/infrastructure/web/app.py
"""Factory Flask pour l'application ALVS."""

import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
import redis

from src.infrastructure.config.settings import get_settings
from src.infrastructure.security.jwt_service import init_jwt, jwt
from src.infrastructure.web.middlewares.error_handler import register_error_handlers
from src.infrastructure.web.middlewares.rate_limiter import init_rate_limiter


# Configuration Swagger/OpenAPI
SWAGGER_TEMPLATE = {
    "openapi": "3.0.3",
    "info": {
        "title": "ALVS API",
        "version": "1.0.0",
        "description": "API de correspondances littéraires internationales - NarAction",
        "contact": {
            "name": "Équipe ALVS",
            "email": "contact@naraction.org"
        }
    },
    "servers": [
        {"url": "http://localhost:5000", "description": "Développement"}
        # Production sera ajouté après déploiement
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Token JWT obtenu via /auth/login"
            }
        },
        "schemas": {
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                    "message": {"type": "string"},
                    "details": {"type": "object"}
                }
            },
            "LoginRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "format": "email", "example": "user@example.com"},
                    "password": {"type": "string", "format": "password", "example": "password123"}
                }
            },
            "LoginResponse": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string"},
                    "token_type": {"type": "string", "example": "Bearer"},
                    "user": {"$ref": "#/components/schemas/User"}
                }
            },
            "RegisterRequest": {
                "type": "object",
                "required": ["email", "password", "password_confirm", "first_name", "last_name"],
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string", "minLength": 8},
                    "password_confirm": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"}
                }
            },
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "role": {"type": "string", "enum": ["member", "teacher", "patron", "admin", "relie"]}
                }
            },
            "Colli": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "theme": {"type": "string"},
                    "description": {"type": "string"},
                    "status": {"type": "string", "enum": ["pending", "active", "rejected", "completed"]},
                    "creator_id": {"type": "string", "format": "uuid"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "Letter": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "colli_id": {"type": "string", "format": "uuid"},
                    "sender_id": {"type": "string", "format": "uuid"},
                    "letter_type": {"type": "string", "enum": ["text", "file"]},
                    "content": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            },
            "Comment": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "letter_id": {"type": "string", "format": "uuid"},
                    "author_id": {"type": "string", "format": "uuid"},
                    "content": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"}
                }
            }
        },
        "responses": {
            "NotFound": {
                "description": "Ressource non trouvée",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            },
            "Unauthorized": {
                "description": "Token manquant ou invalide",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            },
            "Forbidden": {
                "description": "Permissions insuffisantes",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            },
            "RateLimited": {
                "description": "Trop de requêtes (429)",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            },
            "ValidationError": {
                "description": "Erreur de validation des données",
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}
            }
        }
    },
    "tags": [
        {"name": "Authentication", "description": "Gestion de l'authentification"},
        {"name": "COLLI", "description": "Gestion des communautes litteraires"},
        {"name": "Letters", "description": "Gestion des correspondances"},
        {"name": "Comments", "description": "Gestion des commentaires"},
        {"name": "Files", "description": "Gestion des fichiers"},
        {"name": "Notifications", "description": "Notifications utilisateur"},
        {"name": "Search", "description": "Recherche globale"},
        {"name": "Invitations", "description": "Invitations COLLI"},
        {"name": "Reports", "description": "Signalements de contenu"},
        {"name": "Export", "description": "Export donnees RGPD"},
        {"name": "Admin", "description": "Administration (admin uniquement)"},
        {"name": "Health", "description": "Statut de l'API"}
    ]
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [{
        "endpoint": "apispec",
        "route": "/apispec.json",
        "rule_filter": lambda rule: True,
        "model_filter": lambda tag: True,
    }],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs",
    "openapi": "3.0.3"  # Force OpenAPI 3.0 only
}


# Redis client pour la blocklist
_redis_client = None


def get_redis_client():
    """Récupère le client Redis."""
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            _redis_client = redis.from_url(redis_url)
    return _redis_client


def create_app(config_override: dict = None) -> Flask:
    """
    Factory pour créer l'application Flask.
    
    Args:
        config_override: Configuration de test optionnelle.
        
    Returns:
        Flask: L'application configurée.
    """
    app = Flask(__name__)
    
    # Charger la configuration
    settings = get_settings()
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH
    
    # Configuration JWT
    app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = settings.JWT_ACCESS_TOKEN_EXPIRES
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = settings.JWT_REFRESH_TOKEN_EXPIRES
    
    # JWT Cookies (Refresh Token en cookie HttpOnly)
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
    app.config['JWT_COOKIE_SECURE'] = settings.JWT_COOKIE_SECURE
    app.config['JWT_COOKIE_HTTPONLY'] = settings.JWT_COOKIE_HTTPONLY
    app.config['JWT_COOKIE_SAMESITE'] = settings.JWT_COOKIE_SAMESITE
    app.config['JWT_COOKIE_CSRF_PROTECT'] = settings.JWT_COOKIE_CSRF_PROTECT
    
    # Override pour les tests
    if config_override:
        app.config.update(config_override)
    
    # Configuration CORS avec origines restreintes
    cors_origin = os.getenv('CORS_ORIGIN', 'http://localhost:5173')
    cors_origins = [origin.strip() for origin in cors_origin.split(',')]
    
    # Initialiser les extensions
    CORS(app, origins=cors_origins)
    init_jwt(app)
    init_rate_limiter(app)
    
    # Initialiser Swagger (documentation API)
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)
    
    # Configurer la blocklist JWT (révocation de tokens)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        redis_client = get_redis_client()
        if redis_client:
            return redis_client.exists(f"revoked:{jti}")
        return False
    
    # Initialiser le container d'injection de dépendances
    from src.infrastructure.container import init_container
    init_container(app)
    
    # Enregistrer les middlewares
    register_error_handlers(app)
    
    # Enregistrer les blueprints
    _register_blueprints(app)
    
    return app


def _register_blueprints(app: Flask) -> None:
    """Enregistre tous les blueprints."""
    from src.infrastructure.web.routes.auth_routes import auth_bp
    from src.infrastructure.web.routes.colli_routes import colli_bp
    from src.infrastructure.web.routes.health_routes import health_bp
    from src.infrastructure.web.routes.letter_routes import letter_bp
    from src.infrastructure.web.routes.comment_routes import comment_bp
    from src.infrastructure.web.routes.file_routes import file_bp
    from src.infrastructure.web.routes.admin_routes import admin_bp
    from src.infrastructure.web.routes.notification_routes import notification_bp
    from src.infrastructure.web.routes.search_routes import search_bp
    from src.infrastructure.web.routes.invitation_routes import invitation_bp
    from src.infrastructure.web.routes.report_routes import report_bp
    from src.infrastructure.web.routes.export_routes import export_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(colli_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(letter_bp)
    app.register_blueprint(comment_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(invitation_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(export_bp)


# Point d'entree pour le developpement
if __name__ == '__main__':
    app = create_app()
    
    # Initialiser SocketIO pour les notifications temps reel
    from src.infrastructure.websocket import init_socketio
    socketio = init_socketio(app)
    
    # Lancer avec SocketIO (supporte WebSocket)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)