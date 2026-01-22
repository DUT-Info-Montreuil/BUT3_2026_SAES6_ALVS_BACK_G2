from shared.database import db
from models.user_model import User

class UserRepository:
    
    def save(self, user):
        db.session.add(user)
        db.session.commit()
        return user
    
    
    def get_all_users(self):
        return User.query.all()
    
    
    def get_user_by_id(self, user_id):
        return User.query.get(user_id)
    
    
    def get_user_by_email(self, email):
        return User.query.filter_by(email=email).first()
    
    
    def delete(self, user):
        db.session.delete(user)
        db.session.commit()
        return True