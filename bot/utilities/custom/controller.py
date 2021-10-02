# Future
from __future__ import annotations

# Standard Library
from typing import TYPE_CHECKING

# Packages
import discord

# My stuff
from core import colours
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

    async def send_new(self) -> None:

        if not self.player.current or not self.player.text_channel:
            return

        assert self.player.current.ctx and self.player.current.ctx.guild

        embed = discord.Embed(
            colour=colours.MAIN,
            title="Now playing:",
            description=f"**[{self.player.current.title}]({self.player.current.uri})**"
        )
        embed.set_thumbnail(url=self.player.current.thumbnail)

        guild_config = await self.player.client.guild_manager.get_config(self.player.current.ctx.guild.id)

        if guild_config.embed_size is enums.EmbedSize.LARGE:

            embed.add_field(
                name="Player info:",
                value=f"`Paused:` {self.player.paused}\n"
                      f"`Loop mode:` {self.player.queue.loop_mode.name.title()}\n"
                      f"`Filter:` {None}\n"
                      f"`Queue entries:` {len(self.player.queue)}\n"
                      f"`Queue time:` {utils.format_seconds(sum(track.length for track in self.player.queue) // 1000, friendly=True)}\n",
            )
            embed.add_field(
                name="Track info:",
                value=f"`Time:` {utils.format_seconds(self.player.position // 1000)} / {utils.format_seconds(self.player.current.length // 1000)}\n"
                      f"`Author:` {self.player.current.author}\n"
                      f"`Source:` {self.player.current.source.value.title()}\n"
                      f"`Requester:` {self.player.current.requester.mention}\n"
                      f"`Seekable:` {self.player.current.is_seekable()}\n",
            )

            if not self.player.queue.is_empty():

                entries = [f"`{index + 1}.` [{entry.title}]({entry.uri})" for index, entry in enumerate(list(self.player.queue)[:5])]
                if len(self.player.queue) > 5:
                    entries.append(f"`...`\n`{len(self.player.queue)}.` [{self.player.queue[-1].title}]({self.player.queue[-1].uri})")

                embed.add_field(name="Up next:", value="\n".join(entries), inline=False)

        elif guild_config.embed_size is enums.EmbedSize.MEDIUM:

            embed.add_field(
                name="Player info:",
                value=f"`Paused:` {self.player.paused}\n"
                      f"`Loop mode:` {self.player.queue.loop_mode.name.title()}\n"
                      f"`Filter:` {None}\n",
            )
            embed.add_field(
                name="Track info:",
                value=f"`Time:` {utils.format_seconds(self.player.position // 1000)} / {utils.format_seconds(self.player.current.length // 1000)}\n"
                      f"`Author:` {self.player.current.author}\n"
                      f"`Source:` {self.player.current.source.value.title()}\n",
            )

        self.message = await self.player.text_channel.send(embed=embed)

    async def edit_old(self) -> None:

        if not self.message:
            return

        try:
            old = self.player.queue._queue_history[0]
        except IndexError:
            return

        await self.message.edit(embed=utils.embed(description=f"Finished playing **[{old.title}]({old.uri})** by **{old.author}**"))
