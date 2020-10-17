"""
Life
Copyright (C) 2020 Axel#3456

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import random
import typing

import aiohttp
import discord

from cogs.voice.lavalink.exceptions import *
from cogs.voice.lavalink.node import Node
from cogs.voice.lavalink.player import Player


class Client:

    def __init__(self, bot, session: aiohttp.ClientSession = None) -> None:

        self.bot = bot
        self.session = session or aiohttp.ClientSession(loop=self.bot.loop)

        self.nodes: typing.Dict[str, Node] = {}

    def __repr__(self) -> str:
        return f'<LavaLinkClient node_count={len(self.nodes)} player_count={len(self.players)}>'

    @property
    def players(self) -> typing.Mapping[int, Player]:

        players = []
        for node in self.nodes.values():
            players.extend(node.players.values())

        return {player.guild.id: player for player in players}

    async def create_node(self, *, host: str, port: str, password: str, identifier: str) -> Node:

        await self.bot.wait_until_ready()

        if identifier in self.nodes.keys():
            raise NodeCreationError(f'Node with identifier \'{identifier}\' already exists.')

        node = Node(client=self, host=host, port=port, password=password, identifier=identifier)
        await node.connect()

        return node

    def get_node(self, *, identifier: str = None) -> typing.Optional[Node]:

        nodes = {identifier: node for identifier, node in self.nodes.items() if node.is_connected}
        if not nodes:
            return None

        if identifier is None:
            return random.choice([node for node in nodes.values()])

        return nodes.get(identifier, None)

    async def connect(self, *, channel: discord.VoiceChannel):

        node = self.get_node()
        if not node:
            raise NodeNotFound('There are no nodes available.')

        player = await channel.connect(cls=Player)
        player.node = node

        node.players[channel.guild.id] = player
        return player
