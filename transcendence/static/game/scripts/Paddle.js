class Paddle extends Phaser.GameObjects.Image {
    constructor(scene, x, y, texture, i_move) {
        super(scene, x, y, texture);
        scene.add.existing(this);
        // -1 (up), 0 or +1 (down); the server moves the paddle.
        this.direction = 0;
        // Called with the new direction when the player presses or releases a key.
        this.onDirectionChange = null;
        if (i_move) {
            this.setupInputHandler();
        }
    }

    move(x, y) {
        this.x = x;
        this.y = y;
    }

    setupInputHandler() {
        const upKeys = new Set(["arrowup", "w"]);
        const downKeys = new Set(["arrowdown", "s"]);
        const held = new Set();

        const update = () => {
            const keys = [...held];
            const direction = (keys.some((k) => downKeys.has(k)) ? 1 : 0) - (keys.some((k) => upKeys.has(k)) ? 1 : 0);
            if (direction !== this.direction) {
                this.direction = direction;
                if (this.onDirectionChange) {
                    this.onDirectionChange(direction);
                }
            }
        };

        document.addEventListener('keydown', (event) => {
            const key = event.key.toLowerCase();
            if (!upKeys.has(key) && !downKeys.has(key)) {
                return;
            }
            event.preventDefault(); // arrow keys would scroll the page
            held.add(key);
            update();
        });

        document.addEventListener('keyup', (event) => {
            held.delete(event.key.toLowerCase());
            update();
        });

        // Keys released while the window is not focused never send "keyup".
        window.addEventListener('blur', () => {
            held.clear();
            update();
        });
    }
}
