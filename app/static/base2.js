var socket;
var utilisateurs_tableau = [];
var publications_tableau = [];

function initialiser_websocket(publications_dst)
{
    socket.on('nouvelle_publication', function(data){
        alert(data.id)

        infos = btoa("Ron:Password1")
        $.ajax({
            type: 'GET',
            url: "http://127.0.0.1:5000/api/jeton",

            beforeSend: function(xhr) {
                xhr.setRequestHeader('Authorization', 'Basic ' + infos);
            },
            success: function(reponse) {
                jeton = reponse.jeton;
            },
            error: function () {
                $(element_dst).text("Erreur de chargement.");
            },
        });

        requete = `http://127.0.0.1:5000//api/publications/${data.id}`;
        $.ajax({
            url: requete,
            type: 'GET',
            beforeSend: function(xhr){
                xhr.setRequestHeader('Authorization', `Bearer ${jeton}`);
            },
            data: { },
            success: function(reponse) {
                alert(reponse.corps);
                id = reponse["id"];
                if(typeofpublications_tableau[id] === 'undefined')
                {
                    corps = reponse["corps"];
                    id_utilisateur = reponse["utilisateur_id"];

                    auteur = utilisateurs_tableau[id_utilisateur].nom;
                    avatar = utilisateurs_tableau[id_utilisateur].avatar;
                    horodatage = reponse["horodatage"];
                    publications_tableau[id] = {id, id_utilisateur, corps, horodatage};
                    publication_format = `<tr id=tr{id}><td id=id{id}>${id}</td><td id=avatar${id}><img src="${avatar}" width=100px/></td><td id=auteur${id}>${auteur}</td><td id=horodatage${id}>${horodatage}</td><td id=corps${id}>${corps}</td></tr>`;
                    $(publications_dst).prepend(publication_format)
                }
            },
            error: function(){
                $(element_dst).text("Erreur de chargement.");
            },
        });
    });
    socket.on('actualiser', function(data){
        alert(data.bidon);
        afficher_publications("#utilisateurs", "#publications", 1, 9999);
    });
};

/*async*/ function afficher_publications(utilisateurs_dst, publications_dst, page, par_page)
{
    utilisateurs_json = { "par_reference": "vide" };
    publications_json = { "par_reference": "vide" };

    alert("afficher_publications début")
    $(utilisateurs_dst).empty();
    $(publications_dst).empty();
    jQuery.ajaxSetup({async:false});
    charger('http://127.0.0.1:5000/api/utilisateurs', utilisateurs_dst, utilisateurs_json, page, par_page)
    charger('http://127.0.0.1:5000/api/publications', publications_dst, publications_json, page, par_page)

    jQuery.ajaxSetup({async:true});
    alert("afficher_publications fin")

    u = utilisateurs_json.par_reference;
    u.items.forEach(element => {
        id = element["id"];
        nom = element["nom"];
        avatar = element["avatar"];
        courriel = element["courriel"];
        a_propos_de_moi = element["a_propos_de_moi"];

        partisans = element["partisans"];
        publications = element["publications"];
        utilisateurs_tableau[id] = {id, nom, avatar:avatar, courriel, a_propos_de_moi, partisans, publications};
    })

    utilisateurs_tableau.forEach(element => {
        id = element["id"];
        nom = element["nom"];
        avatar = element["avatar"];
        partisans = element["partisans"];
        avatars_partisans=""
        partisans.forEach(id_partisan => {
            avatar_partisan = utilisateurs_tableau[id_partisan].avatar;
            avatars_partisans = `<img src="${avatar_partisan}" width=50px/>${avatars_partisans}`;
        });
        utilisateurs_format = `
        <tr id=tr{id}>
            <td id=id{id}>${id}</td>
            <td id=avatar${id}>
                <img src="${avatar}" width=100px/>
            </td>
            <td id=nom${id}>${nom}
                <td>
                    Est partisan de ${avatars_partisans}
                </td>
            </td>
        </tr>`;
        $(utilisateurs_dst).append(utilisateurs_format)
    });

    p = publications_json.par_reference;
    p.items.reverse().forEach(element => {
        corps = element["corps"];
        id_utilisateur = element["utilisateur_id"];
        id = element["id"];
        auteur = utilisateurs_tableau[id_utilisateur].nom;
        avatar = utilisateurs_tableau[id_utilisateur].avatar;
        horodatage = element["horodatage"];

        publications_tableau[id] = {id, id_utilisateur, corps, horodatage};

        publication_format = `
        <tr id=tr{id}>
            <td id=id{id}>${id}</td>
            <td id=avatar${id}>
                <img src="${avatar}" width=100px/>
            </td>
            <td id=auteur${id}>${auteur}</td><td id=horodatage${id}>${horodatage}</td><td id=corps${id}>${corps}</td></tr>`;
        $(publications_dst).append(publication_format)

        $("#auteur". id).css("color", "red");
    });
    initialiser_websocket(publications_dst);
}


var jeton;
/*async*/ function charger(requete, element_dst, destination, page, par_page){
    infos = btoa("Ron:Password1")
    /*jeton = await test();
    if(!jeton){*/
        $.ajax({
            type: 'GET',
            url: "http://127.0.0.1:5000/api/jeton",
            beforeSend: function(xhr) {
                xhr.setRequestHeader('Authorization', 'Basic ' + infos);
            },
            success: function(reponse){
                jeton = reponse.jeton;
            },
            error: function() {
                $(element_dst).text("Erreur de chargement.");
            },
        });
    //}
    

    alert(jeton);
    $.ajax({
        url: requete,
        type: 'GET',
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', `Bearer ${jeton}`);
        },
        /*data: {page:page, par_page:par_page},*/
        success: function (reponse) {
            alert(reponse);
            destination.par_reference = reponse;
        },
        error: function() {
            $(element_dst).text("Erreur de chargement.");
            alert("Erreur de chargement.");
        },
    });
}
/*async function test(){
    jeton2 = await $.ajax({
        type: 'GET',
        url: "http://127.0.0.1:5000/api/jeton",
        beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', 'Basic ' + infos);
        },
        error: function() {
            $(element_dst).text("Erreur de chargement.");
        },
    });
    console.log("jeton2", jeton2);
    return jeton2.jeton;
}*/