import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
'''
    Note que essa bola e raquete são diferentes pro python e pro js.
    O Js não possui lógica de jogo, apenas para exibir na tela e capturar input
    enquanto este de python contém lógicas importantes, como detecção de colisão
'''
from static.game.scripts.Ball import Ball
from static.game.scripts.Paddle import Paddle
from static.game.scripts.Vector2 import Vector2
from static.game.scripts.constants import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

'''
    Dicionário global que armazena todas as informações de todos os jogos.
    Manter na key o room_group_name e como value um outro dicionário com as infos.
    Exemplo:
    game_69_broadcast: {
        ball: Ball(),
        left_paddle: Paddle(...),
        ...
    }
''' 
games = {}

class BroadcastConsumer(AsyncWebsocketConsumer):

    '''
        Após capturar o nome do grupo e o id, verifica se o nome do grupo existe como key na variavel
        global games. Caso exista, não precisa criar de novo, então só atribui os valores para
        as variáveis da classe (self.ball, self.paddle, ...). No caso de não existir,
        então ele cria uma nova chave com uma nova bola, novos paddles e um score zerado.
    '''
    async def connect(self):
        await self.accept()
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"game_{self.room_id}_broadcast"

        if self.room_group_name not in games:  # verifica se os dados do game não existe
            games[self.room_group_name] = {  # caso não exista, cria uma nova chave para armazenar os dados
                'ball': Ball(),
                'left_paddle': Paddle(LEFT_PADDLE_START_POSITION[0], LEFT_PADDLE_START_POSITION[1]),
                'right_paddle': Paddle(RIGHT_PADDLE_START_POSITION[0], RIGHT_PADDLE_START_POSITION[1]),
                'score': [0, 0]
                }
        # passa todas as variáveis do game para uma variável específica dessa instância, para facilitar o acesso depois
        self.ball = games[self.room_group_name]['ball']
        self.left_paddle = games[self.room_group_name]['left_paddle']
        self.right_paddle = games[self.room_group_name]['right_paddle']
        self.score = games[self.room_group_name]['score']

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # vai servir no futuro para enviar informações de começar jogo ou não
        # vamos precisar criar a lógica de marcar connect dos players jogadores
        await self.send(text_data=json.dumps({"type": "playerId", "playerId": 'cavalinho'}))

    # aqui vamos precisar criar a lógica de marcar disconect dos players jogadores
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event['data']))

    '''
        Toda vez que recebe alguma informação do frontend, essa informação é processada e enviada de volta
        apenas as posições dos objetos da cena e o score.
        É basicamente o loop do jogo, porém quem controla o timedelta do loop é o phaser pelo frontend.
        Lá, acontece a mesma coisa: Recebe infos, atualiza a tela e envia info pra cá, porém o frontend
        não depende de receber dados para funcionar, ele possui o loop do phaser através do update,
        então ele continua "correndo" mesmo com aqui engasgado.
    '''
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        await self.ball.move()

        # pega informação de input dos paddles e processa as infos pra trazer nova posição dos paddles
        left_player_velocity = text_data_json.get("left_player_velocity", {})
        right_player_velocity = text_data_json.get("right_player_velocity", {})
        await self.right_paddle.set_paddle_velocity(right_player_velocity.get('x', 0), right_player_velocity.get('y', 0))
        await self.right_paddle.move()
        await self.left_paddle.set_paddle_velocity(left_player_velocity.get('x', 0), left_player_velocity.get('y', 0))
        await self.left_paddle.move()

        # checa colisão com raquete ou ponto. atualiza o score se necessário
        self.ball.checkPaddleCollision(self.left_paddle.position.x, self.left_paddle.position.y, PLAYER_LEFT)
        self.ball.checkPaddleCollision(self.right_paddle.position.x, self.right_paddle.position.y, PLAYER_RIGHT)
        
        if (self.ball.position.x > CANVAS_WIDTH):
            self.score[PLAYER_LEFT] += 1
            await self.ball.resetBall()
        if (self.ball.position.x < 0):
            self.score[PLAYER_RIGHT] += 1
            await self.ball.resetBall()

        await self.channel_layer.group_send(self.room_group_name, {
            "type": "game_update",
            "data": {
                "ball_x": self.ball.position.x,
                "ball_y": self.ball.position.y,
                "left_player_position_x": self.left_paddle.position.x,
                "left_player_position_y": self.left_paddle.position.y,
                "right_player_position_x": self.right_paddle.position.x,
                "right_player_position_y": self.right_paddle.position.y,
                "score": self.score
            }
        })
