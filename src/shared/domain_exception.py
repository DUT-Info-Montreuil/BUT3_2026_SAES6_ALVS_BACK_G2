# src/shared/domain_exception.py
"""Exceptions du domaine métier."""


class DomainException(Exception):
    """Exception de base pour le domaine métier."""
    pass


class ConfigurationError(DomainException):
    """Erreur de configuration de l'application."""
    pass
