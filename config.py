import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or "maxpass"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        'sqlite:///' + os.path.join(basedir, 'petits_gazou.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_TABLES_EFFACER = os.environ.get('DB_TABLES_EFFACER') or [ 'publication', 'utilisateur']
    DB_TABLES_CREER = os.environ.get('DB_TABLES_CREER') or ['utilisateur', 'publication']
    
    MAIL_SERVER = "localhost"
    MAIL_PORT = 8025
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = [ 'email@example.com' ]

    PUBLICATION_PAR_PAGE = 5