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

function deSelectItens() {
  const items = document.querySelectorAll(".item-user");
  items.forEach(function (item) {
    item.classList.remove("selected");
  });
}

function selectItem(item) {
  deSelectItens();
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
