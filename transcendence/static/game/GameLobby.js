// Waiting room shown over the game until play begins: who is in the room,
// who is ready, the "Ready" button and the countdown. Updated from the state
// the server broadcasts (see srcs_game/session.py).
class GameLobby {
  constructor(socket) {
    this.socket = socket;
    this.me = null;
    this.element = document.getElementById("game-lobby");
    this.hint = this.element.querySelector(".game-lobby-hint");
    this.countdown = this.element.querySelector(".game-lobby-countdown");
    this.readyButton = document.getElementById("ready-button");
    this.cancelButton = document.getElementById("cancel-game-button");
    this.players = [String(leftPlayer), String(rightPlayer)];
    this.names = [GAME_TEXTS.leftPlayer, GAME_TEXTS.rightPlayer];

    this.readyButton.addEventListener("click", () => {
      this.readyButton.disabled = true;
      this.socket.send(JSON.stringify({ type: "ready" }));
    });

    if (this.cancelButton) {
      this.cancelButton.addEventListener("click", async () => {
        this.cancelButton.disabled = true;
        const response = await fetch(this.cancelButton.dataset.url, {
          method: "POST",
          credentials: "same-origin",
          headers: { "X-CSRFToken": GameLobby.csrfToken() },
        });
        await response.text(); // finish the request before leaving the page
        window.location.href = "/";
      });
    }
  }

  static csrfToken() {
    const cookie = document.cookie.split(";").map((c) => c.trim()).find((c) => c.startsWith("csrftoken="));
    return cookie ? decodeURIComponent(cookie.substring("csrftoken=".length)) : "";
  }

  static format(text, values) {
    return Object.entries(values).reduce((result, [key, value]) => result.replace(`%(${key})s`, value), text);
  }

  setMe(userId) {
    this.me = String(userId);
  }

  update(state) {
    const waiting = state.phase === "waiting" || state.phase === "countdown";
    this.element.hidden = !waiting;
    if (!waiting) {
      return;
    }

    const connected = (state.connected || []).map(String);
    const ready = (state.ready || []).map(String);
    for (const id of this.players) {
      const status = this.element.querySelector(`li[data-player="${id}"] .status`);
      const playerState = ready.includes(id) ? "ready" : connected.includes(id) ? "present" : "absent";
      status.dataset.state = playerState;
      status.textContent = {
        ready: GAME_TEXTS.statusReady,
        present: GAME_TEXTS.statusPresent,
        absent: GAME_TEXTS.statusAbsent,
      }[playerState];
    }

    if (state.phase === "countdown") {
      this.hint.textContent = "";
      this.countdown.hidden = false;
      this.countdown.textContent = GameLobby.format(GAME_TEXTS.countdown, { seconds: state.countdown });
      this.readyButton.hidden = true;
      if (this.cancelButton) {
        this.cancelButton.hidden = true;
      }
      return;
    }

    const mySide = this.players.indexOf(this.me);
    const iAmReady = ready.includes(this.me);
    this.countdown.hidden = true;
    if (this.cancelButton) {
      this.cancelButton.hidden = false;
    }
    this.readyButton.hidden = mySide === -1 || iAmReady;
    if (!iAmReady) {
      this.readyButton.disabled = false; // e.g. the countdown stopped because a player left
    }

    if (mySide === -1) {
      this.hint.textContent = GAME_TEXTS.hintSpectator;
      return;
    }
    const opponent = this.players[1 - mySide];
    const name = this.names[1 - mySide];
    if (!connected.includes(opponent)) {
      this.hint.textContent = GameLobby.format(GAME_TEXTS.hintJoin, { name });
    } else if (iAmReady) {
      this.hint.textContent = GameLobby.format(GAME_TEXTS.hintWaitReady, { name });
    } else if (ready.includes(opponent)) {
      this.hint.textContent = GameLobby.format(GAME_TEXTS.hintOpponentReady, { name });
    } else {
      this.hint.textContent = GAME_TEXTS.hintPressReady;
    }
  }
}
