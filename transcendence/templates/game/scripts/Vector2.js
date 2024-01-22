class Vector2 {
    constructor(x, y) {
        this.x = x;
        this.y = y
    }

    add(rightSideVector) {
        return new Vector2(this.x + rightSideVector.x, this.y + rightSideVector.y)
    }

    toString() {
        return `Vector2(${this.x}, ${this.y})`
    }
}

// velocidade_atual = new Vector2(1, 1)

// aceleracao = new Vector2(5, 4)

// nova_velocidade = velocidade_atual.add(aceleracao)

// console.log(nova_velocidade)
