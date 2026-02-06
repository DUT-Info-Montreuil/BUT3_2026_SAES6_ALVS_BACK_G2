from flask import Blueprint
from app.controllers.user_controller import UserController

bp = Blueprint('main', __name__)

# User routes
bp.route('/api/users', methods=['GET'])(UserController.get_users)
bp.route('/api/users/<int:user_id>', methods=['GET'])(UserController.get_user_by_id)
bp.route('/api/users', methods=['POST'])(UserController.create_user)
bp.route('/api/users/<int:user_id>', methods=['PUT'])(UserController.update_user)
bp.route('/api/users/<int:user_id>', methods=['DELETE'])(UserController.delete_user)

@bp.route('/api/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200