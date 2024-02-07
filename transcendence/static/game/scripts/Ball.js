class Ball extends Phaser.GameObjects.Image {
    constructor(scene, x, y, texture ) {
        super(scene, x, y, texture);

        this.x = x;
        this.y = y;

        // this.setTexture(texture);
        scene.add.existing(this);
   
    }

    move(x, y) {
        // this.hitHorizontalBorders()
        this.x = x;
        this.y = y;
    }    
}
 