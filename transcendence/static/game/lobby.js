// Home page: keeps the "open games" panel (challenges and games in progress)
// up to date. The server pings /ws/lobby/ whenever one of the user's games
// changes; the panel is then reloaded from /game/open/.
(function () {
  const container = document.getElementById("open-games");
  if (!container) {
    return;
  }

  function csrfToken() {
    const cookie = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith("csrftoken="));
    return cookie ? decodeURIComponent(cookie.substring("csrftoken=".length)) : "";
  }

  // Requests cut short by leaving the page (e.g. to join a game) are not errors.
  let leaving = false;
  window.addEventListener("beforeunload", () => {
    leaving = true;
  });

  async function refresh() {
    try {
      const response = await fetch(container.dataset.url, { credentials: "same-origin" });
      if (response.ok) {
        container.innerHTML = await response.text();
      }
    } catch (e) {
      if (!leaving) {
        console.error("Could not refresh the open games:", e);
      }
    }
  }

  let reconnecting = false;

  function connect() {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws/lobby/`);
    socket.onmessage = refresh;
    socket.onopen = () => {
      if (reconnecting) {
        refresh(); // catch up on anything missed while disconnected
      }
    };
    socket.onclose = () => {
      reconnecting = true;
      setTimeout(connect, 3000);
    };
  }
  connect();

  // "Cancel" / "Decline" buttons.
  container.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-cancel-game]");
    if (!button) {
      return;
    }
    button.disabled = true;
    await fetch(button.dataset.cancelGame, {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": csrfToken() },
    });
    refresh();
  });
})();
