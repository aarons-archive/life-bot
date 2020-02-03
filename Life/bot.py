import asyncio
import collections
import json
import os
import time

import aiohttp
import asyncpg
import psutil
from discord.ext import commands

import config
from cogs.music import player
from utilities import paginators

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
    "cogs.kross",
    "cogs.music.music",
    #"cogs.rpg.accounts",
]


class MyContext(commands.Context):

    @property
    def player(self):
        return self.bot.granitepy.get_player(self.guild, cls=player.Player)

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
        self.loop = asyncio.get_event_loop()
        self.process = psutil.Process()
        self.boot_time = time.time()
        self.config = config

        self.granitepy = None
        self.session = None
        self.rpg = None
        self.db = None

        self.socket_stats = collections.Counter()
        self.pings = collections.deque(maxlen=14400)
        self.owner_ids = [238356301439041536]
        self.guild_blacklist = []
        self.user_blacklist = []
        self.usage = {}

        for extension in EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f"[EXT] Success - {extension}")
            except commands.ExtensionNotFound:
                print(f"[EXT] Failed - {extension}")

    def run(self):
        self.loop.run_until_complete(self.bot_start())

    async def initiate_database(self):

        try:
            self.db = await asyncpg.create_pool(**self.config.DB_CONN_INFO)
            print(f"\n[DB] Connected to database.")

            usages = await self.db.fetch("SELECT * FROM bot_usage")
            blacklisted_users = await self.db.fetch("SELECT * FROM blacklist WHERE type = $1", "user")
            blacklisted_guilds = await self.db.fetch("SELECT * FROM blacklist WHERE type = $1", "guild")

            for guild in usages:
                self.usage[guild["id"]] = json.loads(guild["usage"])
            print(f"[DB] Loaded bot usages.")
            for user in blacklisted_users:
                self.user_blacklist.append(user["id"])
            print(f"[DB] Loaded user blacklist.")
            for guild in blacklisted_guilds:
                self.guild_blacklist.append(guild["id"])
            print(f"[DB] Loaded guild blacklist.")

        except ConnectionRefusedError:
            print(f"\n[DB] Connection to database was denied.")
        except Exception as e:
            print(f"\n[DB] An error occured: {e}")

    async def bot_start(self):
        self.session = aiohttp.ClientSession()
        await self.initiate_database()
        await self.login(config.DISCORD_TOKEN)
        await self.connect()

    async def is_owner(self, user):
        return user.id in self.owner_ids

    async def on_message(self, message):

        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if ctx.command:
            if message.author.id in self.user_blacklist:
                return await message.channel.send(f"Sorry, you are blacklisted from using this bot.")
            else:
                await self.process_commands(message)

    async def on_message_edit(self, before, after):

        if before.author.bot or after.author.bot:
            return

        ctx = await self.get_context(after)
        if ctx.command:
            if before.author.id or after.author.id in self.user_blacklist:
                return await after.channel.send(f"Sorry, you are blacklisted from using this bot.")
            else:
                await self.process_commands(after)

    async def get_context(self, message, *, cls=MyContext):
        return await super().get_context(message, cls=cls)


if __name__ == "__main__":
    Life().run()
