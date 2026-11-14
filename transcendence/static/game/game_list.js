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

		// Function to close the modal
		window.closeModal = function() {
			myModal.hide();
		}
	})
      .catch((error) => {
        console.error("Error loading the modal content: ", error);
      });
  }
});

function gameCsrfToken() {
  const cookie = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith("csrftoken="));
  return cookie ? decodeURIComponent(cookie.substring("csrftoken=".length)) : "";
}

// Time and points chosen in the game modal (server defaults when it is closed).
function chosenGameSettings() {
  const data = new FormData();
  const form = document.getElementById("game-settings");
  if (form) {
    data.set("minutes", form.elements.minutes.value);
    data.set("score", form.elements.score.value);
  }
  return data;
}

async function startGame(url) {
  const errorBox = document.querySelector("#game-settings .game-settings-error");
  try {
    const response = await fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": gameCsrfToken(), Accept: "application/json" },
      body: chosenGameSettings(),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || response.statusText);
    }
    window.location.pathname = `/game/${data.room_id}/`;
  } catch (error) {
    if (errorBox) {
      errorBox.textContent = error.message;
      errorBox.hidden = false;
    }
    console.error("Error creating game:", error);
  }
}

// Challenge another player (game modal and the chat's "play" button).
function onCreateGame(rightPlayerId) {
  if (!rightPlayerId || isNaN(rightPlayerId)) {
    console.error("Invalid user ID for the right player:", rightPlayerId);
    return;
  }
  startGame(`/game/create_game/${rightPlayerId}/`);
}

// "Play against the computer" (the settings form of the game modal).
document.addEventListener("submit", (event) => {
  if (event.target.id === "game-settings") {
    event.preventDefault();
    startGame(event.target.action);
  }
});
