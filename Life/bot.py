import asyncio
import collections
import json
import os
import multiprocessing
import time

import aiohttp
import asyncpg
import psutil
from discord.ext import commands

import config
from cogs.voice.utilities.player import Player
from cogs.utilities.imaging import Imaging
from cogs.utilities.utils import Utils
from cogs.utilities import paginators

os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"

EXTENSIONS = [
    "cogs.information",
    "cogs.images",
    "cogs.help",
    "cogs.owner",
    "jishaku",
    "cogs.background",
    "cogs.events",
    "cogs.kross",
    "cogs.voice.music",
    "cogs.voice.playlists",
]


class MyContext(commands.Context):

    @property
    def player(self):
        return self.bot.granitepy.get_player(self.guild, cls=Player)

    @property
    def account(self):
        return self.bot.account_manager.get_account(self.author.id)

    async def paginate(self, **kwargs):
        return await paginators.Paginator(ctx=self, **kwargs).paginate()

    async def paginate_embed(self, **kwargs):
        return await paginators.EmbedPaginator(ctx=self, **kwargs).paginate()

    async def paginate_codeblock(self, **kwargs):
        return await paginators.CodeBlockPaginator(ctx=self, **kwargs).paginate()

    async def paginate_embeds(self, **kwargs):
        return await paginators.EmbedsPaginator(ctx=self, **kwargs).paginate()


class Life(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
            reconnect=True,
        )
        self.bot = self
        self.loop = asyncio.get_event_loop()
        self.process = psutil.Process()
        self.boot_time = time.time()
        self.config = config

        self.granitepy = None
        self.session = None
        self.rpg = None
        self.db = None

        self.pings = collections.deque(maxlen=1440)
        self.socket_stats = collections.Counter()
        self.guild_blacklist = []
        self.user_blacklist = []
        self.usage = {}

        self.imaging = Imaging(self.bot)
        self.utils = Utils()

        self.bot.add_check(self.blacklist_check)

        for extension in EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f"[EXT] Success - {extension}")
            except commands.ExtensionNotFound:
                print(f"[EXT] Failed - {extension}")

    async def initiate_database(self):

        try:
            self.db = await asyncpg.create_pool(**self.config.DB_CONN_INFO)
            print(f"\n[DB] Connected to database.")

            usages = await self.db.fetch("SELECT * FROM bot_usage")
            blacklisted_users = await self.db.fetch("SELECT * FROM blacklist WHERE type = $1", "user")
            blacklisted_guilds = await self.db.fetch("SELECT * FROM blacklist WHERE type = $1", "guild")

            for guild in usages:
                self.usage[guild["id"]] = json.loads(guild["usage"])
            print(f"[DB] Loaded bot usages. ({len(usages)} guilds)")
            for user in blacklisted_users:
                self.user_blacklist.append(user["id"])
            print(f"[DB] Loaded user blacklist. ({len(blacklisted_users)} users)")
            for guild in blacklisted_guilds:
                self.guild_blacklist.append(guild["id"])
            print(f"[DB] Loaded guild blacklist. ({len(blacklisted_guilds)} guilds)")

        except ConnectionRefusedError:
            print(f"\n[DB] Connection to the database was denied.")
        except Exception as e:
            print(f"\n[DB] An error occurred: {e}")

    async def bot_start(self):
        self.session = aiohttp.ClientSession()
        await self.initiate_database()
        await self.login(config.DISCORD_TOKEN)
        await self.connect()

    async def bot_close(self):
        await self.session.close()
        await self.close()

    def run(self):
        try:
            self.loop.run_until_complete(self.bot_start())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.bot_close())

    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)

    async def on_message_edit(self, before, after):

        if before.content == after.content:
            return

        await self.process_commands(after)

    async def on_message(self, message):

        if message.author.bot:
            return

        await self.process_commands(message)

    async def blacklist_check(self, ctx):
        if ctx.author.id in self.bot.user_blacklist:
            raise commands.CheckFailure(f"Sorry, you are blacklisted from using this bot.")
        return True

    @property
    def uptime(self):
        return round(time.time() - self.boot_time)


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    Life().run()
