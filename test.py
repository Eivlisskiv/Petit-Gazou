from datetime import datetime, timedelta
import unittest
from app import app, db
from app.modeles import Utilisateur, Publication

class CasModeleUser(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_pwdHashing(self):
        u = Utilisateur(nom='patate')
        pwd = 'Password1'
        u.enregisrter_mot_de_passe(pwd)
        self.assertFalse(u.valider_mot_de_passe(pwd[::-1]))
        self.assertTrue(u.valider_mot_de_passe(pwd))

    def test_Subs(self):
        u1 = Utilisateur(nom='patate', email='p@info.cgg')
        u2 = Utilisateur(nom='tomate', email='t@info.cgg')
        db.session.add_all([u1, u2])
        db.session.commit()

        self.assertEqual(u1.partisans.all(), [])
        self.assertEqual(u1.tbpartisans.all(), [])

        u1.userSub(u2)
        db.session.commit()

        self.assertTrue(u1.isPartisan(u2))
        self.assertEqual(u1.partisans.count(), 1)
        self.assertEqual(u1.partisans.first().nom, 'tomate')
        self.assertEqual(u2.tbpartisans.count(), 1)
        self.assertEqual(u2.tbpartisans.first().nom, 'patate')

        u1.userUnsub(u2)
        db.session.commit()

        self.assertFalse(u1.isPartisan(u2))
        self.assertEqual(u1.partisans.count(), 0)
        self.assertEqual(u2.tbpartisans.count(), 0)

    def test_subbedPubs(self):
        usertb = []
        for i in range(4):
            usertb.append(Utilisateur(nom='u' + str(i), email= 'u' + str(i) + '@info.cgg'))

        db.session.add_all(usertb)

        now = datetime.utcnow()
        pubstb = []
        for u in usertb:
            pubstb.append(Publication(body='Publication de ' + u.nom, auteur=u, creation=now + timedelta(seconds=1)))

        db.session.add_all(pubstb)

        usertb[0].userSub(usertb[1])
        usertb[0].userSub(usertb[3])
        usertb[1].userSub(usertb[2])
        usertb[2].userSub(usertb[3])

        db.session.commit()
        
        substb = []
        for u in usertb:
            substb.append(u.getPartisansPubs().all())

        self.assertEqual(substb[0], [pubstb[0], pubstb[1], pubstb[3]])
        self.assertEqual(substb[1], [pubstb[1], pubstb[2]])

        self.assertEqual(substb[2], [pubstb[2], pubstb[3]])
        self.assertEqual(substb[3], [pubstb[3]])



if __name__ == "__main__":
    unittest.main(verbosity=2)
