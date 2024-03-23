let chatLog = document.querySelector('#chat-log');
let otherUser;
let lastMessageSender = null;
let chat_id = null;
async function openChat(other_user_id, username = "") {
  chatLog.innerHTML = '';
  const dataRoom = await getDataRoom(other_user_id);
  const dataChat = await getDataChat(dataRoom.room_id);
  // await setupWebSocket(dataChat.room_id, dataChat.current_user);
  initializeChatLog(dataChat.current_user, dataChat.messages);
  appendChatHeader(dataChat.other_user_username, dataChat.other_user_avatar)
  document.getElementById('no-chat-selected-message').style.display = 'none';
  document.getElementById('message-input-container').style.display = 'flex';

  let currentUserId = dataChat.current_user_id;
  let otherUserId = dataChat.other_user_id;
  let otherUserUsername = dataChat.other_user_username;
  let otherUserAvatar = dataChat.other_user_avatar;
  let roomId = dataRoom.room_id;
  let oldChatInput = document.getElementById('chat-message-input')
  let newChatInput = oldChatInput.cloneNode(true)
  newChatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      sendMessage(roomId, currentUserId, otherUserId, otherUserUsername, otherUserAvatar)
    }
  });
  oldChatInput.parentNode.replaceChild(newChatInput, oldChatInput);
  oldChatInput.remove();
}

async function sendMessage(roomId, currentUserId, otherUserId, otherUserUsername, otherUserAvatar) {
  const messageInputDom = document.getElementById('chat-message-input');
  const message = messageInputDom.value.trim();
  if (message !== '') {
    if (window.chatSocketUpdate && window.chatSocketUpdate.readyState === WebSocket.OPEN) {

      window.chatSocketUpdate.send(JSON.stringify({
        'type': "chat",
        'chat_id': roomId,
        'message': message,
        'user_id': currentUserId,
        'other_user_id': otherUserId,
        'other_user_avatar': otherUserAvatar,
        'other_user_username': otherUserUsername

      }));
      renderUserWindow(otherUserId, otherUserUsername, otherUserAvatar)
    }
  }
  messageInputDom.value = '';
  const dataChat = await getDataChat(roomId);
  initializeChatLog(dataChat.current_user, dataChat.messages);
}

function renderUserWindow(id, username, avatar) {
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
  if (!existingUser) {
    document.querySelector('ul.list-users').appendChild(listItem);
  }
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

function initializeChatLog(current_user, messages) {
  let lastUser = "";

  messages.forEach((item) => {
    const isCurrentUser = item.user === current_user;
    const isUserChange = lastUser !== item.user || lastUser === '';
    const clickableMessage = makeLinksClickable(item.content);
    chatLog.innerHTML += `
			<div> 
				${isCurrentUser
        ? `
						<div class="sent-message">
							<p class="${isUserChange ? 'special-style' : ''}">${clickableMessage}</p>
						</div>
					`
        : `
						<div class="received-message">
						  <div class="user-photo">
							${isUserChange
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

function makeLinksClickable(message) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  // const messageWithClickableLinks = message.replace(urlRegex, '<a href="$1" target="_blank" style="color: black;">$1</a>');
  // return messageWithClickableLinks;
  return message
}

function createButtonsContainer(buttonBlock, buttonPlay) {
  const buttonsContainer = document.createElement('div');
  buttonsContainer.id = 'buttons-container';
  buttonsContainer.appendChild(buttonBlock);
  buttonsContainer.appendChild(buttonPlay);
  return buttonsContainer;
}
function createButtonBlock() {
  const buttonBlock = document.createElement('div');
  buttonBlock.className = 'buttons-chat';
  const img = createButtonImage('unblocked user', 'static/images/chat_button_unblocked.png');
  buttonBlock.appendChild(img);
  return buttonBlock;
}

function createButtonPlay() {
  const buttonPlay = document.createElement('div');
  buttonPlay.className = 'buttons-chat';
  const img = createButtonImage('init game', 'static/images/chat_button_play.png');
  buttonPlay.appendChild(img);
  buttonPlay.addEventListener('click', function() {
    onCreateGame(otherUser.other_user_id);
  });
  return buttonPlay;
}

function createButtonImage(title, src) {
  const img = document.createElement('img');
  img.title = title;
  img.setAttribute('src', src);
  return img;
}

function createUsernameElement(otherUserUsername, userPhoto) {
  const usernameElement = document.createElement('h2');
  usernameElement.textContent = otherUserUsername;

  const divProfileElement = document.createElement('div');
  const divImgElement = document.createElement('div');
  divImgElement.className = 'user-photo';
  divProfileElement.id = 'profile-element';

  divProfileElement.addEventListener('click', function() {
    openUserModal(otherUserUsername);
  });

  divImgElement.appendChild(userPhoto);
  divProfileElement.appendChild(divImgElement);
  divProfileElement.appendChild(usernameElement);
  return divProfileElement
}
function createUserPhoto(otherUserAvatar) {
  const userPhoto = document.createElement('img');
  userPhoto.alt = 'Avatar';
  userPhoto.src = otherUserAvatar ? otherUserAvatar : 'https://res.cloudinary.com/dw9xon1xs/image/upload/v1706288572/arya2_lr9qcd.png';
  return userPhoto;
}
function removeExistingChatHeader() {
  const existingChatHeader = document.querySelector('.chat-header');
  if (existingChatHeader) {
    existingChatHeader.remove();
  }
}
function createChatHeader() {
  const chatHeader = document.createElement('header');
  chatHeader.className = 'chat-header';
  removeExistingChatHeader();
  return chatHeader;
}
function appendChatHeader(otherUserUsername, otherUserAvatar, parentElement) {
  const chatHeader = createChatHeader();

  if (otherUserUsername) {
    const userPhoto = createUserPhoto(otherUserAvatar);

    divProfileElement = createUsernameElement(otherUserUsername, userPhoto);
    chatHeader.appendChild(divProfileElement);
    const buttonBlock = createButtonBlock();
    const buttonPlay = createButtonPlay();
    const buttonsContainer = createButtonsContainer(buttonBlock, buttonPlay)
    chatHeader.appendChild(buttonsContainer);

  }
  document.getElementById('header-container').appendChild(chatHeader);
}

function selectItem(item) {
  var items = document.querySelectorAll('.item-user');
  items.forEach(function(item) {
    item.classList.remove('selected');
  });

  item.classList.add('selected');
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
