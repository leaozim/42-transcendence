const chatModal = document.getElementById("chat-modal");
const chatButton = document.getElementById("chat-button");
const profileElement = document.getElementById("profile-element");
const userModal = document.getElementById("user-modal");

function Sockets() {
  this.chatSocket;
  this.infoSocket;

  (async function () {
    const response = await fetch("/user/");
    const data = await response.json();
    const url = `ws://${window.location.host}/ws/chat_update/${data.id}`;

    this.infoSocket = new WebSocket(url);

    this.infoSocket.onmessage = async (event) => {
      const parseNestedJson = (_, value) => {
        try {
          return JSON.parse(value);
        } catch (error) {
          return value;
        }
      };

      const userNotification = JSON.parse(
        await event.data.text(),
        parseNestedJson,
      ).data;

      renderUserWindow(
        userNotification.id,
        userNotification.username,
        userNotification.avatar,
      );
    };
  }).call(this);
}

Sockets.prototype.add = function (socket) {
  this.close();

  this.chatSocket = socket;
};

Sockets.prototype.close = function () {
  if (this.chatSocket) {
    this.chatSocket.close();
  }
};

const sockets = new Sockets();

if (chatButton) {
  chatButton.addEventListener("click", function () {
    chatModal.style.display = "block";
  });
}
function openChatScreen(userId, username) {
  var chatModal = document.getElementById("chat-modal");

  chatModal.style.display = "block";

  openChat(userId, username);
}

window.addEventListener("click", function (event) {
  if (event.target == chatModal) {
    chatModal.style.display = "none";
    deSelectItens();
    sockets.close();
  }
  if (event.target === userModal) {
    userModal.style.display = "none";
  }
});

document.addEventListener("DOMContentLoaded", function () {
  profileElement.addEventListener("click", function (event) {
    if (profileElement) {
      document.dispatchEvent(new Event("showProfileModal"));
    }
  });
});

function openUserModal(username) {
  const usernameElement = document.getElementById("user-profile-username");
  usernameElement.textContent = username;
  userModal.style.display = "block";
  chatModal.style.display = "none";
  sockets.close();
}
