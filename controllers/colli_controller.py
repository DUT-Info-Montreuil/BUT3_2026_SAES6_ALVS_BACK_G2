from flask import Blueprint, jsonify, request
from http import HTTPStatus
from services.colli_service import ColliService
from services.colli_member_service import ColliMemberService
from services.letter_service import LetterService


colli_bp = Blueprint('colli', __name__)

colli_service = ColliService()
colli_member_service = ColliMemberService()
letter_service = LetterService()


@colli_bp.get('')
def get_all_collis():
    collis = colli_service.get_all_collis()
    return jsonify(collis), HTTPStatus.OK


@colli_bp.post('')
def create_colli():
    data = request.get_json()
    new_colli = colli_service.create_colli(data)
    return jsonify(new_colli), HTTPStatus.CREATED


@colli_bp.get('/<string:colli_id>')
def get_colli_by_id(colli_id):
    colli = colli_service.get_colli_by_id(colli_id)
    if not colli:
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    return jsonify(colli), HTTPStatus.OK


@colli_bp.put('/<string:colli_id>')
def update_colli(colli_id):
    data = request.get_json()
    updated_colli = colli_service.update_colli_by_id(colli_id, data)
    
    if not updated_colli:
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    return jsonify(updated_colli), HTTPStatus.OK


@colli_bp.delete('/<string:colli_id>')
def delete_colli(colli_id):
    success = colli_service.delete_colli_by_id(colli_id)
    
    if not success:
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    return '', HTTPStatus.NO_CONTENT


@colli_bp.patch('/<string:colli_id>/approve')
def approve_colli(colli_id):
    approved_colli = colli_service.approve_colli(colli_id)
    
    if not approved_colli:
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    return jsonify(approved_colli), HTTPStatus.OK


@colli_bp.patch('/<string:colli_id>/reject')
def reject_colli(colli_id):
    rejected_colli = colli_service.reject_colli(colli_id)
    
    if not rejected_colli:
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    return jsonify(rejected_colli), HTTPStatus.OK


# --- Colli Member Endpoints --- #


@colli_bp.post('/<string:colli_id>/members')
def add_member_to_colli(colli_id):
    data = request.get_json()
    
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    data['colli_id'] = colli_id
    user_id = data.get('user_id')
    
    if colli_member_service.get_by_user_and_colli(user_id, colli_id):
        return jsonify({'error': 'User is already a member of this colli'}), HTTPStatus.CONFLICT
    
    new_member = colli_member_service.add_member_to_colli(data)
    return jsonify(new_member), HTTPStatus.CREATED


@colli_bp.get('/<string:colli_id>/members')
def get_members_by_colli_id(colli_id):
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    members = colli_member_service.get_members_by_colli_id(colli_id)
    return jsonify(members), HTTPStatus.OK


@colli_bp.delete('/<string:colli_id>/members/<string:colli_member_id>')
def remove_member_from_colli(colli_id, colli_member_id):
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    success = colli_member_service.remove_member_from_colli(colli_member_id)
    
    if not success:
        return jsonify({'error': 'Member not found in this colli'}), HTTPStatus.NOT_FOUND
    
    return '', HTTPStatus.NO_CONTENT


@colli_bp.patch('/<string:colli_id>/members/<string:colli_member_id>')
def update_member_role(colli_id, colli_member_id):
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    data = request.get_json()
    new_role = data.get('role')
    
    if not new_role:
        return jsonify({'error': 'New role is required'}), HTTPStatus.BAD_REQUEST
    
    updated_member = colli_member_service.update_member_role(colli_member_id, new_role)
    
    if not updated_member:
        return jsonify({'error': 'Member not found in this colli'}), HTTPStatus.NOT_FOUND
    
    return jsonify(updated_member), HTTPStatus.OK


# --- Letter Endpoints --- #


@colli_bp.post('/<string:colli_id>/letters')
def create_letter(colli_id):
    data = request.get_json()
    sender_id = data.get('sender_id')
    
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    if not sender_id:
        return jsonify({'error': 'Sender ID is required'}), HTTPStatus.BAD_REQUEST
    
    is_member = colli_member_service.get_by_user_and_colli(sender_id, colli_id)
    if not is_member:
        return jsonify({'error': 'Sender is not a member of this colli'}), HTTPStatus.FORBIDDEN
    
    data['colli_id'] = colli_id
    new_letter = letter_service.create_letter(data)
    
    return jsonify(new_letter), HTTPStatus.CREATED


@colli_bp.get('/<string:colli_id>/letters')
def get_letters_by_colli_id(colli_id):
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    letters = letter_service.get_letters_by_colli_id(colli_id)
    return jsonify(letters), HTTPStatus.OK


@colli_bp.get('/<string:colli_id>/letters/<string:letter_id>')
def get_letter_by_id(colli_id, letter_id):
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    letter = letter_service.get_letter_by_id(letter_id)
    if not letter or letter['colli_id'] != colli_id:
        return jsonify({'error': 'Letter not found in this colli'}), HTTPStatus.NOT_FOUND
    
    return jsonify(letter), HTTPStatus.OK


@colli_bp.delete('/<string:colli_id>/letters/<string:letter_id>')
def delete_letter(colli_id, letter_id):
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    letter = letter_service.get_letter_by_id(letter_id)
    if not letter or letter['colli_id'] != colli_id:
        return jsonify({'error': 'Letter not found in this colli'}), HTTPStatus.NOT_FOUND
    
    success = letter_service.delete_letter_by_id(letter_id)
    if not success:
        return jsonify({'error': 'Failed to delete letter'}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    return '', HTTPStatus.NO_CONTENT