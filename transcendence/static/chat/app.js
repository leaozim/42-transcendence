const chatModal = document.getElementById("chat-modal");
const chatButton = document.getElementById("chat-button");
const profileElement = document.getElementById("profile-element");
const userModal = new UserModal();

if (chatButton) {
  chatButton.addEventListener("click", function () {
    chatModal.style.display = "block";
  });
}

function openChatScreen(userId, username) {
  chatModal.style.display = "block";

  openChat(userId, username);
}

window.addEventListener("click", function (event) {
  if (event.target == chatModal) {
    chatModal.style.display = "none";
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
