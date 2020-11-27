from datetime import datetime, timedelta
from app import db
import os, base64
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for
from app import LoginManager

from PIL import Image, ImageDraw, ImageFont
import random, base64
from io import BytesIO

@LoginManager.user_loader
def load_utilisateur(id):
    return Utilisateur.query.get(int(id))

tbpartisans = db.Table('TBPartisans',
    db.Column('suiveur', db.Integer, db.ForeignKey('utilisateur.id')),
    db.Column('suivit', db.Integer, db.ForeignKey('utilisateur.id'))
)

class PaginatedAPImixin():
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
                'next': url_for(endpoint, page=page+1, per_page=perp, **kwargs)
                        if ressources.has_next else None,
                'prev': url_for(endpoint, page=page-1, per_page=perp, **kwargs)
                        if ressources.has_prev else None,
            }
        }

class Utilisateur(PaginatedAPImixin, UserMixin, db.Model):
    @staticmethod
    def load_username(nom):
        return Utilisateur.query.filter_by(nom=nom).first_or_404()

    @staticmethod
    def create_user(nom, email, pwd):
        user = Utilisateur(nom=nom, email=email)
        user.enregisrter_mot_de_passe(pwd)
        user.create_pfp()
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def verify_jeton(jeton):
        user = Utilisateur.query.filter_by(jeton=jeton).first()
        if not user or not user.jeton or user.jeton_expiration < datetime.utcnow():
            return None
        return user

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    avatar = db.Column(db.Text(131072), index=False, unique=False)
    about = db.Column(db.Text(140))
    lastonline = db.Column(db.DateTime, default=datetime.utcnow())

    jeton = db.Column(db.String(32), index=True, unique=True)
    jeton_expiration = db.Column(db.DateTime)

    publications = db.relationship('Publication', backref='auteur', lazy='dynamic')

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
            'partisans': [item.id for item in followers]
        }
    
    def get_jeton(self, expire=3600):
        now = datetime.utcnow()
        if not self.jeton or self.jeton_expiration < now + timedelta(seconds=60): 
            self.jeton = base64.b64encode(os.urandom(24)).decode('utf-8')
            self.jeton_expiration = now + timedelta(seconds=expire)
            db.session.add(self)
        return self.jeton
    
    def revoke_jeton(self):
        self.jeton_expiration = datetime.utcnow() - timedelta(seconds=1)
    
    def create_pfp(self):
        fnt = ImageFont.truetype('./Library/Fonts/arial.ttf', 15)
        image = Image.new('RGB', (128,128), color="Black")
        for i in range(20):
            coords = (random.randint(0, 128),
             random.randint(0, 128))

            color = (random.randint(0, 255),
            random.randint(0, 255), random.randint(0, 255)) 

            h = random.randint(10, i + 10)
            fnt = ImageFont.truetype('./Library/Fonts/arial.ttf', h)
            d = ImageDraw.Draw(image)
            d.text(coords, self.nom, font=fnt, fill=color)
        tampon = BytesIO()
        image.save(tampon, format="JPEG")
        image_base = "data:image/jpg;base64," + base64.b64encode(tampon.getvalue()).decode('utf-8')
        print('image created:')
        print(image_base)
        self.avatar =  image_base
        return image_base


class Publication(PaginatedAPImixin, db.Model):

    @staticmethod
    def from_id(id):
        return Publication.query.get_or_404(id).to_dict()

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(128))
    creation = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    id_auteur = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))
    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def to_dict(self):
        return {
            'id' : self.id,
            'body': self.body,
            'creation': self.creation,
            'id_auteur': self.id_auteur
        }

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