from app.api import bp
from flask import jsonify
from app import db
from app.api.auth import basic_auth, token_auth

@bp.route('/jeton', methods=['GET'])
@basic_auth.login_required
def get_jeton():
    jeton = basic_auth.current_user().get_jeton()
    db.session.commit()
    return jsonify({'jeton':jeton})

@bp.route('/jeton', methods=['DELETE'])
@basic_auth.login_required
def delete_jeton():
    jeton = basic_auth.current_user().revoquer_jeton()
    db.session.commit()
    return '', 204