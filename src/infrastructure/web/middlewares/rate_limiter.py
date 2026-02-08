# src/infrastructure/web/middlewares/rate_limiter.py
"""Rate limiting pour protéger contre les attaques par force brute."""

import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Instance globale du limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://"),
)


def init_rate_limiter(app: Flask) -> None:
    """Initialise le rate limiter avec l'application Flask."""
    limiter.init_app(app)


# Décorateurs pré-configurés pour les routes sensibles
def limit_login():
    """Limiteur pour la route /login."""
    return limiter.limit("5 per minute;100 per day")


def limit_register():
    """Limiteur pour la route /register."""
    return limiter.limit("3 per hour")


def limit_refresh():
    """Limiteur pour la route /refresh."""
    return limiter.limit("10 per minute")
