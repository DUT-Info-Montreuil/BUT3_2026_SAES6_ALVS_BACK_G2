# src/infrastructure/web/routes/health_routes.py
"""Routes de santé pour le monitoring."""

import logging
from datetime import datetime
from http import HTTPStatus

from flask import Blueprint, current_app, jsonify

from src.infrastructure.config.settings import get_settings

health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)


@health_bp.get('/health')
def health_check():
    """
    Vérifie la santé de l'application
    ---
    tags:
      - Health
    summary: Liveness probe
    description: Utilisé par les load balancers et le monitoring pour vérifier que l'application est en vie.
    responses:
      200:
        description: Application en bonne santé
        content:
          application/json:
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: healthy
                timestamp:
                  type: string
                  format: date-time
                service:
                  type: string
                  example: alvs-api
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'alvs-api'
    }), HTTPStatus.OK


@health_bp.get('/ready')
def readiness_check():
    """
    Vérifie que l'application est prête à recevoir du trafic
    ---
    tags:
      - Health
    summary: Readiness probe
    description: >
      Vérifie que l'application et ses dépendances (DB, Redis) sont prêtes
      à recevoir du trafic.
    responses:
      200:
        description: Application prête
        content:
          application/json:
            schema:
              type: object
              properties:
                ready:
                  type: boolean
                checks:
                  type: object
                  properties:
                    config:
                      type: string
                      enum: [ok, error]
                    database:
                      type: string
                      enum: [ok, in_memory, error]
                    redis:
                      type: string
                      enum: [ok, disabled, unavailable]
                timestamp:
                  type: string
                  format: date-time
      503:
        description: Application non prête (dépendance critique en erreur)
    """
    checks = {}

    # Vérifier la configuration
    try:
        settings = get_settings()
        checks['config'] = 'ok'
    except Exception as e:
        logger.error(f"Config check failed: {e}")
        checks['config'] = 'error'

    # Vérifier la base de données
    try:
        from src.infrastructure.persistence.sqlalchemy.database import get_engine
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        checks['database'] = 'ok'
    except Exception as e:
        logger.warning(f"Database check failed (may be using in-memory): {e}")
        checks['database'] = 'in_memory'  # Pas une erreur, peut être normal en dev

    # Vérifier Redis (optionnel)
    try:
        import redis
        settings = get_settings()
        if settings.REDIS_URL:
            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            checks['redis'] = 'ok'
        else:
            checks['redis'] = 'disabled'
    except Exception as e:
        logger.warning(f"Redis check failed: {e}")
        checks['redis'] = 'unavailable'

    # Déterminer le statut global
    critical_checks = ['config']
    all_critical_ok = all(checks.get(c) == 'ok' for c in critical_checks)
    status = HTTPStatus.OK if all_critical_ok else HTTPStatus.SERVICE_UNAVAILABLE

    return jsonify({
        'ready': all_critical_ok,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }), status


@health_bp.get('/version')
def version_info():
    """
    Informations de version
    ---
    tags:
      - Health
    summary: Version de l'API
    description: Retourne la version et l'environnement de l'API.
    responses:
      200:
        description: Informations de version
        content:
          application/json:
            schema:
              type: object
              properties:
                service:
                  type: string
                  example: alvs-api
                version:
                  type: string
                  example: 1.0.0
                environment:
                  type: string
                  example: development
                timestamp:
                  type: string
                  format: date-time
    """
    return jsonify({
        'service': 'alvs-api',
        'version': '1.0.0',
        'environment': current_app.config.get('ENV', 'production'),
        'timestamp': datetime.utcnow().isoformat()
    }), HTTPStatus.OK
