
class Prefabs():

    def user_image():
        return "<img src='{{ user.avatar }}'>"

    def publication():
        return "<td><img src='{{pub.auteur.avatar}}'>{{user.nom}}</img></td> <td><b>{{ pub.auteur.nom }}</b>: {{ pub.body }}</td>"