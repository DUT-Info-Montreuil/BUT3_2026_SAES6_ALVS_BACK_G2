#new api in development
from flask import Flask
from config import Config
from shared.database import init_database
from controllers.user_controller import user_bp
from controllers.colli_controller import colli_bp


def create_app():
    app = Flask(__name__)
    
    # Load configuration from Config class and initialize database
    app.config.from_object(Config)
    init_database(app)
    
    # Register routes, configurations, and the rest
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(colli_bp, url_prefix='/collis')
    
    return app
    

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)