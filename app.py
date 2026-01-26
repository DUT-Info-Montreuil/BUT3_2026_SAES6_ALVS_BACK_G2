#new api in development
from flask import Flask
from config import Config
from shared.database import init_database
from shared.socketio import socketio
from controllers.user_controller import user_bp
from controllers.colli_controller import colli_bp


def create_app():
    app = Flask(__name__)
    
    # Load configuration from Config class and initialize database
    app.config.from_object(Config)
    init_database(app)
    
    # Initialize SocketIO
    socketio.init_app(app)
    
    with app.app_context():
        import sockets.colli_events
    
    # Register routes, configurations, and the rest
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(colli_bp, url_prefix='/collis')
    
    return app
    

if __name__ == '__main__':
    app = create_app()
    socketio.run(app, debug=True)