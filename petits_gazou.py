from app import app, db, modeles, socketio
from app.modeles import Utilisateur, Publication
import os, csv

@app.shell_context_processor
def make_shell_context():
    return {'db':db, 'U': Utilisateur, 'P':Publication }

if __name__ == "__main__":
    socketio.run(app)

@app.before_first_request
def initialization():
    print("Init")
    tables = app.config['DB_TABLES_EFFACER']
    for table in tables:
        requete="delete from {}".format(table)
        print(requete)
        db.session.execute(requete)

    tables = app.config['DB_TABLES_CREER']
    racine = os.path.abspath(os.path.dirname(__file__))
    for table in tables:
        fichier = 'csv/{}.csv'.format(table)
        if os.path.exists("{}/{}".format(racine, fichier)):
            source = os.path.join(racine, fichier)

            print("==={}===".format(table))
            with open(source) as fichier_csv:
                lecteur_csv = csv.reader(fichier_csv, delimiter=',')
                for ligne in lecteur_csv:
                    element = modeles.get_modele(table, ligne, racine)
                    print(element)

                    if element is not None:
                        db.session.add(element)

    u = Utilisateur.query.filter_by(nom='Harry').first_or_404()
    u2 = Utilisateur.query.filter_by(nom='Hermione').first_or_404()
    u3 = Utilisateur.query.filter_by(nom='Ron').first_or_404()
    u.userSub(u2)
    u.userSub(u3)
    db.session.commit()

    print('List pubs suivies par {}'.format(u.nom))
    for p in u.getPartisansPubs():
        print('{}: {}'.format(p.auteur.nom, p.body))

