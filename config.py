import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    db_path = os.getenv('DATABASE_URL')
    
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, db_path)}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')