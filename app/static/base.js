var socket;
var utilisateurs_tab = [];
var publications_tab = [];

var jeton;

var url_source = 'http://127.0.0.1:5000'

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

function initialiser_websocket(){
    socket.on('nouvelle_publication', socket_nouvelle_publication);

    socket.on('actualiser', socket_actialiser);

    if(!socket || !socket.connected){
        socket = io.connect(`http://${document.domain}:${location.port}/chat`)
    }
}

async function afficher_data(utilisateurs_dst, publications_dst, page, perp){
    let infos = btoa('Ron:Password1')

    //jQuery.ajaxSetup({async:true})
    jeton = await async_ajax('GET', `${url_source}/api/jeton`, 'Basic', infos).jeton

    data =  {page:page, perp:perp}

    //alert('Get users')
    users = await async_ajax('GET', `${url_source}/api/utilisateurs`, 'Bearer', infos, utilisateurs_dst, data)
    //alert('Get pubs')
    pubs = await async_ajax('GET', `${url_source}/api/publications`, 'Bearer', infos, publications_dst, data)

    //alert('load users')
    charger_utilisateurs(utilisateurs_dst, users)
    //alert('load pubs')
    charger_publications(publications_dst, pubs)
}

async function charger_utilisateurs(dst, users){
    $(dst).empty()

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
    })

    utilisateurs_tab.forEach(u => {
        html =  u.partisans && u.partisans.length > 0 ? 
            html = u.partisans.map(pid => {
                return `<img src='${utilisateurs_tab[pid].avatar}' width="50px"></img>`
            }).join('')
        : "";

        $(dst).append(`
        <tr id=tr{id}>
            <td id=id{id}>${u.id}</td>
            <td id=avatar${u.id}>
                <img src="${u.avatar}" width=100px/>
            </td>
            <td id=nom${u.id}>${u.nom}
                <td>
                    Est partisan de ${html}
                </td>
            </td>
        </tr>`
        )
    })
}

function charger_publications(dst, pubs){
    $(dst).empty()

    pubs.items.reverse().forEach(p => {
        publications_tab[p.id] = {
            id: p.id,
            id_utilisateur: p.id_auteur,
            corps: p.body,
            horodatage: p.creation
        }

        auteur = utilisateurs_tab[p.id_auteur]

        $(dst).append(`
        <tr id=tr{id}>
            <td id=id{id}>${p.id}</td>
            <td id=avatar${p.id}>
                <img src="${auteur.avatar}" width="10%"></img>
            </td>
            <td id=corp${p.id}>${p.body}</td>
        </tr>
        `)

        $('#auteur'. id).css("color", "red")
    })
}

async function async_ajax(type, url, header, infos, dst, data){
    let result;
    result = await $.ajax({
        type: type,
        url: url,
        data: data || {},

        beforeSend: function(xhr) {
            xhr.setRequestHeader('Authorization', `${header} ${infos}`);
        },
        
        error: function(){
            if(dst) $(dst).text("Erreur de chargement.") 
            console.log(`ajax error for request ${type} ${url} \n ${header} ${infos} ${dst}`)
        }
    });
    if(result) console.log(`${url} | reuslt =`, result)
    return result
}