class Scene2 extends Phaser.Scene {
    constructor() {
      super("playGame");
      console.log('criando game')
      const sendPlayer1Url = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/game/player1/' + room_id + '/';
      const sendPlayer2Url = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/game/player2/' + room_id + '/';
      const receiveSocketUrl = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/game/broadcast/' + room_id + '/';
      this.sendPlayer1Socket = new WebSocket(sendPlayer1Url);
      this.sendPlayer2Socket = new WebSocket(sendPlayer2Url);
      this.receiveSocket = new WebSocket(receiveSocketUrl);
    }

    async getThisUser() {
      const response = await fetch('http://localhost:8000/auth/user_id/');
      const data = await response.json();
      return data.user_id
    }
  
    async create() {
      this.i_am = await this.getThisUser()
      this.senderSocket = (this.i_am==leftPlayer) ? this.sendPlayer1Socket : this.sendPlayer2Socket;
      this.left_paddle = new Paddle(this, LEFT_PADDLE_START_POSITION.x, LEFT_PADDLE_START_POSITION.y, "paddle", (this.i_am==leftPlayer));
      this.player_left = new Player(this, this.left_paddle, PLAYER_LEFT, leftPlayer)
      this.right_paddle = new Paddle(this, RIGHT_PADDLE_START_POSITION.x, RIGHT_PADDLE_START_POSITION.y, "paddle", (this.i_am==rightPlayer));
      this.player_right = new Player(this, this.right_paddle, PLAYER_RIGHT, rightPlayer)
      this.me = (this.i_am==leftPlayer) ? this.player_left : this.player_right

      this.paddle_height = this.left_paddle.height;
      this.ball = new Ball(this, CENTER_OF_SCREEN.x, CENTER_OF_SCREEN.y, "ball");
    }

    async update() {
      this.receiveSocket.onmessage = (event) => {
        console.log('receive data: ', event.data)
        // const data = JSON.parse(event.data);
        // if (data.ball_x !== undefined && data.ball_y !== undefined) {
        //     this.ball.move(data.ball_x, data.ball_y);
        // }
    };
    if (this.senderSocket !== null && this.senderSocket != null) {
      this.senderSocket.send({'cavalinho'});
    }
    //   this.receiveSocket.onmessage = (event) => {
    //     const data = JSON.parse(event.data);

    //     if (data.player) {
    //         const isLeftPlayer = data.player.left === 1;

    //         if (isLeftPlayer) {
    //             console.log("Recebido do jogador esquerdo:");
    //         } else {
    //             console.log("Recebido do jogador direito:");
    //         }

    //         console.log(`Paddle X: ${data.player.paddle.x}`);
    //         console.log(`Paddle Y: ${data.player.paddle.y}`);

    //         // Atualize a posição do paddle conforme necessário
    //         if (isLeftPlayer) {
    //             this.right_paddle.x = data.player.paddle.x;
    //             this.right_paddle.y = data.player.paddle.y;
    //         } else {
    //             this.left_paddle.x = data.player.paddle.x;
    //             this.left_paddle.y = data.player.paddle.y;
    //         }
    //     }
    // };
      //   this.left_paddle.move()
      //   this.left_paddle.hitHorizontalBorders()
      //   const collisionResultLeft = this.ball.checkPaddleCollision(
      //     this.left_paddle.x,
      //     this.left_paddle.y,
      //     this.paddle_height,
      //     PLAYER_LEFT
      //   );
      //   this.right_paddle.move()
      //   this.right_paddle.hitHorizontalBorders()

      //   const collisionResultRight = this.ball.checkPaddleCollision(
      //     this.right_paddle.x,
      //     this.right_paddle.y,
      //     this.paddle_height,
      //     PLAYER_RIGHT

      // );
      // if (this.ball.x > CANVAS_WIDTH) {
      //   this.player_left.incrementScore();
      //   this.ball.resetBall()
      //   this.left_paddle.resetPaddle(PLAYER_LEFT)
      //   this.right_paddle.resetPaddle(PLAYER_RIGHT)
      //   this.player_left.updateScoreText()
      // }

      // if (this.ball.x < 0) {
      //     this.player_right.incrementScore();
      //     this.ball.resetBall()
      //     this.right_paddle.resetPaddle(PLAYER_RIGHT)
      //     this.left_paddle.resetPaddle(PLAYER_LEFT)
      //     this.player_right.updateScoreText()
      // }
  }


}