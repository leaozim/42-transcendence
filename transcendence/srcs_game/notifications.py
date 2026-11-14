"""
Live updates of the "open games" panel on the home page.

Each logged-in home page listens on /ws/lobby/ (LobbyConsumer), which joins
the group of its user. Whenever one of the user's games changes (created,
joined, started, finished, canceled) or a player enters or leaves a game
room, the group gets a "lobby.changed" event and the page reloads the panel.
"""

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def lobby_group(user_id):
    return f"lobby_{user_id}"


async def notify_lobby(*user_ids):
    channel_layer = get_channel_layer()
    for user_id in {user_id for user_id in user_ids if user_id}:
        await channel_layer.group_send(lobby_group(user_id), {"type": "lobby.changed"})


def notify_lobby_sync(*user_ids):
    async_to_sync(notify_lobby)(*user_ids)
