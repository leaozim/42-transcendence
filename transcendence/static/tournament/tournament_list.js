var openModalButton = document.getElementById("tournament-button");
openModalButton.addEventListener("click", function (e) {
  e.preventDefault();

  const xhr = new XMLHttpRequest();

  xhr.open("POST", "/create_tournament/");

  const form = new FormData(document.getElementById("create_tournament_form"));

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

  xhr.send(form);
});

function handleButtonClick(userId) {
  var button = document.getElementById("tournament-invite-" + userId);

  if (button) {
    button.hidden = true;
    button.style.display = "none";
    sendTournamentInvitation(userId);
  } else {
    console.error("Botão não encontrado");
  }
}

async function sendTournamentInvitation(userId) {
  const xhr = new XMLHttpRequest();

  xhr.open("POST", "/create_tournament/");
  const data = await window.cookieStore.get("csrftoken");
  xhr.setRequestHeader("X-CSRFToken", data.value);
  const form = new FormData(
    document.getElementById(`form_tournament_${userId}`),
  );

  form.set("user_id", userId);

  xhr.onreadystatechange = () => {
    if (xhr.readyState === 4) {
      if (xhr.status === 200) {
      } else {
        console.error("Erro ao enviar convite:", xhr.statusText);
      }
    }
  };

  xhr.send(form);
}
