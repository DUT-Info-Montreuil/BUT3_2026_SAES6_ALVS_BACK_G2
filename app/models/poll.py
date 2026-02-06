# -*- coding: utf-8 -*-
"""
ALVS IA pipeline test - Fichier traité par le système multi-agent IA

Modèles Poll, Option et Vote pour la gestion des sondages
"""

from datetime import datetime
from app.extensions import db


class Poll(db.Model):
    """Modèle représentant un sondage"""
    
    __tablename__ = 'polls'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    allow_multiple_votes = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relations
    options = db.relationship('Option', backref='poll', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='poll', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_polls', lazy=True)
    
    def __init__(self, title, description, created_by, allow_multiple_votes=False):
        self.title = title
        self.description = description
        self.created_by = created_by
        self.allow_multiple_votes = allow_multiple_votes
    
    def to_dict(self, include_votes=False):
        """Convertit le sondage en dictionnaire"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_by': self.created_by,
            'is_active': self.is_active,
            'allow_multiple_votes': self.allow_multiple_votes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'options': [option.to_dict(include_votes=include_votes) for option in self.options]
        }
        
        if include_votes:
            data['total_votes'] = len(self.votes)
            
        return data
    
    def __repr__(self):
        return f'<Poll {self.title}>'


class Option(db.Model):
    """Modèle représentant une option de sondage"""
    
    __tablename__ = 'options'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relations
    votes = db.relationship('Vote', backref='option', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, text, poll_id):
        self.text = text
        self.poll_id = poll_id
    
    def to_dict(self, include_votes=False):
        """Convertit l'option en dictionnaire"""
        data = {
            'id': self.id,
            'text': self.text,
            'poll_id': self.poll_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_votes:
            data['vote_count'] = len(self.votes)
            
        return data
    
    def __repr__(self):
        return f'<Option {self.text}>'


class Vote(db.Model):
    """Modèle représentant un vote"""
    
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Contrainte d'unicité pour éviter les votes multiples (sauf si autorisé)
    __table_args__ = (db.UniqueConstraint('user_id', 'poll_id', 'option_id', name='unique_vote'),)
    
    def __init__(self, user_id, poll_id, option_id):
        self.user_id = user_id
        self.poll_id = poll_id
        self.option_id = option_id
    
    def to_dict(self):
        """Convertit le vote en dictionnaire"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'poll_id': self.poll_id,
            'option_id': self.option_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Vote user:{self.user_id} poll:{self.poll_id} option:{self.option_id}>'
