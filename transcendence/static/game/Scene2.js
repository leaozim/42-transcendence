// Remaining time as m:ss.
function formatClock(seconds) {
  if (seconds === null || seconds === undefined) {
    return "";
  }
  const total = Math.ceil(seconds);
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`;
}

class Scene2 extends Phaser.Scene {
  constructor() {
    super("playGame");
    const receiveSocketUrl = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws/game/broadcast/${room_id}/`;
    this.receiveSocket = new WebSocket(receiveSocketUrl);
    // Waiting room (Ready button, countdown) shown over the game until play begins.
    this.lobby = new GameLobby(this.receiveSocket);
  }

  async getThisUser() {
    const response = await fetch("/auth/user_id/");
    const data = await response.json();
    return data.user_id;
  }

  async create() {
    // descobre quem é o usuário para fazer verificações sobre ser leftPlayer, rightPlayer ou só espectador
    this.i_am = await this.getThisUser();
    this.lobby.setMe(this.i_am);

    // instancia todos os objetos
    this.left_paddle = new Paddle(
      this,
      LEFT_PADDLE_START_POSITION.x,
      LEFT_PADDLE_START_POSITION.y,
      "paddle",
      this.i_am == leftPlayer,
    );
    this.player_left = new Player(
      this,
      this.left_paddle,
      PLAYER_LEFT,
      leftPlayer,
    );
    this.right_paddle = new Paddle(
      this,
      RIGHT_PADDLE_START_POSITION.x,
      RIGHT_PADDLE_START_POSITION.y,
      "paddle",
      this.i_am == rightPlayer,
    );
    this.player_right = new Player(
      this,
      this.right_paddle,
      PLAYER_RIGHT,
      rightPlayer,
    );

    this.ball = new Ball(this, CENTER_OF_SCREEN.x, CENTER_OF_SCREEN.y, "ball");

    // The server runs the game: send the paddle direction only when it changes.
    const sendDirection = (direction) => {
      if (this.receiveSocket.readyState === WebSocket.OPEN) {
        this.receiveSocket.send(JSON.stringify({ type: "input", direction }));
      }
    };
    this.left_paddle.onDirectionChange = sendDirection;
    this.right_paddle.onDirectionChange = sendDirection;

    // Time left, in the middle between the two scores.
    this.clockText = this.add
      .text(CENTER_OF_SCREEN.x, 50, "", { fontFamily: "Arial", fontSize: "28px", color: "#ffffff" })
      .setOrigin(0.5);

    // prepara um eventData zerado. Conforme o backend processar as informações, este eventData será atualizado
    this.eventData = {
      phase: "waiting",
      ball_x: this.ball.x,
      ball_y: this.ball.y,
      left_player_position_x: this.left_paddle.x,
      left_player_position_y: this.left_paddle.y,
      right_player_position_x: this.right_paddle.x,
      right_player_position_y: this.right_paddle.y,
      score: [0, 0],
      time_left: null,
    };

    this.receiveSocket.onmessage = (event) => {
      this.eventData = JSON.parse(event.data);
      this.lobby.update(this.eventData);

      // Troca para a próxima Scene, enviando o resultado para ser exibido na tela
      if (this.eventData.phase === "finished" || this.eventData.phase === "canceled") {
        this.over = true;
        this.scene.start("GameOver", {
          winner: this.eventData.winner,
          result: this.eventData.result,
          winnerId: this.eventData.winner_id,
        });
      }
    };
  }

  update() {
    if (!this.eventData || this.over) {
      return;
    }
    this.player_left.score = this.eventData.score[PLAYER_LEFT];
    this.player_left.updateScoreText();
    this.player_right.score = this.eventData.score[PLAYER_RIGHT];
    this.player_right.updateScoreText();
    this.clockText.setText(formatClock(this.eventData.time_left));

    // Move todos os objetos da cena conforme os dados que foram recebidos do back
    this.ball.move(this.eventData.ball_x, this.eventData.ball_y);
    this.left_paddle.move(this.eventData.left_player_position_x, this.eventData.left_player_position_y);
    this.right_paddle.move(this.eventData.right_player_position_x, this.eventData.right_player_position_y);
  }
}
