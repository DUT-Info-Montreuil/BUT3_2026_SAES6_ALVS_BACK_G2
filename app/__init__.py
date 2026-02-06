# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Module principal de l'application Flask ALVS
"""

from flask import Flask
from flask_cors import CORS
from app.extensions import db, jwt
from app.config import Config


def create_app(config_class=Config):
    """Factory pattern pour créer l'application Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialisation des extensions
    db.init_app(app)
    jwt.init_app(app)  # Initialize JWTManager with the app
    CORS(app)
    
    # Enregistrement des blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.polls import polls_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(polls_bp, url_prefix='/api/polls')
    
    # Création des tables
    with app.app_context():
        db.create_all()
    
    return app
