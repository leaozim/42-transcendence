class Scene2 extends Phaser.Scene {
    constructor() {
      super("playGame");
      const base_url = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/game/' + "{{ room_name }}" + '/';
      this.pongSocket = new WebSocket(base_url);
    }
  
    create() {
        this.left_paddle = new Paddle(this, LEFT_PADDLE_START_POSITION.x, LEFT_PADDLE_START_POSITION.y, "paddle");
        this.player_left = new Player(this, this.left_paddle, PLAYER_LEFT)
        this.right_paddle = new Paddle(this, RIGHT_PADDLE_START_POSITION.x, RIGHT_PADDLE_START_POSITION.y, "paddle");
        this.player_right = new Player(this, this.right_paddle, PLAYER_RIGHT)

        this.paddle_height = this.left_paddle.height;
        this.ball = new Ball(this, CENTER_OF_SCREEN.x, CENTER_OF_SCREEN.y, "ball");
        // this.scoreTextLeft = this.add.text(400, 16, `Player Left: ${this.player_left.getScore()}`, { fontSize: '18px', fill: '#fff' });
        // this.scoreTextRight = this.add.text(580, 16, `Player Right: ${this.player_right.getScore()}`, { fontSize: '18px', fill: '#fff' });
    }

    update() {
        this.ball.move();
        this.left_paddle.move()
        this.left_paddle.hitHorizontalBorders()
        const collisionResultLeft = this.ball.checkPaddleCollision(
          this.left_paddle.x,
          this.left_paddle.y,
          this.paddle_height,
          PLAYER_LEFT
        );
        this.right_paddle.move()
        this.right_paddle.hitHorizontalBorders()

        const collisionResultRight = this.ball.checkPaddleCollision(
          this.right_paddle.x,
          this.right_paddle.y,
          this.paddle_height,
          PLAYER_RIGHT

      );
      if (this.ball.x > CANVAS_WIDTH) {
        this.player_left.incrementScore();
        this.ball.resetBall()
        this.left_paddle.resetPaddle(PLAYER_LEFT)
        this.right_paddle.resetPaddle(PLAYER_RIGHT)
        this.player_left.updateScoreText()
      }

      if (this.ball.x < 0) {
          this.player_right.incrementScore();
          this.ball.resetBall()
          this.right_paddle.resetPaddle(PLAYER_RIGHT)
          this.left_paddle.resetPaddle(PLAYER_LEFT)
          this.player_right.updateScoreText()
      }

      this.pongSocket.send(JSON.stringify({
        ball: { x: this.ball.x, y: this.ball.y },
      }));
  }


}