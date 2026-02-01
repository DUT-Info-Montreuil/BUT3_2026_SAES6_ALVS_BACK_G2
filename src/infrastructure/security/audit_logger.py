# src/infrastructure/security/audit_logger.py
"""Audit logging pour les evenements de securite."""

import logging
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class AuditEvent(Enum):
    """Types d'evenements d'audit."""
    # Auth
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    TOKEN_REFRESH = "token_refresh"
    ACCOUNT_LOCKED = "account_locked"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"
    
    # User
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ROLE_CHANGED = "role_changed"
    
    # Content
    COLLI_CREATED = "colli_created"
    COLLI_APPROVED = "colli_approved"
    COLLI_REJECTED = "colli_rejected"
    LETTER_CREATED = "letter_created"
    COMMENT_CREATED = "comment_created"
    REPORT_CREATED = "report_created"
    
    # Data
    DATA_EXPORTED = "data_exported"
    DATA_DELETION_REQUESTED = "data_deletion_requested"
    
    # Security
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_TOKEN = "invalid_token"


# Configuration du logger d'audit
audit_logger = logging.getLogger("security.audit")
audit_logger.setLevel(logging.INFO)

# Handler console avec format structure
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s | AUDIT | %(levelname)s | %(message)s'
))
audit_logger.addHandler(console_handler)

# Handler fichier (si configure)
log_dir = os.getenv('AUDIT_LOG_DIR', 'logs')
if log_dir:
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(
        os.path.join(log_dir, 'audit.log'),
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    ))
    audit_logger.addHandler(file_handler)


def log_audit_event(
    event: AuditEvent,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    level: str = "info"
) -> None:
    """
    Log un evenement d'audit structure.
    
    Args:
        event: Type d'evenement
        user_id: ID de l'utilisateur concerne
        ip_address: Adresse IP
        details: Details additionnels
        level: Niveau de log (info, warning, error)
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event.value,
        "user_id": user_id or "anonymous",
        "ip_address": ip_address or "unknown",
        "details": details or {}
    }
    
    message = json.dumps(log_data, ensure_ascii=False)
    
    if level == "warning":
        audit_logger.warning(message)
    elif level == "error":
        audit_logger.error(message)
    else:
        audit_logger.info(message)


# Fonctions de convenance (compatibilite avec l'ancien code)
def log_login_success(user_id: str, ip_address: str) -> None:
    """Log une connexion reussie."""
    log_audit_event(AuditEvent.LOGIN_SUCCESS, user_id, ip_address)


def log_login_failure(email: str, ip_address: str, reason: str) -> None:
    """Log un echec de connexion."""
    log_audit_event(
        AuditEvent.LOGIN_FAILURE, 
        None, 
        ip_address, 
        {"email": email, "reason": reason},
        "warning"
    )


def log_logout(user_id: str) -> None:
    """Log une deconnexion."""
    log_audit_event(AuditEvent.LOGOUT, user_id)


def log_token_refresh(user_id: str) -> None:
    """Log un rafraichissement de token."""
    log_audit_event(AuditEvent.TOKEN_REFRESH, user_id)


def log_account_locked(email: str, ip_address: str) -> None:
    """Log un verrouillage de compte."""
    log_audit_event(
        AuditEvent.ACCOUNT_LOCKED,
        None,
        ip_address,
        {"email": email},
        "warning"
    )


def log_suspicious_activity(user_id: Optional[str], ip_address: str, activity: str) -> None:
    """Log une activite suspecte."""
    log_audit_event(
        AuditEvent.SUSPICIOUS_ACTIVITY,
        user_id,
        ip_address,
        {"activity": activity},
        "warning"
    )


def log_data_export(user_id: str, ip_address: str = None) -> None:
    """Log un export de donnees RGPD."""
    log_audit_event(AuditEvent.DATA_EXPORTED, user_id, ip_address)


def log_password_reset_requested(email: str, ip_address: str = None) -> None:
    """Log une demande de reset de mot de passe."""
    log_audit_event(
        AuditEvent.PASSWORD_RESET_REQUESTED,
        None,
        ip_address,
        {"email": email}
    )


def log_role_changed(admin_id: str, target_user_id: str, old_role: str, new_role: str) -> None:
    """Log un changement de role."""
    log_audit_event(
        AuditEvent.ROLE_CHANGED,
        admin_id,
        None,
        {"target_user": target_user_id, "old_role": old_role, "new_role": new_role}
    )
