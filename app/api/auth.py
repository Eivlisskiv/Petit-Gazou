from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.modeles import Utilisateur
from app.api.erreurs import reponse_erreur_json

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(un, pwd):
    user = Utilisateur.load_username(un)
    if user and user.valider_mot_de_passe(pwd):
        return user

@basic_auth.error_handler
def basic_auth_error(code):
    return reponse_erreur_json(code, 'Erreur Auth')

@token_auth.verify_token
def verify_token(token):
    return Utilisateur.verify_jeton(token) if token else None

@token_auth.error_handler
def token_auth_error(code):
    return reponse_erreur_json(code)
