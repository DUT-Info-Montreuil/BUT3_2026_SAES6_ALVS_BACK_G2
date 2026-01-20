'''from sqlalchemy import create_engine


db_path = 'sqlite:///data.db'

engine = create_engine(db_path)

try:
    conn = engine.connect()
    print("Database connection established.")
except Exception as ex:
    print("Database connection failed:", ex)'''

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
        
        db.create_all()
        print(f"Base de données et tables initialisées: {app.config['SQLALCHEMY_DATABASE_URI']}")