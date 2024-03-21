const messagesExchanged = {};
class ChatUpdater {
    static async updateUserList() {
        try {
            const data = await fetch("/chat/get_updated_user_list");
            const updatedUsers = await data.json();
            // console.log(updatedUsers)
            return updatedUsers;
        } catch (error) {
            console.error('Error during AJAX request:', error);
        }
    }

    static async renderUpdatedUser(updatedUserString, currentUserString) {
        const updatedUserInfo = JSON.parse(updatedUserString);
        const currentUserInfo = JSON.parse(currentUserString);
        let loggedInUserId;

        loggedInUserId = await this.getLoggedUserId();
        if (loggedInUserId == currentUserInfo.id) {
            console.log(loggedInUserId.username);
            console.log(currentUserInfo.username);

            this.renderUserWindow(updatedUserInfo.id, updatedUserInfo.username, updatedUserInfo.avatar);
        }
    }

    static renderUserWindow(id, username, avatar) {
        const listUsersContainer = document.getElementById('list-users-container');
        const titleListUsers = document.querySelector('.title-list-users');
        console.log(username)
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
        if (!existingUser) {
            const ul = document.querySelector('ul.list-users').appendChild(listItem)
            // existingUser.remove();
        }
        // var userChat;
        // document.querySelectorAll("li").forEach((element) => {
        //     if (element.getAttribute("data-user-id") === id) {
        //         element.remove();
        //     }
        //   });
        // listUsersContainer.insertBefore(listItem, titleListUsers.nextSibling);
        
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