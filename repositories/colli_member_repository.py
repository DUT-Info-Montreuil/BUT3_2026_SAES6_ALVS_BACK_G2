from shared.database import db
from models.colli_member_model import ColliMember


class ColliMemberRepository:
    def save(self, colli_member):
        db.session.add(colli_member)
        db.session.commit()
        return colli_member
    
    
    def get_colli_member_by_id(self, colli_member_id):
        return ColliMember.query.get(colli_member_id)
    
    
    def get_members_by_colli_id(self, colli_id):
        return ColliMember.query.filter_by(colli_id=colli_id).all()
    
    
    def get_by_user_and_colli(self, user_id, colli_id):
        return ColliMember.query.filter_by(user_id=user_id, colli_id=colli_id).first()
    
    
    def delete(self, colli_member):
        db.session.delete(colli_member)
        db.session.commit()
        return True