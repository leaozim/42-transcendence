const chatButton = document.getElementById("chat-button");
const chatModal = document.getElementById("chat-modal");

chatButton.addEventListener("click", function () {
  chatModal.style.display = "block";
});

window.addEventListener("click", function (event) {
  if (event.target == chatModal) {
    chatModal.style.display = "none";
  }
});
