from shared.database import db
from models.comment_model import Comment


class CommentRepository:
    
    def save(self, comment):
        db.session.add(comment)
        db.session.commit()
        return comment
    
    
    def get_comment_by_id(self, comment_id):
        return Comment.query.get(comment_id)
    
    
    def get_comments_by_letter_id(self, letter_id):
        return Comment.query.filter_by(letter_id=letter_id).order_by(Comment.created_at.asc()).all()
    
    
    def delete(self, comment):
        db.session.delete(comment)
        db.session.commit()
        return True