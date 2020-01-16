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


class Life(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or(config.DISCORD_PREFIX),
            reconnect=True,
        )
        self.session = aiohttp.ClientSession()
        self.loop = asyncio.get_event_loop()
        self.process = psutil.Process()
        self.start_time = time.time()
        self.config = config

        self.db = None
        self.account_manager = None
        self.granitepy = None

        self.socket_stats = collections.Counter()
        self.pings = collections.deque(maxlen=14400)
        self.owner_ids = {238356301439041536}
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
        try:
            self.loop.run_until_complete(self.bot_start())
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.bot_close())

    async def db_connect(self):

        try:
            self.db = await asyncpg.create_pool(**config.DB_CONN_INFO)
            print(f"\n[DB] Connected to database.")

            usage = await self.db.fetch("SELECT * FROM bot_usage")
            for guild in usage:
                self.usage[guild["id"]] = json.loads(guild["usage"])

            blacklisted_users = await self.db.fetch("SELECT * FROM blacklist WHERE type = $1", "user")
            blacklisted_guilds = await self.db.fetch("SELECT * FROM blacklist WHERE type = $1", "guild")
            for user in blacklisted_users:
                self.user_blacklist.append(int(user["id"]))
            for guild in blacklisted_guilds:
                self.guild_blacklist.append(int(guild["id"]))

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

        if not after.embeds and not after.pinned and not before.pinned and not before.embeds:
            ctx = await self.get_context(after)
            if ctx.command:
                if after.author.id in self.user_blacklist:
                    return await after.channel.send(f"Sorry, you are blacklisted from using this bot.")
                else:
                    await self.process_commands(after)

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=MyContext)


class MyContext(commands.Context):

    @property
    def player(self):
        return self.bot.granitepy.get_player(self.guild.id, cls=player.Player)

    @property
    def account(self):
        return self.bot.account_manager.get_account(self.author.id)

    async def paginate(self, **kwargs):
        paginator = paginators.Paginator(ctx=self, **kwargs)
        return await paginator.paginate()

    async def paginate_embed(self, **kwargs):
        paginator = paginators.EmbedPaginator(ctx=self, **kwargs)
        return await paginator.paginate()

    async def paginate_codeblock(self, **kwargs):
        paginator = paginators.CodeBlockPaginator(ctx=self, **kwargs)
        await paginator.paginate()

    async def paginate_embeds(self, **kwargs):
        paginator = paginators.EmbedsPaginator(ctx=self, **kwargs)
        return await paginator.paginate()


if __name__ == "__main__":
    Life().run()
