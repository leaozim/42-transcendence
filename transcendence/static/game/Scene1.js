class Scene1 extends Phaser.Scene {
    constructor() {
      super("bootGame");
    }

    preload(){
        this.load.image("paddle", "/static/game/assets/paddle.png");
        this.load.image("ball", "/static/game/assets/ball.png");
      }

    create() {
      this.add.text(20, 20, GAME_TEXTS.loading);
      this.scene.start("playGame");
    }
  }