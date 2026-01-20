from flask import Blueprint
from services.colli_service import ColliService


colli_bp = Blueprint('colli', __name__)
colli_service = ColliService()


@colli_bp.get('')
def get_all_collis():
    data_from_service = colli_service.get_all_collis()
    return data_from_service


@colli_bp.post('')
def create_colli():
    data_from_service = colli_service.create_colli()
    return data_from_service


@colli_bp.get('/<int:colli_id>')
def get_colli_by_id(colli_id):
    data_from_service = colli_service.get_colli_by_id(colli_id)
    return data_from_service


@colli_bp.put('/<int:colli_id>')
def update_colli(colli_id):
    data_from_service = colli_service.update_colli(colli_id)
    return data_from_service


@colli_bp.delete('/<int:colli_id>')
def delete_colli(colli_id):
    data_from_service = colli_service.delete_colli(colli_id)
    return data_from_service