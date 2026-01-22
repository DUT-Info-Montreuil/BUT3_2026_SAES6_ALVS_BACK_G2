from shared.database import db
from models.colli_model import Colli

class ColliRepository:
    
    def save(self, colli):
        db.session.add(colli)
        db.session.commit()
        return colli
    
    
    def get_all_collis(self):
        return Colli.query.all()
    
    
    def get_colli_by_id(self, colli_id):
        return Colli.query.get(colli_id)
    
    
    def delete(self, colli):
        db.session.delete(colli)
        db.session.commit()
        return True