from shared.database import db
from datetime import datetime
import uuid


class ColliMember(db.Model):
    __tablename__ = 'colli_members'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    colli_id = db.Column(db.String(36), db.ForeignKey('collis.id'), nullable=False)
    
    # Role could be 'admin', 'moderator', 'member'
    role = db.Column(db.String(30), nullable=False, default='member')
    
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'colli_id', name='_user_colli_uc'),
    )