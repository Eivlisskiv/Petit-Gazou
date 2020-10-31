var socket;
var utilisateurs_tab = [];
var publications_tab = [];

var url_source = 'http://127.0.0.1:500'

async function socket_nouvelle_publication(data){
    console.log('socket_nouvelle_publication', data.id)

    dst = dst || element_dst

    infos = btoa('Ron:Password1')
    jeton = await ajax_jeton(infos, dst)
    console.log('jeton', jeton)
    let response;
    try{
        response = await $.ajax({
            type: 'GET',
            url: `${url_source}//api/publications/${data.id}`,

            beforeSend: function(xhr){
                xhr.setRequestHeader('Authorization', `Bearer ${infos}`)
            }
        })
    }catch(e){
        $(dst).text('Erreur de chargement');
        return
    }

    console.log('response.body', response.body)

    if(!publications_tab[response.id]){
        auteur = utilisateurs_tab[response.id_auteur]
        $(publication_dst).prepend(`
        <tr id=tr{id}>
            <td id=id{id}>${response.id}</td>
            <td id=avatar>
                <img src="${auteur.avatar}">${auteur.nom}</img>
            </td>
        </tr>
        `)
    }
}

function socket_actialiser(data){
    console.log(data.bidon)
    afficher_publications('#utilisateurs', "#publications", 1, 9999)
}

function initialiser_websocket(publications_dst){
    if(!socket || !socket.connected){
        socket = io.connect(`http://${document.domain}:${location.port}/chat`)
    }

    socket.on('nouvelle_publication', socket_nouvelle_publication);

    socket.on('actualiser', socket_actialiser);
}

async function afficher_data(utilisateurs_dst, publications_dst, page, perp){

    console.log("afficher_data début")

    //jQuery.ajaxSetup({async:false})

    users = await charger(`${url_source}/api/publications`, publications_dst, page, perp)
    pubs = await charger(`${url_source}/api/utilisateurs`, utilisateurs_dst, page, perp)

    //jQuery.ajaxSetup({async:true})
    console.log('end afficher_data')

    charger_utilisateurs(utilisateurs_dst, users)
    charger_publications(publications_dst, pubs)

    initialiser_websocket(publications_dst)

}

function charger_utilisateurs(dst, users){

    $(dst).empty()

    if(!users || !users.items){
        console.log('users', users)
        return;
    }

    users.items.forEach(u => {
        utilisateurs_tab[u.id] = {
            id: u.id,
            nom : u.nom,
            avatar : u.avatar,
            email : u.email,
            about : u.about,
            partisans : u.partisans,
            publications : u.publications,
        }

        html = u.partisans.map(function(pid) {
            return `<img src='${users[pid].avatar}' width="50px"></img>`
        }).join('')
        $(dst).append(`
        <tr id=tr{id}>
            <td id=id{id}>${u.id}</td>
            <td id=avatar${u.id}>
                <img src="${u.avatar}" width="100px"></img>
            </td>
            <td id=nom${u.nom}>
                <td>
                    Est partisan de ${html}
                </td>
            </td>
        </tr>
        `)
    })
}

function charger_publications(dst, pubs){
    $(dst).empty()

    if(!pubs || !pubs.items){
        console.log('pubs', pubs)
        return;
    }

    pubs.items.reverse().forEach(p => {
        publications_tab[p.id] = {
            id: p.id,
            id_utilisateur: p.id_auteur,
            corps: p.body,
            horodatage: p.creation
        }

        $(dst).append(`
        <tr id=tr{id}>
            <td id=id{id}>${p.id}</td>
            <td id=avatar${p.id}>
                <img src="${utilisateurs_tab[p.id_auteur].avatar}" width="10%"></img>
            </td>
            <td id=corp${p.id}>${p.body}</td>
        </tr>
        `)

        $('#auteur'. id).css("color", "red")
    })
}

var jeton

async function charger(requete, dst, page, perp){
    infos = btoa('Ron:Password1')

    jeton = await ajax_jeton(infos, dst)

    console.log('jeton', jeton)

    return await $.ajax({
        type: 'GET',
        url: requete,

        beforeSend: function(xhr){
            xhr.setRequestHeader('Authorization', `Bearer ${infos}`)
        },
        data: {page:page, perp:perp},
        
        error: function(){
            $(dst).text('Erreur de chargement');
        }
    })
}

async function ajax_jeton(infos, dst){
    let result;
    try{
        result = await $.ajax({
            type: 'GET',
            url: `${url_source}/api/jeton`,

            beforeSend: function(xhr){
                xhr.setRequestHeader('Authorization', `Basic ${infos}`)
            }
        })
    }catch(e){
        console.log('Error in Jeton request')
        console.log(e)
        $(dst).text('Erreur de chargement');
    }
    return result;
}

console.log('loaded base.js')