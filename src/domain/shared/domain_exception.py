# src/domain/shared/domain_exception.py
"""Exceptions de base du domaine."""


class DomainException(Exception):
    """
    Exception de base pour toutes les règles métier violées.

    Les exceptions du domaine représentent des violations des invariants
    métier qui doivent être gérées par la couche application.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class EntityNotFoundException(DomainException):
    """Exception levée quand une entité n'est pas trouvée."""
    pass


class InvalidOperationException(DomainException):
    """Exception levée quand une opération n'est pas permise."""
    pass


class ValidationException(DomainException):
    """Exception levée quand une validation échoue."""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message)
