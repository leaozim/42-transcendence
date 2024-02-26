const chatModal = document.getElementById("chat-modal");
const chatButton = document.getElementById("chat-button");
const profileElement = document.getElementById('profile-element');

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

document.addEventListener("DOMContentLoaded", function () {

  console.log("DOMContentLoaded foi disparado");
  console.log(profileElement)
  profileElement.addEventListener("click", function (event) {   
    if (profileElement) {
          console.log("aaaaaaaaaaaaa foi disparado");

      document.dispatchEvent(new Event('showProfileModal'));
    }
  });

});

const userModal = document.getElementById("user-modal");

  function openUserModal(username) {
    const usernameElement = document.getElementById("user-profile-username");
  
    usernameElement.textContent = username;
  
    userModal.style.display = "block";
    chatModal.style.display = "none";
  }

  
  window.addEventListener("click", function (event) {
    if (event.target === userModal) {
        userModal.style.display = "none"; 
    }
});