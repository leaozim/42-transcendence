class Scene3 extends Phaser.Scene {
    constructor() {
        super("GameOver");
    }

    init(data) {
        this.winner = data.winner
    }

    async create() {
        // Adiciona o texto "Fim de jogo" no centro da tela
        this.add.text(this.cameras.main.centerX, this.cameras.main.centerY, "End of game", {
            font: "48px Arial",
            fill: "#ffffff"
        }).setOrigin(0.5);

        const message = (this.winner !== null ? `The winner is ${this.winner}` : "Game annulled")

        this.add.text(this.cameras.main.centerX, this.cameras.main.centerY + 50, message, {
            font: "24px Arial",
            fill: "#ffffff"
        }).setOrigin(0.5);

        this.add.text(this.cameras.main.centerX, this.cameras.main.centerY + 100, "You can close this window", {
            font: "18px Arial",
            fill: "#ffffff"
        }).setOrigin(0.5);
    }
}