# src/infrastructure/security/account_lockout.py
"""Gestion du verrouillage des comptes après échecs de connexion."""

from typing import Optional
import redis
import os


class AccountLockoutService:
    """
    Service de verrouillage de compte.
    
    Bloque un compte après un nombre défini d'échecs de connexion.
    Utilise Redis pour stocker les compteurs d'échecs.
    """
    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        threshold: int = 5,
        lockout_duration: int = 900  # 15 min
    ):
        self._redis = redis_client
        self._threshold = threshold
        self._lockout_duration = lockout_duration
        
        # Fallback en mémoire si Redis n'est pas disponible
        self._memory_store: dict = {}
    
    def _get_key(self, email: str) -> str:
        return f"lockout:{email.lower()}"
    
    def is_locked(self, email: str) -> bool:
        """Vérifie si un compte est verrouillé."""
        key = self._get_key(email)
        
        if self._redis:
            attempts = self._redis.get(key)
            return int(attempts or 0) >= self._threshold
        else:
            return self._memory_store.get(key, 0) >= self._threshold
    
    def increment_failure(self, email: str) -> int:
        """
        Incrémente le compteur d'échecs.
        
        Returns:
            int: Nombre d'échecs actuel
        """
        key = self._get_key(email)
        
        if self._redis:
            pipe = self._redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self._lockout_duration)
            results = pipe.execute()
            return results[0]
        else:
            current = self._memory_store.get(key, 0) + 1
            self._memory_store[key] = current
            return current
    
    def clear_lockout(self, email: str) -> None:
        """Réinitialise le compteur d'échecs après une connexion réussie."""
        key = self._get_key(email)
        
        if self._redis:
            self._redis.delete(key)
        else:
            self._memory_store.pop(key, None)
    
    def get_remaining_attempts(self, email: str) -> int:
        """Retourne le nombre de tentatives restantes."""
        key = self._get_key(email)
        
        if self._redis:
            attempts = int(self._redis.get(key) or 0)
        else:
            attempts = self._memory_store.get(key, 0)
        
        return max(0, self._threshold - attempts)


# Instance globale (initialisée dans app.py)
_lockout_service: Optional[AccountLockoutService] = None


def get_lockout_service() -> AccountLockoutService:
    """Récupère le service de verrouillage."""
    global _lockout_service
    if _lockout_service is None:
        redis_url = os.getenv("REDIS_URL")
        redis_client = redis.from_url(redis_url) if redis_url else None
        _lockout_service = AccountLockoutService(redis_client=redis_client)
    return _lockout_service
