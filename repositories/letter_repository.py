from shared.database import db
from models.letter_model import Letter


class LetterRepository:
    
    def save(self, letter):
        db.session.add(letter)
        db.session.commit()
        return letter
    
    
    def get_letter_by_id(self, letter_id):
        return Letter.query.get(letter_id)
    
    
    def get_letters_by_colli_id(self, colli_id):
        return Letter.query.filter_by(colli_id=colli_id).order_by(Letter.created_at.asc()).all()
    
    
    def delete(self, letter):
        db.session.delete(letter)
        db.session.commit()
        return True