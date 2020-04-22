import asyncio
import collections
import os
import re
import signal
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

        self.general_perms = discord.Permissions(add_reactions=True, read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
        self.voice_perms = discord.Permissions(permissions=self.general_perms.value, connect=True, speak=True)

        self.clean_content = commands.clean_content()
        self.image_url_regex = re.compile('(?:([^:/?#]+):)?(?://([^/?#]*))?([^?#]*\.(?:jpe?g|gif|png))(?:\?([^#]*))?(?:#(.*))?')

    @property
    def uptime(self):

        return round(time.time() - self.start_time)

    async def get_context(self, message, *, cls=LifeContext):

        return await super().get_context(message, cls=cls)

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

    async def can_run_command(self, ctx: commands.Context):

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        if ctx.author.id in self.bot.user_blacklist.keys():
            raise commands.CheckFailure(f'You are blacklisted from using this bot with reason `{self.bot.user_blacklist[ctx.author.id]}`')

        me = ctx.guild.me if ctx.guild else self.bot.user
        needed_perms = {perm: value for perm, value in dict(self.general_perms).items() if value is not False}
        current_perms = dict(me.permissions_in(ctx.channel))
        missing = [perm for perm, value in needed_perms.items() if current_perms[perm] != value]

        if missing:
            raise commands.BotMissingPermissions(missing)

        return True

    async def load_extensions(self):

        for extension in self.config.EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f'[EXT] Success - {extension}')
            except commands.ExtensionNotFound:
                print(f'[EXT] Failed - {extension}')

    async def load_database(self):

        try:
            self.db = await asyncpg.create_pool(**self.config.DATABASE)
            print(f'\n[DB] Connected to the database.')

            blacklisted_users = await self.db.fetch('SELECT * FROM blacklist WHERE type = $1', 'user')
            for user in blacklisted_users:
                self.user_blacklist[user['id']] = user['reason']
            print(f'\n[BLACKLIST] Loaded user blacklist. [{len(blacklisted_users)} users]')

            blacklisted_guilds = await self.db.fetch('SELECT * FROM blacklist WHERE type = $1', 'guild')
            for guild in blacklisted_guilds:
                self.guild_blacklist[guild['id']] = guild['reason']
            print(f'[BLACKLIST] Loaded guild blacklist. [{len(blacklisted_guilds)} guilds]')

        except ConnectionRefusedError:
            print(f'\n[DB] Connection to the database was denied.')
        except Exception as e:
            print(f'\n[DB] An error occurred: {e}')

    async def bot_start(self):

        self.session = aiohttp.ClientSession(loop=self.loop)
        await self.load_extensions()
        await self.load_database()

        await self.login(token=config.TOKEN)
        await self.connect()

    async def bot_close(self):

        await self.logout()

        await self.session.close()

    def run(self):

        try:
            self.loop.add_signal_handler(signal.SIGINT, lambda: self.loop.stop())
            self.loop.add_signal_handler(signal.SIGTERM, lambda: self.loop.stop())
        except NotImplementedError:
            pass

        async def runner():
            try:
                await self.bot_start()
            finally:
                await self.bot_close()

        # noinspection PyUnusedLocal
        def stop_loop_on_completion(f):
            self.loop.stop()

        future = asyncio.ensure_fgituture(runner(), loop=self.loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            future.remove_done_callback(stop_loop_on_completion)


if __name__ == '__main__':
    Life().run()
