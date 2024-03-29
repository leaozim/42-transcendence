async function openChat(other_user_id, username = "") {
  const dataRoom = await getDataRoom(other_user_id);
  const dataChat = await getDataChat(dataRoom.room_id);
  const oldChatInput = document.getElementById("chat-message-input");
  setupWebSocket(dataChat.room_id, dataChat.current_user);

  clearChatLog();

  if (dataChat.messages.length) {
    initializeChatLog(dataChat.current_username, dataChat.messages);
  }
  appendChatHeader(dataChat.other_user_username, dataChat.other_user_avatar);

  document.getElementById("no-chat-selected-message").style.display = "none";
  document.getElementById("message-input-container").style.display = "flex";

  const newChatInput = oldChatInput.cloneNode(true);

  oldChatInput.parentNode.replaceChild(newChatInput, oldChatInput);
  oldChatInput.remove();

  newChatInput.addEventListener("keydown", function (event) {
    event.stopImmediatePropagation();
    if (event.key === "Enter") {
      sendMessage();
    }
  });
}

function clearChatLog() {
  const chatLog = document.getElementById("chat-log");

  chatLog.innerHTML = "";
}

function closeChat() {
  const chatInputDiv = document.getElementById("message-input-container");
  const paragraphNoChat = document.getElementById("no-chat-selected-message");

  paragraphNoChat.style.display = "block";
  chatInputDiv.style.display = "none";
  chatModal.style.display = "none";
  removeExistingChatHeader();
  deSelectItens();
  clearChatLog();
}

function addSendedMessage(message) {
  const chatLog = document.getElementById("chat-log");
  const messageHTML = createMessageHtml(MessageType.sent, message, true);

  chatLog.insertAdjacentHTML("beforeend", messageHTML);
}

async function sendMessage() {
  const input = document.getElementById("chat-message-input");
  const message = input.value.trim();

  input.value = "";

  if (message.length) {
    if (
      sockets.chatSocket &&
      sockets.chatSocket.readyState === WebSocket.OPEN
    ) {
      await sockets.chatSocket.send(JSON.stringify({ message: message }));
    }

    addSendedMessage(message);
  }
}

function createNewChatUser(id, username, avatar) {
  const newChatUser = document.createElement("li");

  newChatUser.className = "item-user";
  newChatUser.setAttribute("data-user-id", id);
  newChatUser.setAttribute("data-username", username);
  newChatUser.setAttribute(
    "onclick",
    `selectItem(this); openChat('${id}', '${username}')`,
  );

  newChatUser.innerHTML = `
      <img src="${avatar}" class="user-photo" onclick="selectItem(this.parentElement); openChat('${id}', '${username}')">
      <span class="button_name">${username}</span>`;

  return newChatUser;
}

function renderUserWindow(id, username, avatar) {
  const user = document.querySelector(`li[data-user-id="${id}"]`);

  if (!user) {
    document
      .querySelector("ul.list-users")
      .appendChild(createNewChatUser(id, username, avatar));
  }
}

async function getDataRoom(userId) {
  if (!userId || isNaN(userId)) {
    console.error("Invalid user ID:", userId);
  } else {
    try {
      const data = await fetch("/chat/create_or_open_chat/" + userId);
      const response = await data.json();

      return response;
    } catch (error) {
      console.error("Error during AJAX request:", error);
    }
  }
}

async function getDataChat(roomId) {
  try {
    const data = await fetch("/chat/" + roomId);
    const response = await data.json();
    return response;
  } catch (error) {
    console.error("Error during AJAX request:", error);
  }
}

function createButtonsContainer(buttonBlock, buttonPlay) {
  const buttonsContainer = document.createElement("div");
  buttonsContainer.id = "buttons-container";
  buttonsContainer.appendChild(buttonBlock);
  buttonsContainer.appendChild(buttonPlay);
  return buttonsContainer;
}
function createButtonBlock() {
  const buttonBlock = document.createElement("div");
  buttonBlock.className = "buttons-chat";
  const img = createButtonImage(
    "unblocked user",
    "static/images/chat_button_unblocked.png",
  );
  buttonBlock.appendChild(img);
  return buttonBlock;
}

function createButtonPlay() {
  const buttonPlay = document.createElement("div");
  buttonPlay.className = "buttons-chat";
  const img = createButtonImage(
    "init game",
    "static/images/chat_button_play.png",
  );
  buttonPlay.appendChild(img);
  buttonPlay.addEventListener("click", function () {
    onCreateGame(otherUser.other_user_id);
  });
  return buttonPlay;
}

function createButtonImage(title, src) {
  const img = document.createElement("img");
  img.title = title;
  img.setAttribute("src", src);
  return img;
}

function createUsernameElement(otherUserUsername, userPhoto) {
  const usernameElement = document.createElement("h2");
  usernameElement.textContent = otherUserUsername;

  const divProfileElement = document.createElement("div");
  const divImgElement = document.createElement("div");
  divImgElement.className = "user-photo";
  divProfileElement.id = "profile-element";

  divProfileElement.addEventListener("click", function () {
    openUserModal(otherUserUsername);
  });

  divImgElement.appendChild(userPhoto);
  divProfileElement.appendChild(divImgElement);
  divProfileElement.appendChild(usernameElement);
  return divProfileElement;
}

function createUserPhoto(otherUserAvatar) {
  const userPhoto = document.createElement("img");
  userPhoto.alt = "Avatar";
  userPhoto.src = otherUserAvatar
    ? otherUserAvatar
    : "https://res.cloudinary.com/dw9xon1xs/image/upload/v1706288572/arya2_lr9qcd.png";
  return userPhoto;
}

function removeExistingChatHeader() {
  const existingChatHeader = document.querySelector(".chat-header");
  if (existingChatHeader) {
    existingChatHeader.remove();
  }
}

function createChatHeader() {
  const chatHeader = document.createElement("header");
  chatHeader.className = "chat-header";
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
    const buttonsContainer = createButtonsContainer(buttonBlock, buttonPlay);
    chatHeader.appendChild(buttonsContainer);
  }
  document.getElementById("header-container").appendChild(chatHeader);
}

function selectItem(item) {
  var items = document.querySelectorAll(".item-user");
  items.forEach(function (item) {
    item.classList.remove("selected");
  });

  item.classList.add("selected");
}

function onCreateGame(rightPlayerId) {
  if (!rightPlayerId || isNaN(rightPlayerId)) {
    console.error("Invalid user ID for the right player:", rightPlayerId);
    return;
  }

  fetch("/game/create_game/" + rightPlayerId)
    .then((response) => response.json())
    .then((data) => {
      window.location.pathname = "/game/" + data.room_id + "/";
    })
    .catch((error) => {
      console.error("Error creating game:", error);
    });
}
