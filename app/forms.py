from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.modeles import Utilisateur

class FormSession(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired(message="Nom est un champ obligatoire")])
    password = PasswordField('Mot de passe', validators=[DataRequired(message="mot de passe est un champ obligatoire")])
    souvenir = BooleanField('Se souvenir de moi')
    submit = SubmitField('Etablir une session')

class FormRegister(FlaskForm):
    submit = SubmitField('Enregistrer')
    nom = StringField('Nom', validators=[DataRequired(message="Nom est un champ obligatoire")])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    password2 = PasswordField('Retapez Mot de passe', validators=[DataRequired(), EqualTo('password')])

    def validate_nom(self, nom):
        user = app.modeles.load_username(nom=nom.data).first()
        if user is not None:
            raise ValidationError('Ce nom existe déjà...')

    def validate_email(self, email):
        user = app.modeles.load_username(email=email.data).first()
        if user is not None:
            raise ValidationError('Ce courriel existe déjà...')

class FormEditProfile(FlaskForm):
    nom=StringField('Nom', validators=[DataRequired()])
    about=TextAreaField('À propos de moi', validators=[Length(min=0, max=140)])
    submit=SubmitField('Soumettre')

    def __init__(self, nom_original, *args, **kwargs):
        super(FormEditProfile, self).__init__(*args, **kwargs)
        self.nom_original = nom_original

    def validate_nom(self, nom):
        if nom.data != self.nom_original and app.modeles.load_username(nom=self.nom.data).first() is not None:
                raise ValidationError('Ce nom existe déjà dans la base de données')

class PublicationForm(FlaskForm):
    publication = TextAreaField('Message', validators=[DataRequired(), Length(min=1, max=140)])
    send = SubmitField('Envoyer')

