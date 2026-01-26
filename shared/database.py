import os
from flask_sqlalchemy import SQLAlchemy

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
        
        db.create_all()
        print(f"<Dev>Base de données et tables initialisées: {app.config['SQLALCHEMY_DATABASE_URI']}")