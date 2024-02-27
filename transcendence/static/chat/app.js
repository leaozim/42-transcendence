const chatModal = document.getElementById("chat-modal");
const chatButton = document.getElementById("chat-button");
const profileElement = document.getElementById('profile-element');
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
  // setupWebSocketUpdate()
}

window.addEventListener("click", function (event) {
  if (event.target == chatModal) {
    chatModal.style.display = "none";
  }
  if (event.target === userModal) {
    userModal.style.display = "none"; 
  }
});

document.addEventListener("DOMContentLoaded", function () {
  profileElement.addEventListener("click", function (event) {   
    if (profileElement) {
      document.dispatchEvent(new Event('showProfileModal'));
    }
  });

});


function openUserModal(username) {
  const usernameElement = document.getElementById("user-profile-username");
  usernameElement.textContent = username;
  userModal.style.display = "block";
  chatModal.style.display = "none";
}
