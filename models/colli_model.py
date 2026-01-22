from shared.database import db
from datetime import datetime
import uuid


class Colli(db.Model):
    __tablename__ = 'collis'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    theme = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    
    def __repr__(self):
        return f'<Colli {self.name}>'