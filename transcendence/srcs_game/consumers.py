import json
import uuid

from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class MultiplayerConsumer(WebsocketConsumer):
    MAX_SPEED = 5
    THRUST = 0.2

    game_group_name = "game_group"
    players = {}

    update_lock = asyncio.Lock()

    async def connect(self):
        self.player_id = str(uuid.uuid4())
        await self.accept()

        await self.channel_layer.group_add(
            self.game_group_name, self.channel_name
        )

        await self.send(
            text_data=json.dumps({"type": "playerId", "playerId": self.player_id})
        )

        async with self.update_lock:
            self.players[self.player_id] = {
                "id": self.player_id,
                "x": 500,
                "y": 500,
                "facing": 0,
                "dx": 0,
                "dy": 0,
                "thrusting": False,
            }

        if len(self.players) == 1:
            asyncio.create_task(self.game_loop())

    async def disconnect(self, close_code):
        async with self.update_lock:
            if self.player_id in self.players:
                del self.players[self.player_id]

        await self.channel_layer.group_discard(
            self.game_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type", "")

        player_id = text_data_json["playerId"]

        player = self.players.get(player_id, None)
        if not player:
            return

        if message_type == "mouseDown":
            player["thrusting"] = True
        elif message_type == "mouseUp":
            player["thrusting"] = False
        elif message_type == "facing":
            player["facing"] = text_data_json["facing"]

    async def state_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "stateUpdate",
                    "objects": event["objects"],
                }
            )
        )

    async def game_loop(self):
        while len(self.players) > 0:
            async with self.update_lock:
                for player in self.players.values():
                    if player["thrusting"]:
                        dx = self.THRUST * math.cos(player["facing"])
                        dy = self.THRUST * math.sin(player["facing"])
                        player["dx"] += dx
                        player["dy"] += dy

                        speed = math.sqrt(player["dx"] ** 2 + player["dy"] ** 2)
                        if speed > self.MAX_SPEED:
                            ratio = self.MAX_SPEED / speed
                            player["dx"] *= ratio
                            player["dy"] *= ratio

                    player["x"] += player["dx"]
                    player["y"] += player["dy"]

            await self.channel_layer.group_send(
                self.game_group_name,
                {"type": "state_update", "objects": list(self.players.values())},
            )
            await asyncio.sleep(0.05)