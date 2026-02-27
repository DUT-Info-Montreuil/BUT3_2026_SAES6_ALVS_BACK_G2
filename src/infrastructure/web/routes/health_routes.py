# src/infrastructure/web/routes/health_routes.py
"""Routes de santé pour le monitoring."""

from flask import Blueprint, jsonify, current_app
from http import HTTPStatus
from datetime import datetime
import logging

from src.infrastructure.config.settings import get_settings


health_bp = Blueprint('health', __name__)
logger = logging.getLogger(__name__)


@health_bp.get('/health')
def health_check():
    """
    Vérifie la santé de l'application.
    
    Utilisé par les load balancers et le monitoring.
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'alvs-api'
    }), HTTPStatus.OK


@health_bp.get('/ready')
def readiness_check():
    """
    Vérifie que l'application est prête à recevoir du trafic.
    
    Inclut la vérification des dépendances (DB, Redis, etc.).
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
    """Retourne les informations de version."""
    return jsonify({
        'service': 'alvs-api',
        'version': '1.0.0',
        'environment': current_app.config.get('ENV', 'production'),
        'timestamp': datetime.utcnow().isoformat()
    }), HTTPStatus.OK
