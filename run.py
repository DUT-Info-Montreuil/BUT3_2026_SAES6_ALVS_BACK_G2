# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Point d'entrée de l'application Flask ALVS
"""

from app import create_app
from app.config import DevelopmentConfig
from flask_jwt_extended import JWTManager

# Créer l'application
app = create_app(DevelopmentConfig)

# Initialiser JWT
jwt = JWTManager(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
