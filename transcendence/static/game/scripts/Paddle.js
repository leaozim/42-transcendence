class Paddle extends Phaser.GameObjects.Image  {
    constructor(scene, x, y, texture) {
        super(scene, x, y, texture);
        this.velocity = new Vector2(0, 0);
        scene.add.existing(this);
        this.setupInputHandler();


    }

    hitHorizontalBorders() {
        const halfBallHeight = this.height / 2;
    
        if (this.y - halfBallHeight <= 0) {
            this.y = halfBallHeight;
            this.velocity.y = 0;
        } else if (this.y + halfBallHeight >= CANVAS_HEIGHT) {
            this.y = CANVAS_HEIGHT - halfBallHeight;
            this.velocity.y = 0;
        }
    }
    
    move() {
        this.y += this.velocity.y;
        this.x += this.velocity.x;
    }

    setupInputHandler() {
        document.addEventListener('keydown', (event) => {
            let velocity = { x: 0, y: 0 };

            switch (event.key) {
                case 'w':
                    velocity.y = -5;
                    break;
                case 's':
                    velocity.y = 5;
                    break;
                case 'ArrowUp':
                    velocity.y = -5;
                    break;
                case 'ArrowDown':
                    velocity.y = 5;
                    break;
            }

            this.setPaddleVelocity(velocity);
        });

        document.addEventListener('keyup', () => {
            this.setPaddleVelocity({ x: 0, y: 0 });
        });
    }

    setPaddleVelocity(velocity) {
        this.velocity = velocity;
    }

    resetPaddle(player) {
        if (player == PLAYER_LEFT)
            this.y = LEFT_PADDLE_START_POSITION.y;
        else 
            this.y = RIGHT_PADDLE_START_POSITION.y;
    }

}
    