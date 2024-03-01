const messagesExchanged = {};
class ChatUpdater {
    static async updateUserList() {
        try {
            const data = await fetch("/chat/get_updated_user_list");
            const updatedUsers = await data.json();
            console.log(updatedUsers)
            return updatedUsers;
        } catch (error) {
            console.error('Error during AJAX request:', error);
        }
    }

    static async renderUpdatedUser(updatedUserString, current_user_string) {
        let current_user;
        const updatedUser = JSON.parse(updatedUserString);
        const current_user_jdon = JSON.parse(current_user_string);
        current_user =  await this.getLoggedUser()
        console.log(updatedUser.id, updatedUser.username)
        console.log(current_user)
        console.log(current_user_jdon.id)
        if (current_user == current_user_jdon.id  ) {
            this.renderUserWind(updatedUser.id, updatedUser.username, updatedUser.avatar)
        }
    }

    static renderUserWind(id, username, avatar) {
        const listUsersContainer = document.getElementById('list-users-container');
        const titleListUsers = document.querySelector('.title-list-users');

        const listItem = document.createElement('li');
        listItem.className = 'item-user';
        listItem.setAttribute('data-user-id', id);
        listItem.setAttribute('data-username', username);
        listItem.setAttribute('onclick', `selectItem(this); openChat('${id}', '${username}')`);
    
        listItem.innerHTML = `
            <img src="${avatar}" class="user-photo" onclick="selectItem(this.parentElement); openChat('${id}', '${username}')">
            <span class="button_name">${username}</span>
        `;
        const existingUser = listUsersContainer.querySelector(`[data-user-id="${id}"]`);
        if (existingUser) {
            console.log(existingUser)
            existingUser.remove();
        }
        listUsersContainer.insertBefore(listItem, titleListUsers.nextSibling);
        
    }
    static async getLoggedUser() {  
        try {
            const response = await fetch('http://localhost:8000/auth/user_id/');
            const data = await response.json();
            return data.user_id;
        } catch (error) {
            console.error("Erro ao obter o nome de usuário:", error);
            return null;
        }
    };
}