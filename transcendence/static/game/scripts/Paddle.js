class Paddle extends Phaser.GameObjects.Image  {
    constructor(scene, x, y, texture, i_move) {
        super(scene, x, y, texture);
        this.velocity = new Vector2(0, 0);
        scene.add.existing(this);
        if (i_move) {
            this.setupInputHandler();
        }
    }
    
    move(x, y) {
        this.x = x;
        this.y = y;
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

    velocity_to_dict() {
        return {x: this.velocity.x, y: this.velocity.y}
    }

}
