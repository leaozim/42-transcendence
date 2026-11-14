class Scene3 extends Phaser.Scene {
    constructor() {
        super("GameOver");
    }

    init(data) {
        this.winner = data.winner;
        this.result = data.result;
        this.winnerId = data.winnerId;
    }

    winnerName() {
        // In single-player games the right player is the computer.
        if (VS_COMPUTER && String(this.winnerId) === String(rightPlayer)) {
            return GAME_TEXTS.computer;
        }
        return this.winner;
    }

    message() {
        if (this.result === "win") {
            return GAME_TEXTS.winner.replace("%(name)s", this.winnerName());
        }
        if (this.result === "draw") {
            return GAME_TEXTS.draw;
        }
        return GAME_TEXTS.annulled;
    }

    addButton(y, label, onClick) {
        return this.add.text(this.cameras.main.centerX, y, label, {
            font: "22px Arial",
            fill: "#52c0d7",
            backgroundColor: "#1e1e1e",
            padding: { x: 18, y: 10 },
        })
            .setOrigin(0.5)
            .setInteractive({ useHandCursor: true })
            .on("pointerover", function () { this.setColor("#ffffff"); })
            .on("pointerout", function () { this.setColor("#52c0d7"); })
            .on("pointerdown", onClick);
    }

    create() {
        const centerX = this.cameras.main.centerX;
        const centerY = this.cameras.main.centerY;

        this.add.text(centerX, centerY - 40, GAME_TEXTS.gameOver, {
            font: "48px Arial",
            fill: "#ffffff"
        }).setOrigin(0.5);

        this.add.text(centerX, centerY + 15, this.message(), {
            font: "24px Arial",
            fill: "#ffffff"
        }).setOrigin(0.5);

        let y = centerY + 90;
        const playAgainForm = document.getElementById("play-again-form");
        if (playAgainForm) {
            this.addButton(y, GAME_TEXTS.playAgain, () => playAgainForm.submit());
            y += 60;
        }
        this.addButton(y, GAME_TEXTS.backHome, () => { window.location.href = "/"; });
    }
}
