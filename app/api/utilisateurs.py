from app.api import bp
from app.modeles import Utilisateur
from app.api.auth import basic_auth, token_auth
from flask import jsonify, request

@bp.route('/utilisateurs/<int:id>', methods=['GET'])
#@token_auth.login_required
def get_utilisateur(id):
    return jsonify(Utilisateur.query.get_or_404(id).to_dict())

@bp.route('/utilisateurs', methods=['GET'])
#@token_auth.login_required
def get_utilisateurs():
    page = request.args.get('page', 1, type=int)
    perp = min(request.args.get('par_page', 10, type=int), 100)
    return jsonify(Utilisateur.to_collection_dict(
        Utilisateur.query, page, perp, 
        'api.get_publications'
        ))

@bp.route('/utilisateurs', methods=['POST'])
@token_auth.login_required
def create_utilisateurs():
    return 'create'

@bp.route('/utilisateurs/<int:id>', methods=['PUT'])
@token_auth.login_required
def modify_utilisateurs():
    return 'modify'

@bp.route('/utilisateurs/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_utilisateurs():
    return 'delete'