import asyncio
import collections
import os
import re
import time

import aiohttp
import asyncpg
import discord
import psutil
from discord.ext import commands

from cogs.utilities import utils
from config import config
from context import LifeContext

os.environ['JISHAKU_HIDE'] = 'True'
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
asyncio.set_event_loop(asyncio.SelectorEventLoop())


class Life(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(config.PREFIX), reconnect=True)

        self.bot = self
        self.loop = asyncio.get_event_loop()
        self.session = None

        self.utils = utils.Utils(self.bot)
        self.process = psutil.Process()
        self.start_time = time.time()
        self.config = config
        self.db = None

        self.pings = collections.deque(maxlen=1440)
        self.socket_stats = collections.Counter()
        self.owner_ids = [238356301439041536]
        self.guild_blacklist = {}
        self.user_blacklist = {}

        self.bot.add_check(self.can_run_command)

        self.general_perms = discord.Permissions(add_reactions=True, read_messages=True, send_messages=True,
                                                 embed_links=True, attach_files=True, read_message_history=True,
                                                 external_emojis=True)
        self.voice_perms = discord.Permissions(permissions=self.general_perms.value, connect=True, speak=True)

        self.clean_content = commands.clean_content()
        self.image_url_regex = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:'
                                          'jpe?g|gif|png|webm))(?:\?([^#]*))?(?:#(.*))?')
        self.spotify_url_regex = re.compile("https://open.spotify.com?.+(album|playlist|track)/([a-zA-Z0-9]+)")

    @property
    def uptime(self):

        return round(time.time() - self.start_time)

    async def get_context(self, message, *, cls=LifeContext):

        return await super().get_context(message, cls=cls)

    async def can_run_command(self, ctx: commands.Context):

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        if ctx.author.id in self.bot.user_blacklist.keys():
            raise commands.CheckFailure(f'You are blacklisted from using this bot with reason '
                                        f'`{self.bot.user_blacklist[ctx.author.id]}`')

        me = ctx.guild.me if ctx.guild else self.bot.user
        needed_perms = {perm: value for perm, value in dict(self.general_perms).items() if value is not False}
        current_perms = dict(me.permissions_in(ctx.channel))
        missing = [perm for perm, value in needed_perms.items() if current_perms[perm] != value]

        if missing:
            raise commands.BotMissingPermissions(missing)

        return True

    async def on_message(self, message):

        if message.author.bot:
            return

        await self.process_commands(message)

    async def on_message_edit(self, before, after):

        if before.author.bot:
            return

        if before.content == after.content:
            return

        await self.process_commands(after)

    async def start(self, *args):

        self.session = aiohttp.ClientSession(loop=self.loop)

        try:
            self.db = await asyncpg.create_pool(**self.config.DATABASE)
            print(f'\n[DB] Connected to the database.\n')

            blacklisted_users = await self.db.fetch('SELECT * FROM blacklist WHERE type = $1', 'user')
            for user in blacklisted_users:
                self.user_blacklist[user['id']] = user['reason']
            print(f'[BLACKLIST] Loaded user blacklist. [{len(blacklisted_users)} users]')

            blacklisted_guilds = await self.db.fetch('SELECT * FROM blacklist WHERE type = $1', 'guild')
            for guild in blacklisted_guilds:
                self.guild_blacklist[guild['id']] = guild['reason']
            print(f'[BLACKLIST] Loaded guild blacklist. [{len(blacklisted_guilds)} guilds]\n')

        except Exception as e:
            print(f'\n[DB] An error occurred: {e}\n')

        for extension in self.config.EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f'[EXT] Loaded - {extension}')
            except commands.ExtensionNotFound:
                print(f'[EXT] Failed - {extension}')

        return await super().start(*args)

    async def close(self):

        print("[EXT] Unloading all extensions.")
        for extension in self.config.EXTENSIONS:
            try:
                self.unload_extension(extension)
            except commands.ExtensionNotFound:
                pass

        print("[DB] Closing database connection.")
        await self.db.close()

        print("[CS] Closing aiohttp client session.")
        await self.session.close()

        print("[BOT] Shutting bot down.")
        await super().close()

        print("Bye bye!")

    def run(self):
        super().run(self.config.TOKEN)
