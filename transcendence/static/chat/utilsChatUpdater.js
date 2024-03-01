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

    static async renderUpdatedUser(updatedUserString, currentUserString) {
        let loggedInUserId;
        const updatedUserInfo = JSON.parse(updatedUserString);
        const currentUserInfo = JSON.parse(currentUserString);
    
        loggedInUserId = await this.getLoggedUserId();
        console.log(updatedUserInfo.username);
        console.log(loggedInUserId);
        console.log(currentUserInfo.username);
    
        if (loggedInUserId == currentUserInfo.id) {
            console.log(currentUserInfo.username);
            this.renderUserWindow(updatedUserInfo.id, updatedUserInfo.username, updatedUserInfo.avatar);
        }
    }

    static renderUserWindow(id, username, avatar) {
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
    static async getLoggedUserId() {  
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