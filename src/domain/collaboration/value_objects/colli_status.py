# src/domain/collaboration/value_objects/colli_status.py
"""Value Object pour le statut d'un COLLI."""

from enum import Enum


class ColliStatus(Enum):
    """
    Statuts possibles d'un COLLI.
    
    Workflow: PENDING → ACTIVE ou REJECTED
              ACTIVE → COMPLETED
    """
    PENDING = "pending"       # En attente d'approbation
    ACTIVE = "active"         # Approuvé et actif
    REJECTED = "rejected"     # Rejeté par l'admin
    COMPLETED = "completed"   # Terminé (fin de cycle)
    
    def can_transition_to(self, target: "ColliStatus") -> bool:
        """Vérifie si la transition vers un autre statut est valide."""
        allowed_transitions = {
            ColliStatus.PENDING: [ColliStatus.ACTIVE, ColliStatus.REJECTED],
            ColliStatus.ACTIVE: [ColliStatus.COMPLETED],
            ColliStatus.REJECTED: [],
            ColliStatus.COMPLETED: [],
        }
        return target in allowed_transitions.get(self, [])
