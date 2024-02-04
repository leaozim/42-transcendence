class Ball extends Phaser.GameObjects.Image {
    constructor(scene, x, y, texture ) {
        // super(scene, x, y, texture);

        this.initialSpeed = 2
        this.speed = this.initialSpeed;
        this.maxSpeed = 10;
        this.accelerationInterval = 3000;
        this.accelerationAmount = 0.1;
        this.setAccelerationTimer()
        this.setDirections()
        this.x = x;
        this.y = y;
        this.velocity = this.setRandomDirection()

        // Adicione lógica específica da bola aqui, se necessário
        // this.setTexture(texture); caso o super não funcione. Mas só tente isso como último recurso
        // scene.add.existing(this);
   
    }

    hitHorizontalBorders() {
        if (this.y <= 0 || this.y >= CANVAS_HEIGHT)
            this.velocity.y *= -1;
    }

    move() {
        this.hitHorizontalBorders()
        this.y += this.velocity.y;
        this.x += this.velocity.x;
    }

    checkPaddleCollision(xPaddle, yPaddle, paddleHeight, player) {


        let offset = paddleHeight / 2;
        if (player == PLAYER_LEFT) {
            if (this.x <= xPaddle && 
                this.y <= yPaddle + offset &&
                this.y >= yPaddle - offset) {
                this.velocity.x *= -1;
                this.lastHitPlayer = player;
            }
        }
        else {
            if (this.x >= xPaddle && 
                this.y <= yPaddle + offset &&
                this.y >= yPaddle - offset) {
                this.velocity.x *= -1;
                this.lastHitPlayer = player;
            }
        }
        return [false, null];
    }
    
    setRandomDirection() {
        return Phaser.Math.RND.pick(this.directions);
    }

    accelerateBall() {
        this.speed += this.accelerationAmount;

        if (this.speed > this.maxSpeed) {
            this.speed = this.maxSpeed;
        }
        this.velocity.x += this.velocity.x > 0 ? this.accelerationAmount : -this.accelerationAmount;
        this.velocity.y += this.velocity.y > 0 ? this.accelerationAmount : -this.accelerationAmount;
    }

    resetBall () {
        this.x = CENTER_OF_SCREEN.x;
        this.y = CENTER_OF_SCREEN.y;
        this.speed = this.initialSpeed;
        this.setDirections(); 
        this.resetAccelerationTimer()
        this.velocity = this.setRandomDirection();
    }

    setDirections() {
        this.directions = [
            new Vector2(this.speed, this.speed),
            new Vector2(-this.speed, this.speed),
            new Vector2(this.speed, -this.speed),
            new Vector2(-this.speed, -this.speed)
        ];
    }

    resetAccelerationTimer() {
        if (this.accelerationTimer) {
            this.accelerationTimer.destroy();
        }
        this.setAccelerationTimer()
    }

    setAccelerationTimer() {
        this.accelerationTimer = this.scene.time.addEvent({
            delay: this.accelerationInterval,
            callback: this.accelerateBall,
            callbackScope: this,
            loop: true
        });
    }
    
}
 