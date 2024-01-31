const profileButton = document.getElementById("profile-button");
const profileModal = document.getElementById("profile-modal");

profileButton.addEventListener("click", function () {
  profileModal.style.display = "block";
});

window.addEventListener("click", function (event) {
  if (event.target == profileModal) {
    profileModal.style.display = "none";
  }
});
