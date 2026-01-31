# src/infrastructure/web/app.py
"""Factory Flask pour l'application ALVS."""

from flask import Flask
from flask_cors import CORS

from src.infrastructure.config.settings import get_settings
from src.infrastructure.security.jwt_service import init_jwt
from src.infrastructure.web.middlewares.error_handler import register_error_handlers


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
    
    # Override pour les tests
    if config_override:
        app.config.update(config_override)
    
    # Initialiser les extensions
    CORS(app)
    init_jwt(app)
    
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
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(colli_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(letter_bp)
    app.register_blueprint(comment_bp)


# Point d'entrée pour le développement
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
