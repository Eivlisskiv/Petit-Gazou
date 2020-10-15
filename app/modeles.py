from datetime import datetime
from app import db
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import LoginManager

@LoginManager.user_loader
def load_utilisateur(id):
    return Utilisateur.query.get(int(id))

tbpartisans = db.Table('TBPartisans',
    db.Column('suiveur', db.Integer, db.ForeignKey('utilisateur.id')),
    db.Column('suivit', db.Integer, db.ForeignKey('utilisateur.id'))
)

class PaginatedAPImixin(obj):
    @staticmethod
    def to_collection_dict(requete, page, perp, endpoint, **kwargs):
        ressources = requete.paginate(page, perp, False)
        return {
            'items': [item.to_dict() for item in ressources.items],
            '_meta':{
                'page':page,
                'per_page':perp,
                'page count':ressources.pages,
                'item count':ressources.total
            },
            '_links':{
                'self': url_for(endpoint, page=page, per_page=perp, **kwargs),
                'next': url_for(endpoint, page=page+1, per_page=perp, **kwards)
                        if ressources.has_next else None,
                'prev': url_for(endpoint, page=page-1, per_page=perp, **kwards)
                        if ressources.has_prev else None,
            }
        }

class Utilisateur(UserMixin, db.Model):
    @staticmethod
    def load_username(nom):
        return Utilisateur.query.filter_by(nom=nom).first_or_404()


    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    avatar = db.Column(db.Text(131072), index=False, unique=False)
    about = db.Column(db.Text(140))
    publications = db.relationship('Publication', backref='auteur', lazy='dynamic')

    lastonline = db.Column(db.DateTime, default=datetime.utcnow())

    partisans = db.relationship('Utilisateur', secondary=tbpartisans, 
        primaryjoin=(tbpartisans.c.suiveur == id),
        secondaryjoin=(tbpartisans.c.suivit == id),
        backref=db.backref('tbpartisans', lazy='dynamic'), lazy='dynamic'
    )

    def userSub(self, user):
        if not self.isPartisan(user):
            self.partisans.append(user)
        
    def userUnsub(self, user):
        if self.isPartisan(user):
            self.partisans.remove(user)

    def isPartisan(self, user):
        return self.partisans.filter(tbpartisans.c.suivit == user.id).count() > 0

    def getPartisansPubs(self):
        return Publication.query.join(
            tbpartisans, (tbpartisans.c.suivit == Publication.id_auteur)
        ).filter(tbpartisans.c.suiveur == self.id).union(
            Publication.query.filter_by(id_auteur=self.id)
        ).order_by(Publication.creation.desc())

    def __repr__(self):
        return '<Utilisateur {}>'.format(self.nom)

    def enregisrter_mot_de_passe(self, pwd):
        self.password = generate_password_hash(pwd)

    def valider_mot_de_passe(self, pwd):
        return check_password_hash(self.password, pwd)

    def to_dict(self):
        pubs = self.getPartisansPubs()
        followers = self.partisans

        return {
            'id': self.id,
            'nom': self.nom,
            'email': self.email,
            'avatar': self.avatar,
            'about': self.about,
            'lastseen': self.lastonline,
            'pubs': [item.id for item in pubs],
            'followers': [item.id for item in followers]
        }

class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(128))
    creation = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    id_auteur = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
    def __repr__(self):
        return '<Post {}>'.format(self.body)

def get_modele(modele, ligne, racine):

    if modele == "publication":
        id=int(ligne[0])

        horodatage=datetime.strptime(ligne[2].strip(), '%Y-%m-%d %H:%M:%S.%f')
        u = Utilisateur.query.get(id)

        p = Publication(body=ligne[1].strip(), creation=horodatage, id_auteur=id)

        print(id)
        print(u.nom)
        print(p.id_auteur)

        return p
    if modele == "utilisateur":
        nom = ligne[0].strip()
        source = os.path.join(racine, 'base64/{}.base64'.format(nom))
        print(source)
        if os.path.isfile(source):
            with open(source, 'r') as file:
                avatar = file.read()
        else:
            avatar = "null"
        u=Utilisateur(nom=nom, email=ligne[1].strip(), avatar=avatar, about=ligne[3].strip(), lastonline=datetime.utcnow())
        u.enregisrter_mot_de_passe(ligne[2].strip())
        return u