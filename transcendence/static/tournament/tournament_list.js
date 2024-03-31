var openModalButton = document.getElementById("tournament-button");
openModalButton.addEventListener("click", function (e) {
  e.preventDefault();

  const xhr = new XMLHttpRequest();

  xhr.open("POST", "/create_tournament/");

  const form = new FormData(document.getElementById("create_tournament_form"));

  xhr.send(form);

  xhr.onreadystatechange = () => {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
        document.querySelector("#modal .modal-content").innerHTML =
          xhr.responseText;
        var myModal = new bootstrap.Modal(document.getElementById("modal"));
        myModal.show();
      } else {
        throw new Error(`${xhr.responseText}`);
      }
    }
  };
});
