function setupWebSocket(roomId, currentUser) {
	const base_url = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/chat/' + roomId + '/';
	chatSocket = new WebSocket(base_url);
	chatSocket.onmessage = (event) => {
		const parsed = JSON.parse(event.data);
		addReceivedMessage(currentUser, parsed.username, parsed.message, parsed.user_avatar, parsed.users);
	};
}

async function sendMessage() {
	const messageInputDom = document.getElementById('chat-message-input');
	const message = messageInputDom.value.trim();

	if (message !== '') {
		
        if (window.chatSocket) {
            window.chatSocket.send(JSON.stringify({
                'message': message,
            }));
        }		
		ChatUpdater.renderUserWindow(otherUser.other_user_id, otherUser.other_user_username, otherUser.other_user_avatar)
	}
	messageInputDom.value = '';

}