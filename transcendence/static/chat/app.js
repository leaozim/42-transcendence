const chatModal = document.getElementById("chat-modal");
const chatButton = document.getElementById("chat-button");

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
  }
});

