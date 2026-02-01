# src/infrastructure/security/audit_logger.py
"""Audit logging pour les événements de sécurité."""

import logging
from datetime import datetime
from typing import Optional


# Configuration du logger d'audit
audit_logger = logging.getLogger("security.audit")
audit_logger.setLevel(logging.INFO)

# Handler console avec format structuré
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s | AUDIT | %(levelname)s | %(message)s'
))
audit_logger.addHandler(handler)


def log_login_success(user_id: str, ip_address: str) -> None:
    """Log une connexion réussie."""
    audit_logger.info(f"LOGIN_SUCCESS user={user_id} ip={ip_address}")


def log_login_failure(email: str, ip_address: str, reason: str) -> None:
    """Log un échec de connexion."""
    audit_logger.warning(f"LOGIN_FAILURE email={email} ip={ip_address} reason={reason}")


def log_logout(user_id: str) -> None:
    """Log une déconnexion."""
    audit_logger.info(f"LOGOUT user={user_id}")


def log_token_refresh(user_id: str) -> None:
    """Log un rafraîchissement de token."""
    audit_logger.debug(f"TOKEN_REFRESH user={user_id}")


def log_account_locked(email: str, ip_address: str) -> None:
    """Log un verrouillage de compte."""
    audit_logger.warning(f"ACCOUNT_LOCKED email={email} ip={ip_address}")


def log_suspicious_activity(user_id: Optional[str], ip_address: str, activity: str) -> None:
    """Log une activité suspecte."""
    audit_logger.warning(f"SUSPICIOUS_ACTIVITY user={user_id or 'anonymous'} ip={ip_address} activity={activity}")
