import asyncio
import collections
import json
import os
import time

import aiohttp
import asyncpg
import config
import psutil
from discord.ext import commands

from Life.Life.cogs.music.player import Player
from Life.Life.cogs.utilities.paginators import CodeblockPaginator, Paginator, EmbedPaginator, EmbedsPaginator

os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"

EXTENSIONS = [
    "cogs.information",
    "cogs.fun",
    "cogs.help",
    "cogs.owner",
    "jishaku",
    "cogs.background",
    "cogs.events",
    "cogs.music.music",
    "cogs.rpg.accounts"
]


class Life(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
            reconnect=True,
        )
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession()

        self.config = config
        self.start_time = time.time()
        self.process = psutil.Process()

        self.db = None
        self.db_ready = False

        self.owner_ids = {238356301439041536}
        self.user_blacklist = []
        self.guild_blacklist = []

        self.usage = {}

        for extension in EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f"[EXT] Success - {extension}")
            except commands.ExtensionNotFound:
                print(f"[EXT] Failed - {extension}")

    def run(self):
        try:
            self.loop.run_until_complete(self.bot_start())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.bot_close())

    async def db_connect(self):
        # Try to connect to the database.
        try:
            self.db = await asyncpg.create_pool(**config.DB_CONN_INFO)
            print(f"\n[DB] Connected to database.")

            # Create tables if the dont exist.
            print("\n[DB] Creating tables.")
            with open("schema.sql") as r:
                await self.db.execute(r.read())
            print("[DB] Done creating tables.")

            # Tell the bot that the databse is ready.
            self.db_ready = True

            # Fetch command usage from database.
            usage = await self.db.fetch("SELECT * FROM bot_usage")

            # Add the usage of each guild to the bots usage.
            for guild in usage:
                self.usage[guild["id"]] = json.loads(guild["usage"])

            # Fetch user/guild blacklists.
            blacklisted_users = await self.db.fetch("SELECT * FROM user_blacklist")
            blacklisted_guilds = await self.db.fetch("SELECT * FROM guild_blacklist")

            # Append blacklisted users and guilds to the respective blacklists.
            for user in range(len(blacklisted_users)):
                self.user_blacklist.append(int(blacklisted_users[user]["id"]))
            for user in range(len(blacklisted_guilds)):
                self.guild_blacklist.append(int(blacklisted_guilds[user]["id"]))

        # Accept any exceptions we might find.
        except ConnectionRefusedError:
            print(f"\n[DB] Connection to database was denied.")
        except Exception as e:
            print(f"\n[DB] An error occured: {e}")

    async def bot_start(self):
        await self.db_connect()
        await self.login(config.DISCORD_TOKEN)
        await self.connect()

    async def bot_close(self):
        await super().logout()
        await self.session.close()

    async def is_owner(self, user):
        # Set custom owner ids.
        return user.id in self.owner_ids

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=MyContext)


class MyContext(commands.Context):

    @property
    def player(self):
        # Get the current guilds player.
        return self.bot.andesite.get_player(self.guild.id, cls=Player)

    async def paginate(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Start pagination
        paginator = Paginator(
            ctx=self,
            title=title,
            entries=entries,
            entries_per_page=entries_per_page,
            total_entries=len(entries))
        return await paginator.paginate()

    async def paginate_embed(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")
        footer = kwargs.get("footer")
        colour = kwargs.get("colour")

        # Start pagination
        paginator = EmbedPaginator(
            ctx=self,
            title=title,
            footer=footer,
            entries=entries,
            colour=colour,
            entries_per_page=entries_per_page,
            total_entries=len(entries))
        return await paginator.paginate()

    async def paginate_codeblock(self, **kwargs):
        # Get the aruguements.
        title = kwargs.get("title")
        entries = kwargs.get("entries")
        entries_per_page = kwargs.get("entries_per_page")

        # Start pagination
        paginator = CodeblockPaginator(
            ctx=self,
            title=title,
            entries=entries,
            entries_per_page=entries_per_page,
            total_entries=len(entries))
        return await paginator.paginate()

    async def paginate_embeds(self, **kwargs):
        # Get the aruguements.
        entries = kwargs.get("entries")

        paginator = EmbedsPaginator(ctx=self, entries=entries)

        # Start pagination
        return await paginator.paginate()


if __name__ == "__main__":
    Life().run()
