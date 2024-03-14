const chatModal = document.getElementById("chat-modal");
const chatButton = document.getElementById("chat-button");
const profileElement = document.getElementById("profile-element");
const userModal = document.getElementById("user-modal");

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
  } else if (event.target === userModal) {
    userModal.style.display = "none";
  } else if (_blockModal.modal && event.target == _blockModal.modal) {
    _blockModal.close();
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
}

userModal
  .querySelector("button#block-button")
  .addEventListener("click", async () => {
    const usernameElement = userModal.querySelector(
      "h1#user-profile-username",
    ).textContent;
    await _blockModal.open(usernameElement, userModal.parentNode);

    userModal.style.display = "none";
  });
