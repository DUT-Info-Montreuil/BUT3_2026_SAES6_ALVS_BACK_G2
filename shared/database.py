import os
import logging
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger(__name__)

db = SQLAlchemy()

def init_database(app):
    db.init_app(app)
    
    data_dir = os.path.join(app.config['BASE_DIR'], 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    with app.app_context():
        #import models here to create tables
        from models.user_model import User
        from models.colli_model import Colli
        from models.colli_member_model import ColliMember
        from models.letter_model import Letter
        from models.comment_model import Comment
         
        db.create_all()
        logger.info(f"Base de données et tables initialisées: {app.config['SQLALCHEMY_DATABASE_URI']}")