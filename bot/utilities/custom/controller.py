# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
import discord

# My stuff
from utilities import enums, utils


if TYPE_CHECKING:

    # My stuff
    from utilities import custom


class Controller:

    def __init__(
        self,
        player: custom.Player,
        /
    ) -> None:

        self.player: custom.Player = player
        self.message: discord.Message | None = None

    #

    async def invoke(self, channel: discord.TextChannel | None = None) -> discord.Message | None:

        if (channel is None and self.player.text_channel is None) or self.player.current is None:
            return

        channel = channel or self.player.text_channel
        guild_config = await self.player.client.guild_manager.get_config(channel.guild.id)

        embed = utils.embed(
            title="Now playing:",
            description=f"**[{self.player.current.title}]({self.player.current.uri})**\nBy **{self.player.current.author}**",
            thumbnail=self.player.current.thumbnail
        )

        embed.add_field(
            name="Player info:",
            value=f"`Paused:` {self.player.paused}\n"
                  f"`Loop mode:` {self.player.queue.loop_mode.name.title()}\n"
                  f"`Queue length:` {len(self.player.queue)}\n"
                  f"`Queue time:` {utils.format_seconds(sum(track.length for track in self.player.queue) // 1000, friendly=True)}\n",
        )
        embed.add_field(
            name="Track info:",
            value=f"`Time:` {utils.format_seconds(self.player.position // 1000)} / {utils.format_seconds(self.player.current.length // 1000)}\n"
                  f"`Author:` {self.player.current.author}\n"
                  f"`Source:` {self.player.current.source.value.title()}\n"
                  f"`Requester:` {self.player.current.requester.mention}\n"
        )

        if guild_config.embed_size is enums.EmbedSize.LARGE and not self.player.queue.is_empty():

            entries = [f"`{index + 1}.` [{entry.title}]({entry.uri})" for index, entry in enumerate(list(self.player.queue)[:3])]
            if len(self.player.queue) > 3:
                entries.append(f"`...`\n`{len(self.player.queue)}.` [{self.player.queue[-1].title}]({self.player.queue[-1].uri})")

            embed.add_field(name="Up next:", value="\n".join(entries), inline=False)

        return await channel.send(embed=embed)

    #

    async def handle_track_start(self) -> None:
        self.message = await self.invoke()

    async def handle_track_over(self) -> None:

        if not self.message:
            return

        try:
            old = self.player.queue._queue_history[0]
        except IndexError:
            return

        await self.message.edit(embed=utils.embed(description=f"Finished playing **[{old.title}]({old.uri})** by **{old.author}**."))
