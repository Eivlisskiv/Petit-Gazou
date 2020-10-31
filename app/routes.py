from app import app
from app import db, modeles, socketio
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import FormSession, FormRegister, FormEditProfile, PublicationForm
from app.modeles import Utilisateur, Publication
from flask_login import current_user, login_user, logout_user, login_required
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime
import random, base64

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.lastonline = datetime.utcnow()
        db.session.commit()

@app.route('/websocket')
def websocket():
    print('Websocket route')
    return render_template('websocket.html')

def getPages(list, url):
    return (
        url_for(url, page=list.next_num) \
        if list.has_next else None, 
        url_for(url, page=list.prev_num) \
        if list.has_prev else None
    )

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    if current_user is None or not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = PublicationForm()
    if request.method == 'POST' and form.validate_on_submit():
        pub = Publication(body=form.publication.data, auteur=current_user)
        db.session.add(pub)
        db.session.commit()
        socketio.emit('nouvelle_publication', { 'id' : pub.id }, namespace='/chat')
        flash('Publication envoyée!')

    pubs = current_user.getPartisansPubs().paginate(
            request.args.get('page', 1, type=int),
            app.config['PUBLICATION_PAR_PAGE'], False
        )

    (next, prev) = getPages(pubs, 'index')

    return render_template('index.html', title="Accueil", user=current_user,
        pubs=pubs.items, form=form, next=next, prev=prev)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    formulaire = FormRegister()
    if formulaire.is_submitted(): 
        print("submitted")
        if formulaire.validate():
            flash('Validation complete!')
            user = Utilisateur(nom=formulaire.nom.data, email=formulaire.email.data)
            user.enregisrter_mot_de_passe(formulaire.password.data)
            fnt = ImageFont.truetype('./Library/Fonts/arial.ttf', 15)
            image = Image.new('RGB', (128,128), color="Black")
            for i in range(20):
                coords = (random.randint(0, 128), random.randint(0, 128))
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) 
                h = random.randint(10, i + 10)
                fnt = ImageFont.truetype('./Library/Fonts/arial.ttf', h)
                d = ImageDraw.Draw(image)
                d.text(coords, user.nom, font=fnt, fill=color)
            tampon = BytesIO()
            image.save(tampon, format="JPEG")
            image_base = "data:image/jpg;base64," + base64.b64encode(tampon.getvalue()).decode('utf-8')
            print(image_base)
            user.avatar =  image_base
            db.session.add(user)
            db.session.commit()
            flash('Félicitations, vous êtes maintenant enregistré!')
            return redirect(url_for('login'))  
    flash('Inscription en cours...')
    return render_template('register.html', title="Enregistrement", form=formulaire)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    formulaire = FormSession()
    if formulaire.validate_on_submit():
        user = Utilisateur.query.filter_by(nom=formulaire.nom.data).first()
        if user is None or not user.valider_mot_de_passe(formulaire.password.data):
            flash("Nom utilisateur ou mot de passe invalide")
            return redirect(url_for('login'))
        login_user(user, remember=formulaire.souvenir.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            return redirect(url_for('index'))
        return redirect(next_page)
    return render_template('login.html', title='Etablir Session', form=formulaire)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile/<nom>')
@login_required
def profile(nom):
    user = Utilisateur.load_username(nom)
    return render_template('profile.html', user=user, pubs=user.publications.all())

@app.route('/suivre/<nom>', methods=['GET'])
@login_required
def suivre(nom):
    user = Utilisateur.load_username(nom)
    if user is None:
        return redirect(url_for('index'))
    if user != current_user:
        if not current_user.isPartisan(user):
            current_user.userSub(user)
            flash('Vous suivez maintenant ' + nom)
        else:
            current_user.userUnsub(user)
            flash('Vous ne suivez plus ' + nom)
        db.session.commit()
        socketio.emit('actualiser', {'bison':'vide'}, namespace='/chat')
    
    return redirect(url_for('profile', nom=nom))
        
@app.route('/editprofile', methods=['GET', 'POST'])
@login_required
def editprofile():
    form = FormEditProfile(current_user.nom)
    if request.method == 'GET':
        form.nom.data = current_user.nom
        form.about.data = current_user.about
    elif form.validate_on_submit:
        current_user.nom = form.nom.data
        current_user.about = form.about.data
        db.session.commit()
        flash("Modifications sauvegardées.")
        return redirect(url_for('profile', nom=current_user.nom))
    
    return render_template('editprofile.html', title='Editer Profil', form=form)

@app.route('/explorer')
@login_required
def explorer():
    pubs=Publication.query.order_by(Publication.creation.desc()).paginate(
            request.args.get('page', 1, type=int),
            app.config['PUBLICATION_PAR_PAGE'], False
        )
    (next, prev) = getPages(pubs, 'explorer')
    return render_template('index.html', title='Explorer', 
        page=request.args.get('page', 1, type=int),
        pubs=pubs.items, next=next, prev=prev
    )