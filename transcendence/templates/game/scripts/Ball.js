import { Vector2 } from './Vector2';
class Ball {
    constructor(position, velocity) {
      this.position = position;
      this.velocity = velocity;
    }


    hitHorizontalBorders() {
        this.velocity.y *= -1;
    }

    move() {
        this.position = this.position.add(this.velocity);
    }
}


const initialPosition = new Vector2(0, 0);
const initialVelocity = new Vector2(2, 3);

const ball = new Ball(initialPosition, initialVelocity);
console.log(ball)
// Movendo a bola
ball.move();
console.log(ball)

if (true) {
  ball.hitHorizontalBorders();
  console.log(ball)
}