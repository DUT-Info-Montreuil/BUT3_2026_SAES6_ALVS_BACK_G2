# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Service de gestion des sondages
"""

from typing import Optional, Dict, Any, List
from app.extensions import db
from app.models.poll import Poll, Option, Vote
from app.models.user import User


class PollService:
    """Service pour la gestion des sondages"""
    
    @staticmethod
    def create_poll(title: str, description: str, created_by: int, options: List[str], allow_multiple_votes: bool = False) -> Dict[str, Any]:
        """Crée un nouveau sondage avec ses options"""
        try:
            # Vérifier que l'utilisateur existe
            user = User.query.filter_by(id=created_by, is_active=True).first()
            if not user:
                return {
                    'success': False,
                    'message': 'Utilisateur non trouvé',
                    'poll': None
                }
            
            # Créer le sondage
            poll = Poll(
                title=title,
                description=description,
                created_by=created_by,
                allow_multiple_votes=allow_multiple_votes
            )
            
            db.session.add(poll)
            db.session.flush()  # Pour obtenir l'ID du sondage
            
            # Créer les options
            for option_text in options:
                option = Option(text=option_text, poll_id=poll.id)
                db.session.add(option)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Sondage créé avec succès',
                'poll': poll
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Erreur lors de la création du sondage: {str(e)}',
                'poll': None
            }
    
    @staticmethod
    def get_poll_by_id(poll_id: int) -> Optional[Poll]:
        """Récupère un sondage par son ID"""
        try:
            return Poll.query.filter_by(id=poll_id, is_active=True).first()
        except Exception:
            return None
    
    @staticmethod
    def get_all_polls() -> List[Poll]:
        """Récupère tous les sondages actifs"""
        try:
            return Poll.query.filter_by(is_active=True).all()
        except Exception:
            return []
    
    @staticmethod
    def vote_on_poll(user_id: int, poll_id: int, option_id: int) -> Dict[str, Any]:
        """Enregistre un vote sur un sondage"""
        try:
            # Vérifier que l'utilisateur existe
            user = User.query.filter_by(id=user_id, is_active=True).first()
            if not user:
                return {
                    'success': False,
                    'message': 'Utilisateur non trouvé'
                }
            
            # Vérifier que le sondage existe et est actif
            poll = Poll.query.filter_by(id=poll_id, is_active=True).first()
            if not poll:
                return {
                    'success': False,
                    'message': 'Sondage non trouvé ou inactif'
                }
            
            # Vérifier que l'option existe et appartient au sondage
            option = Option.query.filter_by(id=option_id, poll_id=poll_id).first()
            if not option:
                return {
                    'success': False,
                    'message': 'Option non trouvée'
                }
            
            # Vérifier si l'utilisateur a déjà voté
            existing_vote = Vote.query.filter_by(user_id=user_id, poll_id=poll_id).first()
            if existing_vote and not poll.allow_multiple_votes:
                return {
                    'success': False,
                    'message': 'Vous avez déjà voté sur ce sondage'
                }
            
            # Vérifier si l'utilisateur a déjà voté pour cette option spécifique
            existing_option_vote = Vote.query.filter_by(user_id=user_id, poll_id=poll_id, option_id=option_id).first()
            if existing_option_vote:
                return {
                    'success': False,
                    'message': 'Vous avez déjà voté pour cette option'
                }
            
            # Créer le vote
            vote = Vote(user_id=user_id, poll_id=poll_id, option_id=option_id)
            db.session.add(vote)
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Vote enregistré avec succès',
                'vote': vote
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Erreur lors de l\'enregistrement du vote: {str(e)}'
            }
    
    @staticmethod
    def has_user_voted(user_id: int, poll_id: int) -> bool:
        """Vérifie si un utilisateur a déjà voté sur un sondage"""
        try:
            vote = Vote.query.filter_by(user_id=user_id, poll_id=poll_id).first()
            return vote is not None
        except Exception:
            return False
    
    @staticmethod
    def get_poll_results(poll_id: int) -> Dict[str, Any]:
        """Récupère les résultats d'un sondage"""
        try:
            poll = Poll.query.filter_by(id=poll_id, is_active=True).first()
            if not poll:
                return {
                    'success': False,
                    'message': 'Sondage non trouvé',
                    'results': None
                }
            
            results = {
                'poll': poll.to_dict(include_votes=True),
                'total_votes': len(poll.votes),
                'options_results': []
            }
            
            for option in poll.options:
                option_votes = len(option.votes)
                percentage = (option_votes / len(poll.votes) * 100) if len(poll.votes) > 0 else 0
                
                results['options_results'].append({
                    'option': option.to_dict(),
                    'votes': option_votes,
                    'percentage': round(percentage, 2)
                })
            
            return {
                'success': True,
                'message': 'Résultats récupérés avec succès',
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur lors de la récupération des résultats: {str(e)}',
                'results': None
            }
    
    @staticmethod
    def delete_poll(poll_id: int, user_id: int) -> Dict[str, Any]:
        """Supprime (désactive) un sondage"""
        try:
            poll = Poll.query.filter_by(id=poll_id, is_active=True).first()
            if not poll:
                return {
                    'success': False,
                    'message': 'Sondage non trouvé'
                }
            
            # Vérifier que l'utilisateur est le créateur ou un admin
            user = User.query.filter_by(id=user_id, is_active=True).first()
            if not user or (poll.created_by != user_id and user.role != 'admin'):
                return {
                    'success': False,
                    'message': 'Vous n\'avez pas les droits pour supprimer ce sondage'
                }
            
            # Désactiver le sondage
            poll.is_active = False
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Sondage supprimé avec succès'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Erreur lors de la suppression: {str(e)}'
            }
