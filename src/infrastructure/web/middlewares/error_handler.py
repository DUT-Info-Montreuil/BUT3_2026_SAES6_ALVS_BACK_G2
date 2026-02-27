# src/infrastructure/web/middlewares/error_handler.py
"""Gestion centralisée des erreurs HTTP."""

from flask import Flask, jsonify
from http import HTTPStatus

from src.application.exceptions import (
    ApplicationException,
    NotFoundException,
    ForbiddenException,
    UnauthorizedException,
    ConflictException,
    ValidationException,
    PersistenceException
)
from src.domain.shared.domain_exception import DomainException


def register_error_handlers(app: Flask) -> None:
    """Enregistre les handlers d'erreurs globaux."""

    @app.errorhandler(429)
    def handle_rate_limit(error):
        return jsonify({
            'error': 'Too Many Requests',
            'message': 'Trop de requêtes. Réessayez plus tard.',
            'status': 429
        }), 429

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'La ressource demandée est introuvable',
            'status': 404
        }), 404

    @app.errorhandler(NotFoundException)
    def handle_not_found(error: NotFoundException):
        return jsonify({
            'error': 'Not Found',
            'message': error.message,
            'status': HTTPStatus.NOT_FOUND
        }), HTTPStatus.NOT_FOUND
    
    @app.errorhandler(ForbiddenException)
    def handle_forbidden(error: ForbiddenException):
        return jsonify({
            'error': 'Forbidden',
            'message': error.message,
            'status': HTTPStatus.FORBIDDEN
        }), HTTPStatus.FORBIDDEN
    
    @app.errorhandler(UnauthorizedException)
    def handle_unauthorized(error: UnauthorizedException):
        return jsonify({
            'error': 'Unauthorized',
            'message': error.message,
            'status': HTTPStatus.UNAUTHORIZED
        }), HTTPStatus.UNAUTHORIZED
    
    @app.errorhandler(ConflictException)
    def handle_conflict(error: ConflictException):
        return jsonify({
            'error': 'Conflict',
            'message': error.message,
            'status': HTTPStatus.CONFLICT
        }), HTTPStatus.CONFLICT
    
    @app.errorhandler(ValidationException)
    def handle_validation(error: ValidationException):
        return jsonify({
            'error': 'Validation Error',
            'message': error.message,
            'errors': error.errors,
            'status': HTTPStatus.BAD_REQUEST
        }), HTTPStatus.BAD_REQUEST
    
    @app.errorhandler(DomainException)
    def handle_domain_exception(error: DomainException):
        return jsonify({
            'error': 'Business Rule Violation',
            'message': error.message,
            'status': HTTPStatus.UNPROCESSABLE_ENTITY
        }), HTTPStatus.UNPROCESSABLE_ENTITY
    
    @app.errorhandler(PersistenceException)
    def handle_persistence(error: PersistenceException):
        app.logger.error(f"Persistence error: {error.message}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Erreur lors de la sauvegarde des données',
            'status': HTTPStatus.INTERNAL_SERVER_ERROR
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        # Logger l'erreur complète côté serveur (pas au client)
        app.logger.exception("Unhandled exception")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Une erreur inattendue est survenue',
            'status': HTTPStatus.INTERNAL_SERVER_ERROR
        }), HTTPStatus.INTERNAL_SERVER_ERROR
