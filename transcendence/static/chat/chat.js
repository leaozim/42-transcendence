let chatLog = document.querySelector('#chat-log');
let otherUser; 
let lastMessageSender = null;
let chat_id = null;
async function openChat(userId, username) {
	chatLog.innerHTML = '';
	const dataRoom  = await getDataRoom(userId);
	const dataChat = await getDataChat(dataRoom.room_id);

	// await setupWebSocket(dataChat.room_id, dataChat.current_user);
	initializeChatLog(dataChat.current_user, dataChat.messages);
	appendChatHeader(dataChat.other_user_username, dataChat.other_user_avatar)
	document.getElementById('no-chat-selected-message').style.display = 'none';
	document.getElementById('message-input-container').style.display = 'flex';

	let currentUserId  = dataChat.current_user_id;
	let otherUserId = dataChat.other_user_id;
	let otherUserUsername = dataChat.other_user_username;
	let otherUserAvatar = dataChat.other_user_avatar;
	let roomId = dataRoom.room_id;
	let chatMessageImput = document.getElementById('chat-message-input')
	chatMessageImput.removeEventListener('keydown', sendMessage)
	document.getElementById('chat-message-input').addEventListener('keydown', function(event) {

		if (event.key === 'Enter') {
			sendMessage(roomId, currentUserId, otherUserId, otherUserUsername, otherUserAvatar)
		}
	});

  
}

async function sendMessage(roomId, currentUserId, otherUserId, otherUserUsername, otherUserAvatar) {
	const messageInputDom = document.getElementById('chat-message-input');
	const message = messageInputDom.value.trim();
	console.log(" aaaaaaaaaaaaaaaaaaaaa", currentUserId)
	if (message !== '') {
        if (window.chatSocketUpdate && window.chatSocketUpdate.readyState === WebSocket.OPEN) {

            window.chatSocketUpdate.send(JSON.stringify({
				'chat_id': roomId,
                'message': message,
				'user_id': currentUserId,
				'other_user_id': otherUserId,
				'other_user_avatar': otherUserAvatar,
				'other_user_username': otherUserUsername

            }));
			// ChatUpdater.renderUserWindow(otherUser.other_user_id, otherUser.other_user_username, otherUser.other_user_avatar)
        }		
	}
	messageInputDom.value = '';

}

async function getDataRoom(userId) {
	if (!userId || isNaN(userId)) {
		console.error('Invalid user ID:', userId);
	} 
	else {
		try {
			const data = await fetch("/chat/create_or_open_chat/" + userId)
			const response = await data.json();
			return response;
		}
		catch (error) {
			console.error('Error during AJAX request:', error);
		}
	}
}

async function getDataChat(roomId) {
  	try {
		const data = await fetch("/chat/" + roomId);
		const response = await data.json();
		return response;
	} 
	catch (error) {
		console.error('Error during AJAX request:', error);
	}
}

