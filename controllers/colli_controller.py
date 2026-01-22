from flask import Blueprint, jsonify, request
from http import HTTPStatus
from services.colli_service import ColliService


colli_bp = Blueprint('colli', __name__)
colli_service = ColliService()


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