class Scene2 extends Phaser.Scene {
    constructor() {
      super("playGame");
      console.log('criando game')
      // const sendPlayer1Url = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/game/player1/' + room_id + '/';
      // const sendPlayer2Url = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/game/player2/' + room_id + '/';
      const receiveSocketUrl = 'ws://' + window.location.hostname + ':' + window.location.port + '/ws/game/broadcast/' + room_id + '/';
      // this.sendPlayer1Socket = new WebSocket(sendPlayer1Url);
      // this.sendPlayer2Socket = new WebSocket(sendPlayer2Url);
      this.receiveSocket = new WebSocket(receiveSocketUrl);
    }

    async getThisUser() {
      const response = await fetch('http://localhost:8000/auth/user_id/');
      const data = await response.json();
      return data.user_id
    }
  
    async create() {
      this.i_am = await this.getThisUser()
      // this.senderSocket = (this.i_am==leftPlayer) ? this.sendPlayer1Socket : this.sendPlayer2Socket;
      this.left_paddle = new Paddle(this, LEFT_PADDLE_START_POSITION.x, LEFT_PADDLE_START_POSITION.y, "paddle", (this.i_am==leftPlayer));
      this.player_left = new Player(this, this.left_paddle, PLAYER_LEFT, leftPlayer)
      this.right_paddle = new Paddle(this, RIGHT_PADDLE_START_POSITION.x, RIGHT_PADDLE_START_POSITION.y, "paddle", (this.i_am==rightPlayer));
      this.player_right = new Player(this, this.right_paddle, PLAYER_RIGHT, rightPlayer)
      this.me = (this.i_am==leftPlayer) ? this.player_left : this.player_right
      
      this.paddle_height = this.left_paddle.height;
      this.ball = new Ball(this, CENTER_OF_SCREEN.x, CENTER_OF_SCREEN.y, "ball");
      
      this.eventData = {
        "ball_x": this.ball.x,
        "ball_y": this.ball.y,
        "left_player_position_x": this.left_paddle.x,
        "left_player_position_y": this.left_paddle.y,
        "right_player_position_x": this.right_paddle.x,
        "right_player_position_y": this.right_paddle.y
      };
      this.receiveSocket.onmessage = (event) => {
        console.log('receive data: ', event.data)
        this.eventData = JSON.parse(event.data);
      };
    }

    async update() {
      if (this.eventData) {
        this.ball.move(this.eventData.ball_x, this.eventData.ball_y)
        this.left_paddle.move(this.eventData.left_player_position_x, this.eventData.left_player_position_y)
        this.right_paddle.move(this.eventData.right_player_position_x, this.eventData.right_player_position_y)
        this.receiveSocket.send(JSON.stringify({
          "type": "end_loop",
          "left_player_velocity": this.left_paddle.velocity_to_dict(),
          "right_player_velocity": this.right_paddle.velocity_to_dict(),
        }));
      }
  }
}