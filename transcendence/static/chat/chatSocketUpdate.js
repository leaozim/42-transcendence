
const base_url_update = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/chat_update/';
chatSocketUpdate = new WebSocket(base_url_update);		
console.log( "entrou no update")

chatSocketUpdate.onopen = (event) => {
    console.log('onopen WebSocket update:', event.data);

    chatSocketUpdate.send(JSON.stringify({
        'cavalinho': 'cavalo manco',

    }));
};

chatSocketUpdate.onmessage = async (event) => {
    console.log('onmessage WebSocket update:', event.data);

    const parsed = JSON.parse(event.data);
    // console.log(parsed.user_list
// )
    updatedUsers = await updateUserList() 
    console.log(parsed)

    renderUpdatedUserList(updatedUsers)

};


async function getLoggedInUsername() {  
	try {
		const response = await fetch('http://localhost:8000/auth/user_id/');
		const data = await response.json();
		return data.user_id;
	} catch (error) {
		console.error("Erro ao obter o nome de usuário:", error);
		return null;
	}
}
async function updateUserList() {
    try {
        const data = await fetch("/chat/get_updated_user_list");
        const updatedUsers = await data.json();
		return updatedUsers;
    } catch (error) {
        console.error('Error during AJAX request:', error);
    }
}
function renderUpdatedUserList(updatedUserList) {

    const listUsersContainer = document.getElementById('list-users-container');
    
    while (listUsersContainer.children.length > 1) {
        listUsersContainer.removeChild(listUsersContainer.lastChild);
    }

    const usersArray = updatedUserList.users_in_chats || [];

    usersArray.forEach(user => {
		if (user.username != user.corrent_user) {
			const listItem = document.createElement('li');
			listItem.className = 'item-user';
			listItem.setAttribute('data-user-id', user.id);
			listItem.setAttribute('data-username', user.username);
			listItem.setAttribute('onclick', `selectItem(this); openChat('${user.id}', '${user.username}')`);

	        listItem.innerHTML = `
				<img src="${user.avatar}" class="user-photo" onclick="selectItem(this.parentElement); openChat('${user.id}', '${user.username}')">
				<span class="botton_name">${user.username}</span>
        	`;

	
            listUsersContainer.appendChild(listItem);
		}

    });
}