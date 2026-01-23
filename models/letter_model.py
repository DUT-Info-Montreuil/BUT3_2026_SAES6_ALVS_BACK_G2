from shared.database import db
from datetime import datetime
import uuid

class Letter(db.Model):
    __tablename__ = 'letters'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 'text' for text letters or 'file' for pdf letters
    letter_type = db.Column(db.String(50), nullable=False, default='text')
    
    # Text content for 'text' letters or name/description for 'file' letters
    content = db.Column(db.Text, nullable=True)
    
    # URL or path to the uploaded pdf file for 'file' letters
    file_url = db.Column(db.String(255), nullable=True)
    
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    colli_id = db.Column(db.String(36), db.ForeignKey('collis.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    