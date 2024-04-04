import json
import time

from channels.generic.websocket import AsyncWebsocketConsumer
'''
    Note que essa bola e raquete são diferentes pro python e pro js.
    O Js não possui lógica de jogo, apenas para exibir na tela e capturar input
    enquanto este de python contém lógicas importantes, como detecção de colisão
'''
from static.game.scripts.Ball import Ball
from static.game.scripts.Paddle import Paddle
from static.game.scripts.constants import *
from asgiref.sync import sync_to_async
from srcs_game.models import Game
from srcs_user.models import User
from srcs_game.services import update_game_result

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

        '''
            Role desgraçado pra pegar o id dos jogadores que jogam neste game.
            Será usado para contar o número de conexões e começar o jogo
            apenas quando os 2 jogadores necessários estiverem conectados.
            Os únicos players que devem ser contados tanto no connect quanto
            no disconnect são esses dois. Os demais vão conseguir assistir
            o jogo mas não interagir com os paddles e ao entrarem ou saírem
            não devem interferir no começo ou encerramento do jogo.
        '''
        game = await sync_to_async(Game.objects.get)(pk=self.room_id)
        if game.is_finish:
            await self.close()
            return
        else:
            game.has_started = True
            await sync_to_async(game.save)()
        left_player = await sync_to_async(lambda: game.leftPlayer)()
        right_player = await sync_to_async(lambda: game.rightPlayer)()
        players_id = (left_player.id, right_player.id)
        

        if self.room_group_name not in games:  # verifica se os dados do game não existe
            games[self.room_group_name] = {  # caso não exista, cria uma nova chave para armazenar os dados
                'ball': Ball(),
                'left_paddle': Paddle(LEFT_PADDLE_START_POSITION[0], LEFT_PADDLE_START_POSITION[1]),
                'right_paddle': Paddle(RIGHT_PADDLE_START_POSITION[0], RIGHT_PADDLE_START_POSITION[1]),
                'score': [0, 0],
                'start_time': time.time(),
                'left_player_id': players_id[PLAYER_LEFT],
                'right_player_id': players_id[PLAYER_RIGHT],
                'reset_timer': False,
                'limit_time': 30,
                'connected': []  # Essa lista serve para dizer quais entre os dois players acima estão conectados
                # o que serve para definir início do game e interrupções por desconexão
                }
        # passa todas as variáveis do game para uma variável específica dessa instância, para facilitar o acesso depois
        self.ball = games[self.room_group_name]['ball']
        self.left_paddle = games[self.room_group_name]['left_paddle']
        self.right_paddle = games[self.room_group_name]['right_paddle']
        self.score = games[self.room_group_name]['score']
        self.playersIds = [games[self.room_group_name]['left_player_id'], games[self.room_group_name]['right_player_id']]
        self.connecteds = games[self.room_group_name]['connected']
        self.start_time = games[self.room_group_name]['start_time']
        self.reset_timer = games[self.room_group_name]['reset_timer']
        self.limit_time = games[self.room_group_name]['limit_time']

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
        elapsed_time = time.time() - self.start_time
        if elapsed_time >= self.limit_time:
            winner_user = None
            if len(self.connecteds) == 2:
                if self.reset_timer == False:
                    self.reset_timer = True
                    self.start_time = time.time()
                    self.limit_time = 60
                if self.score[PLAYER_LEFT] > self.score[PLAYER_RIGHT]:
                    winner = self.playersIds[PLAYER_LEFT]
                elif self.score[PLAYER_LEFT] < self.score[PLAYER_RIGHT]:
                    winner = self.playersIds[PLAYER_RIGHT]
                else:
                    winner_username = "Draw"
                    winner = None

                if winner:
                    winner_user = await sync_to_async(User.objects.get)(id=winner)
                    winner_username = winner_user.username
                    await sync_to_async(update_game_result)(self.room_id, self.score)
            else:
                winner_username = None

            event['data']['winner'] = winner_username
            game = await sync_to_async(Game.objects.get)(pk=self.room_id)
            game.is_finish = True
            game.winner = winner_user
            await sync_to_async(game.save)()

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
        logged_player_id = text_data_json.get("logged_player")
        if logged_player_id in self.playersIds:
            if logged_player_id not in self.connecteds:
                self.connecteds.append(logged_player_id)

        if len(self.connecteds) == 2:
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
                "score": self.score,
                "connected": self.connecteds
            }
        })
