from app import db
from app.api import bp
from app.modeles import Publication
from app.api.auth import basic_auth, token_auth
from flask import jsonify, request

@bp.route('/publications/<int:id>', methods=['GET'])
#@token_auth.login_required
def get_pubs(id):
    return jsonify(Publication.from_id(id).to_dict())

@bp.route('/publications/', methods=['GET'])
#@token_auth.login_required
def get_publications():
    page = request.args.get('page', 1, type=int)
    perp = min(request.args.get('par_page', 10, type=int), 100)
    return jsonify(Publication.to_collection_dict(
            Publication.query, page, perp, 
            'api.get_publications'
        )
    )


@bp.route('/publications/', methods=['POST'])
@token_auth.login_required
def creer_pub():
    return 'create'

@bp.route('/publications/', methods=['PUT'])
@token_auth.login_required
def put_pub():
    return 'modify'

@bp.route('/publications/', methods=['DELETE'])
@token_auth.login_required
def delete_pub():
    return 'delete'