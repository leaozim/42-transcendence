class Player extends Phaser.GameObjects.Image {
    constructor(scene, paddle, player, id) {
        super(scene);
        this.scene = scene;
        this.player = player;
        this.score = 0;
        this.paddle = paddle;
        const scoreTextStyle = {    
            fontFamily: 'Exo',
            fontSize: '36px',
            color: '#D613F0',
           
        };
        const xPosition = (player === PLAYER_LEFT) ? 200 : 580;
        this.id = id

        this.scoreText = this.scene.add.text(xPosition, 50, `Player ${this.player === PLAYER_LEFT ? 'Left' : 'Right'}: ${this.getScore()}`, scoreTextStyle).setOrigin(0.5);
    }

    incrementScore() {
        this.score += 1;
    }

    getScore() {
        return this.score;
    }

    updateScoreText() {
        if (this.scoreText) {
            this.scoreText.setText(`Player ${this.player === PLAYER_LEFT ? 'Left' : 'Right'}: ${this.getScore()}`);
        } 
    }
}