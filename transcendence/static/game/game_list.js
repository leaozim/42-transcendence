document.addEventListener("DOMContentLoaded", (event) => {
  var openModalButton = document.getElementById("game-button");

  // Attach an event listener to it
  openModalButton.addEventListener("click", function () {
    loadModalContent();
  });

  function loadModalContent() {
    fetch("/game/")
      .then((response) => response.text())
      .then((html) => {
        document.querySelector("#modal .modal-content").innerHTML = html;
        var myModal = new bootstrap.Modal(document.getElementById("modal"));
        myModal.show();
      })
      .catch((error) => {
        console.error("Error loading the modal content: ", error);
      });
  }
});
