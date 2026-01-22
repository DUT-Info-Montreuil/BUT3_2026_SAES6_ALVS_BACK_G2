from flask import Blueprint, jsonify, request
from http import HTTPStatus
from services.colli_service import ColliService
from services.colli_member_service import ColliMemberService


colli_bp = Blueprint('colli', __name__)
colli_service = ColliService()
colli_member_service = ColliMemberService()


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
        return jsonify({'message': 'Colli not found'}), HTTPStatus.NOT_FOUND
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


@colli_bp.delete('/<string:colli_id>/members/<string:member_colli_id>')
def remove_member_from_colli(colli_id, member_colli_id):
    if not colli_service.get_colli_by_id(colli_id):
        return jsonify({'error': 'Colli not found'}), HTTPStatus.NOT_FOUND
    
    success = colli_member_service.remove_member_from_colli(member_colli_id)
    
    if not success:
        return jsonify({'error': 'Member not found in this colli'}), HTTPStatus.NOT_FOUND
    
    return '', HTTPStatus.NO_CONTENT