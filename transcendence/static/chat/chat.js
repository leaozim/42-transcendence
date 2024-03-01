const chatLog = document.querySelector('#chat-log');
let otherUser; 
let lastMessageSender = null;

async function openChat(userId, username) {
	if (window.chatSocket) {
        chatSocket.close();
    }

	chatLog.innerHTML = '';
	const dataRoom  = await getDataRoom(userId);
	const dataChat = await getDataChat(dataRoom.room_id);

	await setupWebSocket(dataChat.room_id, dataChat.current_user);
	initializeChatLog(dataChat.current_user, dataChat.messages);
	appendChatHeader(dataChat.other_user_username, dataChat.other_user_avatar)
	otherUser = dataChat;
	document.getElementById('no-chat-selected-message').style.display = 'none';
	document.getElementById('message-input-container').style.display = 'flex';
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

function addReceivedMessage(currentUser, sender, message, userAvatar) {
	const messageElement = document.createElement('div')
	const avatarElement = document.createElement('img');
	const textElement = document.createElement('p');
	const divImgElement = document.createElement('div')

	if (sender === currentUser) {
		messageElement.className = 'sent-message';
	}
	else {
		if (sender != lastMessageSender) {
			userAvatar ? userAvatar : 'https://res.cloudinary.com/dw9xon1xs/image/upload/v1706288572/arya2_lr9qcd.png'; 
			avatarElement.src = userAvatar;
			avatarElement.alt = 'Avatar';
			textElement.className =  'special-style';

		}
		divImgElement.className = 'user-photo';
		messageElement.className = 'received-message';
		divImgElement.appendChild(avatarElement)
		messageElement.appendChild(divImgElement);
	}

	const clickableMessage = makeLinksClickable(message);
    textElement.innerHTML = clickableMessage;
	messageElement.appendChild(textElement);
	chatLog.appendChild(messageElement);
	messageElement.scrollIntoView({ behavior: 'smooth', block: 'end', inline: 'nearest' });

	lastMessageSender = sender;
}

function initializeChatLog(current_user, messages) {
	let lastUser = "";
	
	messages.forEach((item) => {
		const isCurrentUser = item.user === current_user;
		const isUserChange = lastUser !== item.user || lastUser === '';
		const clickableMessage = makeLinksClickable(item.content);
		chatLog.innerHTML +=`
			<div> 
				${ isCurrentUser
					? `
						<div class="sent-message">
							<p class="${isUserChange ? 'special-style' : ''}">${clickableMessage}</p>
						</div>
					`
					: `
						<div class="received-message">
						  <div class="user-photo">
							${
								isUserChange
								? `<img src="${item.avatar}" alt="${item.user}" >` 
								: '<div></div>'
							}
						  </div>
						  <p class="${isUserChange ? 'special-style' : ''}">${clickableMessage}</p>
						</div>
					`
				}
			</div>
		`;
		lastUser = item.user;
	  })
  }

document.addEventListener('DOMContentLoaded', function() {
  	document.getElementById('chat-message-input').addEventListener('keydown', function(event) {

		if (event.key === 'Enter') {
			sendMessage();
			event.preventDefault(); 
		}
  });
});

function selectItem(item) {
	var items = document.querySelectorAll('.item-user');
	items.forEach(function (item) {
		item.classList.remove('selected');
	});

	item.classList.add('selected');
} 

function makeLinksClickable(message) {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    const messageWithClickableLinks = message.replace(urlRegex, '<a href="$1" target="_blank">$1</a>');
    return messageWithClickableLinks;
}


function onCreateGame(rightPlayerId) {
	if (!rightPlayerId || isNaN(rightPlayerId)) {
		console.error('Invalid user ID for the right player:', rightPlayerId);
		return;
	}
  
	fetch("/game/create_game/" + rightPlayerId)
		.then(response => response.json())
		.then(data => {
			window.location.pathname = '/game/' + data.room_id + '/';
		})
		.catch(error => {
			console.error('Error creating game:', error);
		});
  }