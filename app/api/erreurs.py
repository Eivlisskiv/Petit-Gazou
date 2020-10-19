from flask import render_template, jsonify, request
from werkzeug.http import HTTP_STATUS_CODES
from app import app, db

def reponse_erreur_json(code, message=None):
    payload = { 'erreur': message + ' ' + str(code) }
    print(payload)

    response = jsonify(payload)
    response.status_code = code
    return response

def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text\html']

@app.errorhandler(404)
def not_found_error(error):
    if wants_json_response:
        return reponse_erreur_json(404, 'invalid request')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response:
        return reponse_erreur_json(500, 'internal error')
    return render_template('500.html'), 500