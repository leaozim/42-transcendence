const chatModal = document.getElementById("chat-modal");
const chatButton = document.getElementById("chat-button");
const profileElement = document.getElementById("profile-element");
const userModal = new UserModal();

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
  chatModal.style.display = "block";

  closeModal();
  openChat(userId, username);
}

window.addEventListener("click", function (event) {
  if (event.target == chatModal) {
    closeChat();
    sockets.close();
  } else if (userModal.modal && event.target === userModal.modal) {
    userModal.close();
  } else if (_blockModal.modal && event.target == _blockModal.modal) {
    _blockModal.close();
  }
});

function UserModal() {
  this.modal;

  this.open = async function (username) {
    this.modal = parseHtml(
      await fetchPage(USER_PROFILE_URL, username),
      "div#user-modal",
    );

    document.querySelector("div.col-12").appendChild(this.modal);

    (function () {
      const blockButton = this.modal.querySelector("button#block-button");
      const unblockButton = this.modal.querySelector("button#unblock-button");
      const username = this.modal.querySelector(
        "h1#user-profile-username",
      ).textContent;

      if (blockButton) {
        blockButton.addEventListener("click", async () => {
          await _blockModal.open(
            BLOCK_USER_URL,
            username,
            this.modal.parentNode,
          );

          this.close();
        });
      } else if (unblockButton) {
        unblockButton.addEventListener("click", async () => {
          await _blockModal.open(
            UNBLOCK_USER_URL,
            username,
            this.modal.parentNode,
          );

          this.close();
        });
      }
    }).call(this);

    this.modal.style.display = "block";
  };

  this.close = () => this.modal.remove();
}

async function openUserModal(username) {
  chatModal.style.display = "none";
  await userModal.open(username);
}
