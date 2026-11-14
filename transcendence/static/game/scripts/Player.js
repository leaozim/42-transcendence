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
        const name = player === PLAYER_LEFT ? GAME_TEXTS.leftPlayer : GAME_TEXTS.rightPlayer;
        // Long usernames would overlap the clock in the middle.
        this.label = name.length > 12 ? `${name.slice(0, 11)}…` : name;

        this.scoreText = this.scene.add.text(xPosition, 50, `${this.label}: ${this.getScore()}`, scoreTextStyle).setOrigin(0.5);
    }

    incrementScore() {
        this.score += 1;
        updateScoreText()
    }

    getScore() {
        return this.score;
    }

    updateScoreText() {
        if (this.scoreText) {
            this.scoreText.setText(`${this.label}: ${this.getScore()}`);
        } 
    }
}