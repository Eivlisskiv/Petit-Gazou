from app.api import bp
from app.modeles import Utilisateur
from flask import jsonify, request

@bp.route('/utilisateurs/<int:id>', methods=['GET'])
def get_utilisateur(id):
    return jsonify(Utilisateur.query.get_or_404(id).to_dict())

@bp.route('/utilisateurs', methods=['GET'])
def get_utilisateurs():
    page = request.args.get('page', 1, type=int)
    perp = min(request.args.get('par_page', 10, type=int), 100)
    return jsonify(Utilisateur.to_collection_dict(Utilisateur.query, page, perp, 'api.get_publications'))

@bp.route('/utilisateurs', methods=['POST'])
def create_utilisateurs():
    return 'create'

@bp.route('/utilisateurs/<int:id>', methods=['PUT'])
def modify_utilisateurs():
    return 'modify'

@bp.route('/utilisateurs/<int:id>', methods=['DELETE'])
def delete_utilisateurs():
    return 'delete'