import Vector2 from "./Vector2.js"

let velocidade_atual = new Vector2(1, 1)

let aceleracao = new Vector2(5, 4)

let nova_velocidade = velocidade_atual.add(aceleracao)

console.log(nova_velocidade)
