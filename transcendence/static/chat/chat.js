async function openChat(other_user_id, username = "") {
  const dataRoom = await getDataRoom(other_user_id);
  const dataChat = await getDataChat(dataRoom.room_id);

  setupWebSocket(dataChat.room_id, dataChat.current_user);
  
  clearChatLog();
  
  if (dataChat.messages.length) {
    initializeChatLog(dataChat.current_username, dataChat.messages);
  }
  const blocked = await isBlocked(dataChat.current_user_id, other_user_id)
  appendChatHeader(
    dataChat.other_user_username,
    dataChat.other_user_avatar,
    dataChat.other_user_id,
    blocked
  );

  document.getElementById("no-chat-selected-message").style.display = "none";
  document.getElementById("message-input-container").style.display = "flex";
  const oldChatInput = document.getElementById("chat-message-input");
  if (blocked) {
    oldChatInput.hidden = true;
    return;
  }
  const newChatInput = oldChatInput.cloneNode(true);
  newChatInput.hidden = false;
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
  const chatModal = document.getElementById("chat-modal");

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

  newChatUser.classList.add("item-user");
  newChatUser.setAttribute("data-user-id", id);
  newChatUser.setAttribute("data-username", username);
  newChatUser.setAttribute(
    "onclick",
    `selectItem(this); openChat('${id}', '${username}'); popAlert(${id})`,
  );

  newChatUser.innerHTML = `
      <img src="${avatar}" class="user-photo" onclick="selectItem(this.parentElement); openChat('${id}', '${username}')">
      <span class="button_name">${username}</span>
      <span id="alert-message-${id}" hidden>
        <img src="https://www.shareicon.net/data/128x128/2016/11/15/852842_alert_512x512.png"
          alt="Alert New Message" width="15" height="15">
      </span>
  `;

  return newChatUser;
}

function renderUserWindow({ id, username, avatar }) {
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

function createButtonPlay(otherUserId) {
  const buttonPlay = document.createElement("div");
  buttonPlay.className = "buttons-chat";
  const img = createButtonImage(
    "init game",
    "static/images/chat_button_play.png",
  );
  buttonPlay.appendChild(img);
  buttonPlay.addEventListener("click", function () {
    onCreateGame(otherUserId);
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

function dontOpenOnModal(url) {
  fetch(url)
    .then((response) => response.text())
    .then((html) => {
      console.log("Sucesso");
    })
    .catch((error) => {
      console.error("Error loading the modal content: ", error);
    });
}

function openOnModal(url) {
  fetch(url)
    .then((response) => response.text())
    .then((html) => {
      document.querySelector("#tournament-alias").innerHTML = html;
      initializeFormSubmission();
    })
    .catch((error) => {
      console.error("Error loading the modal content: ", error);
    });
}

function initializeFormSubmission() {
  document
    .querySelector("#tournament-alias-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);

      fetch(this.action, {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
        },
      })
        .then((response) => {
          if (response.ok) {
            return response.text();
          }
          throw new Error("Form submission failed!");
        })
        .then((data) => {
          console.log("Form submitted successfully:", data);
          document.querySelector("#tournament-alias").innerHTML = data;
        })
        .catch((error) => console.error("Error submitting the form:", error));
    });
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

function selectItem(item) {
  var items = document.querySelectorAll(".item-user");
  items.forEach(function (item) {
    item.classList.remove("selected");
  });

  item.classList.add("selected");
}

function onCreateGame(rightPlayerId) {
  console.log(rightPlayerId);
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
