class Scene3 extends Phaser.Scene {
    constructor() {
        super("GameOver");
    }

    init(data) {
        this.winner = data.winner
    }

    async getThisUser() {
        const response = await fetch('http://localhost:8000/auth/user_id/');
        const data = await response.json();
        return data.user_id
      }

    async create() {
        // Adiciona o texto "Fim de jogo" no centro da tela
        this.add.text(this.cameras.main.centerX, this.cameras.main.centerY, "Fim de jogo", {
            font: "48px Arial",
            fill: "#ffffff"
        }).setOrigin(0.5);

        const message = (this.winner !== null ? `O vencedor é ${this.winner}` : "Jogo anulado")

        this.add.text(this.cameras.main.centerX, this.cameras.main.centerY + 50, message, {
            font: "24px Arial",
            fill: "#ffffff"
        }).setOrigin(0.5);
    }
}