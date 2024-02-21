class Vector2 {
    constructor(x, y) {
        this.x = x;
        this.y = y
    }

    add(rightSideVector) {
        this.x += rightSideVector.x
        this.y += rightSideVector.y
    }

    toString() {
        return `Vector2(${this.x}, ${this.y})`
    }
}