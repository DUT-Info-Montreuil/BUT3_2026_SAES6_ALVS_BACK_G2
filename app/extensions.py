# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Extensions Flask pour éviter les imports circulaires
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Instance SQLAlchemy globale
db = SQLAlchemy()

# Instance JWTManager globale
jwt = JWTManager()
