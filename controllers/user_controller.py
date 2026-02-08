from flask import Blueprint, request, jsonify
from http import HTTPStatus
from services.user_service import UserService


user_bp = Blueprint('user', __name__)
user_service = UserService()


@user_bp.get('')
def get_all_users():
    """Liste tous les utilisateurs
    ---
    tags:
      - Users
    responses:
      200:
        description: Liste des utilisateurs
    """
    users = user_service.get_all_users()
    return jsonify(users), HTTPStatus.OK


@user_bp.post('')
def create_user():
    """Créer un nouvel utilisateur
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - first_name
            - last_name
          properties:
            email:
              type: string
            password:
              type: string
            first_name:
              type: string
            last_name:
              type: string
    responses:
      201:
        description: Utilisateur créé
      409:
        description: Email déjà existant
    """
    data = request.get_json()
    if user_service.check_email_exists(data.get('email')):
        return jsonify({'error': 'Email already exists'}), HTTPStatus.CONFLICT
    
    new_user = user_service.create_user(data)
    return jsonify(new_user), HTTPStatus.CREATED


@user_bp.get('/<string:user_id>')
def get_user_by_id(user_id):
    """Récupérer un utilisateur par ID
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Utilisateur trouvé
      404:
        description: Utilisateur non trouvé
    """
    user = user_service.get_user_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), HTTPStatus.NOT_FOUND
    return jsonify(user), HTTPStatus.OK


@user_bp.put('/<string:user_id>')
def update_user_by_id(user_id):
    data = request.get_json()
    new_email = data.get('email')
    
    if new_email:
        existing_user = user_service.get_user_by_email(new_email)
        
        if existing_user and existing_user['id'] != user_id:
            return jsonify({'error': 'Email already exists'}), HTTPStatus.CONFLICT
        
    updated_user = user_service.update_user_by_id(user_id, data)
    
    if not updated_user:
        return jsonify({'error': 'User not found'}), HTTPStatus.NOT_FOUND
    
    return jsonify(updated_user), HTTPStatus.OK


@user_bp.delete('/<string:user_id>')
def delete_user_by_id(user_id):
    """Supprimer un utilisateur
    ---
    tags:
      - Users
    parameters:
      - name: user_id
        in: path
        type: string
        required: true
    responses:
      204:
        description: Supprimé avec succès
      404:
        description: Utilisateur non trouvé
    """
    success = user_service.delete_user_by_id(user_id)
    
    if not success:
        return jsonify({'error': 'User not found'}), HTTPStatus.NOT_FOUND
    
    return '', HTTPStatus.NO_CONTENT


@user_bp.post('/login')
def login_user():
    """Connexion utilisateur
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Connexion réussie
      401:
        description: Identifiants invalides
    """
    data_from_service = user_service.login_user() # TO DO at end
    return data_from_service