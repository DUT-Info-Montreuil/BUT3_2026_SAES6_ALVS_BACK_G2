from shared.database import db
from datetime import datetime
import uuid


class Colli(db.Model):
    __tablename__ = 'collis'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    theme = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Colli status could be 'pending', 'active', 'completed', 'rejected'
    status = db.Column(db.String(50), nullable=False, default='pending')
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    def __repr__(self):
        return f'<Colli {self.name} - {self.status}>'