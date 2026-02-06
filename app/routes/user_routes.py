from flask import request, jsonify
from app.routes import main
from services.user_service import UserService

@main.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = UserService.get_all_users()
    return jsonify([user.to_dict() for user in users])

@main.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict())

@main.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = UserService.create_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )
    
    if not user:
        return jsonify({'error': 'User already exists'}), 409
    
    return jsonify(user.to_dict()), 201

@main.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    user = UserService.update_user(user_id, **data)
    
    if not user:
        return jsonify({'error': 'User not found or update failed'}), 404
    
    return jsonify(user.to_dict())

@main.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    success = UserService.delete_user(user_id)
    
    if not success:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'message': 'User deleted successfully'})
