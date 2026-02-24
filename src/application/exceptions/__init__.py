# src/application/exceptions/__init__.py
"""
Exceptions applicatives pour la gestion d'erreurs HTTP.

Ces exceptions sont mappées vers des codes HTTP dans la couche infrastructure.
"""


class ApplicationException(Exception):
    """Exception de base pour la couche application."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(ApplicationException):
    """Ressource non trouvée (HTTP 404)."""
    pass


class ForbiddenException(ApplicationException):
    """Action interdite pour l'utilisateur (HTTP 403)."""
    pass


class UnauthorizedException(ApplicationException):
    """Authentification requise ou invalide (HTTP 401)."""
    pass


class AuthenticationException(ApplicationException):
    """Échec d'authentification (HTTP 401)."""
    pass


class ConflictException(ApplicationException):
    """Conflit avec l'état actuel de la ressource (HTTP 409)."""
    pass


class ValidationException(ApplicationException):
    """Erreur de validation des données d'entrée (HTTP 400)."""

    def __init__(self, message: str, errors: dict = None):
        super().__init__(message, details={"errors": errors or {}})
        self.errors = errors or {}


class PersistenceException(ApplicationException):
    """Erreur lors de la persistance des données (HTTP 500)."""
    pass
