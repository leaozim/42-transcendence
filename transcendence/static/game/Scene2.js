class Scene2 extends Phaser.Scene {
  constructor() {
    super("playGame");
    const receiveSocketUrl = `wss://${window.location.host}/ws/game/broadcast/${room_id}/`;
    this.receiveSocket = new WebSocket(receiveSocketUrl);

    const playerIds = {
      leftPlayerId: leftPlayer,
      rightPlayerId: rightPlayer,
    };

    this.receiveSocket.onopen = () => {
      this.receiveSocket.send(JSON.stringify(playerIds));
    };
  }

  async getThisUser() {
    const response = await fetch(GET_AUTH_USER_ID);
    const data = await response.json();
    return data.user_id;
  }

  async create() {
    // descobre quem é o usuário para fazer verificações sobre ser leftPlayer, rightPlayer ou só espectador
    this.i_am = await this.getThisUser();

    // Mensagem para indicar que o jogo está parado pois precisa de todos os jogadores conectados
    this.waitingText = this.add
      .text(
        this.cameras.main.centerX,
        this.cameras.main.centerY - 50,
        "Waiting for all the players to connect",
        {
          font: "24px Arial",
          fill: "#ffffff",
        },
      )
      .setOrigin(0.5);

    // Se o evento de dados indicar game over, direciona para Scene3
    if (this.eventData && this.eventData.winner) {
      this.scene.start("GameOver");
      return;
    }

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

    // prepara um eventData zerado. Conforme o backend processar as informações, este eventData será atualizado
    this.eventData = {
      ball_x: this.ball.x,
      ball_y: this.ball.y,
      left_player_position_x: this.left_paddle.x,
      left_player_position_y: this.left_paddle.y,
      right_player_position_x: this.right_paddle.x,
      right_player_position_y: this.right_paddle.y,
      score: [0, 0],
    };

    this.receiveSocket.onmessage = (event) => {
      this.eventData = JSON.parse(event.data);

      // Troca para a próxima Scene, enviando nome do jogador vencedor para ser exibido na tela
      if (this.eventData.winner !== undefined) {
        this.scene.start("GameOver", { winner: this.eventData.winner });
      }

      // Após 2 jogadores se conectarem, o jogo começa então essa mensagem é removida da tela
      if (this.eventData.connected && this.eventData.connected.length === 2) {
        this.waitingText.destroy();
      }
    };
  }

  async update() {
    if (this.eventData && this.eventData.winner === undefined) {
      // Ele sempre tenta atualizar o score, mesmo quando não há novos pontos
      // O motivo disso é que tentar atualizar só quando existe um ponto pode causar
      // pontos que demoram para serem atualizados ou que só são atualizados
      // após mais alguns pontos
      this.player_left.score = this.eventData.score[PLAYER_LEFT];
      this.player_left.updateScoreText();
      this.player_right.score = this.eventData.score[PLAYER_RIGHT];
      this.player_right.updateScoreText();

      // Move todos os objetos da cena conforme os dados que foram recebidos do back
      this.ball.move(this.eventData.ball_x, this.eventData.ball_y);
      this.left_paddle.move(
        this.eventData.left_player_position_x,
        this.eventData.left_player_position_y,
      );
      this.right_paddle.move(
        this.eventData.right_player_position_x,
        this.eventData.right_player_position_y,
      );

      // Envia dados de input pro backend. Ficará repetindo os mesmos resultados acima até que receba uma nova resposta
      // Ou seja, se demorar muitos ticks do update para receber uma resposta, todas as linhas acima
      // vão ficar se repetindo, garantindo que o jogo não quebre, mas como usa position e não velocity,
      // a tela vai apresentar lag
      this.receiveSocket.send(
        JSON.stringify({
          type: "end_loop",
          left_player_velocity: this.left_paddle.velocity_to_dict(),
          right_player_velocity: this.right_paddle.velocity_to_dict(),
          logged_player: this.i_am,
        }),
      );
    }
  }
}

