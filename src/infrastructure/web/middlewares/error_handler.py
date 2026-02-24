# src/infrastructure/web/middlewares/error_handler.py
"""Gestion centralisée des erreurs HTTP."""

from flask import Flask, jsonify, current_app
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
    
    @app.errorhandler(NotFoundException)
    def handle_not_found(error: NotFoundException):
        return jsonify({
            'success': False,
            'message': error.message,
            'error': 'Not Found',
            'status': HTTPStatus.NOT_FOUND
        }), HTTPStatus.NOT_FOUND
    
    @app.errorhandler(ForbiddenException)
    def handle_forbidden(error: ForbiddenException):
        return jsonify({
            'success': False,
            'message': error.message,
            'error': 'Forbidden',
            'status': HTTPStatus.FORBIDDEN
        }), HTTPStatus.FORBIDDEN
    
    @app.errorhandler(UnauthorizedException)
    def handle_unauthorized(error: UnauthorizedException):
        return jsonify({
            'success': False,
            'message': error.message,
            'error': 'Unauthorized',
            'status': HTTPStatus.UNAUTHORIZED
        }), HTTPStatus.UNAUTHORIZED
    
    @app.errorhandler(ConflictException)
    def handle_conflict(error: ConflictException):
        return jsonify({
            'success': False,
            'message': error.message,
            'error': 'Conflict',
            'status': HTTPStatus.CONFLICT
        }), HTTPStatus.CONFLICT
    
    @app.errorhandler(ValidationException)
    def handle_validation(error: ValidationException):
        response_data = {
            'success': False,
            'message': error.message,
            'error': 'Validation Error',
            'status': HTTPStatus.BAD_REQUEST
        }
        if hasattr(error, 'errors') and error.errors:
            response_data['errors'] = error.errors
        return jsonify(response_data), HTTPStatus.BAD_REQUEST
    
    @app.errorhandler(DomainException)
    def handle_domain_exception(error: DomainException):
        return jsonify({
            'success': False,
            'message': error.message,
            'error': 'Business Rule Violation',
            'status': HTTPStatus.UNPROCESSABLE_ENTITY
        }), HTTPStatus.UNPROCESSABLE_ENTITY
    
    @app.errorhandler(PersistenceException)
    def handle_persistence(error: PersistenceException):
        app.logger.error(f"Persistence error: {error.message}")
        return jsonify({
            'success': False,
            'message': 'Erreur lors de la sauvegarde des données',
            'error': 'Internal Server Error',
            'status': HTTPStatus.INTERNAL_SERVER_ERROR
        }), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        # Logger l'erreur complète côté serveur (pas au client)
        app.logger.exception("Erreur interne non gérée", exc_info=error)
        
        # Message conditionnel selon la configuration
        if current_app.config.get('EXPOSE_ERROR_DETAILS', False):
            message = f"Erreur serveur: {str(error)}"
        else:
            message = "Erreur interne du serveur"
        
        return jsonify({
            'success': False,
            'message': message,
            'error': 'Internal Server Error',
            'status': HTTPStatus.INTERNAL_SERVER_ERROR
        }), HTTPStatus.INTERNAL_SERVER_ERROR