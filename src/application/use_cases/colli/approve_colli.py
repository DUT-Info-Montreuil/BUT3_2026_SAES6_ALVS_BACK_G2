# src/application/use_cases/colli/approve_colli.py
"""Use Case: Approuver un COLLI."""

from dataclasses import dataclass
from uuid import UUID

from src.domain.collaboration.repositories.colli_repository import IColliRepository
from src.application.interfaces.event_publisher import IEventPublisher
from src.application.exceptions import NotFoundException
from src.application.dtos.colli_dto import ColliResponseDTO


@dataclass
class ApproveColliCommand:
    """Commande pour approuver un COLLI."""
    colli_id: UUID
    approver_id: UUID  # Admin qui approuve


class ApproveColliUseCase:
    """
    Use Case: Approuver un COLLI.
    
    Règles métier:
    - Seul un admin peut approuver
    - Le COLLI doit être en statut PENDING
    - L'approbation crée automatiquement le créateur comme manager
    """
    
    def __init__(
        self,
        colli_repository: IColliRepository,
        event_publisher: IEventPublisher
    ):
        self._colli_repo = colli_repository
        self._event_publisher = event_publisher
    
    def execute(self, command: ApproveColliCommand) -> ColliResponseDTO:
        """
        Exécute l'approbation du COLLI.
        
        Args:
            command: Commande contenant l'ID du COLLI et l'approbateur.
            
        Returns:
            ColliResponseDTO: Le COLLI approuvé.
            
        Raises:
            NotFoundException: Si le COLLI n'existe pas.
            ColliAlreadyActiveException: Si le COLLI n'est pas en attente.
        """
        # 1. Récupérer le COLLI
        colli = self._colli_repo.find_by_id(command.colli_id)
        if not colli:
            raise NotFoundException(f"COLLI {command.colli_id} introuvable")
        
        # 2. Appliquer la logique métier (encapsulée dans l'entité)
        colli.approve(approved_by=command.approver_id)
        
        # 3. Persister les changements
        self._colli_repo.save(colli)
        
        # 4. Publier les événements domaine
        events = colli.collect_events()
        self._event_publisher.publish_all(events)
        
        # 5. Retourner le DTO
        return ColliResponseDTO.from_entity(colli)
