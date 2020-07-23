"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

import asyncio
import logging
import os
import sys
import time

import aiohttp
import aredis
import asyncpg
import discord
import prettify_exceptions
import setproctitle
from discord.ext import commands

from cogs.utilities import utils
from config import config
from utilities import context, help

try:
    import uvloop
    if sys.platform != 'win32':
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
except ImportError:
    uvloop = None
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()


os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'
os.environ['JISHAKU_HIDE'] = 'True'
prettify_exceptions.hook()


class Life(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, reconnect=True, help_command=help.HelpCommand(), loop=loop)

        self.session = aiohttp.ClientSession(loop=self.loop)
        self.config = config.LifeConfig(bot=self)
        self.utils = utils.Utils(bot=self)

        self.loop = asyncio.get_event_loop()
        self.log = logging.getLogger("Life")
        self.start_time = time.time()

        self.allowed_blacklisted = {'help', 'support', 'invite'}
        self.owner_ids = {238356301439041536}
        self.guild_blacklist = {}
        self.user_blacklist = {}
        self.guild_prefixes = {}
        self.redis = None
        self.db = None

        self.activity = discord.Activity(type=discord.ActivityType.playing, name=f'{self.config.prefix}help')
        self.voice_perms = discord.Permissions(connect=True, speak=True)
        self.permissions = discord.Permissions(read_messages=True, send_messages=True, embed_links=True, attach_files=True,
                                               read_message_history=True, external_emojis=True, add_reactions=True)
        self.add_check(self.can_run_commands)

    async def get_context(self, message: discord.Message, *, cls=context.Context):
        return await super().get_context(message, cls=cls)

    async def get_prefix(self, message: discord.Message):

        if not message.guild or message.guild.id not in self.guild_prefixes.keys():
            return commands.when_mentioned_or(self.config.prefix)(self, message)

        prefixes = [self.config.prefix, *self.guild_prefixes[message.guild.id]]
        return commands.when_mentioned_or(*prefixes)(self, message)

    async def can_run_commands(self, ctx: commands.Context):

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        if ctx.author.id in self.user_blacklist.keys() and ctx.command.name not in self.allowed_blacklisted:
            raise commands.CheckFailure(f'You are blacklisted from using this bot for the following reason:\n\n`{self.user_blacklist[ctx.author.id]}`\n\n'
                                        f'If you would like to appeal this please use `{self.config.prefix}appeal`.')

        needed_perms = {perm: value for perm, value in dict(self.permissions).items() if value is True}
        current_perms = dict(ctx.channel.permissions_for(ctx.guild.me)) if ctx.guild else dict(ctx.channel.me.permissions_in(ctx.channel))

        if ctx.command.cog and ctx.command.cog == self.get_cog('Music') and ctx.author.voice is not None:

            voice_channel = getattr(ctx.author.voice, 'channel', None)
            needed_perms.update({perm: value for perm, value in dict(self.voice_perms).items() if value is True})
            current_perms.update({perm: value for perm, value in voice_channel.permissions_for(ctx.guild.me) if value is True})

        missing = [perm for perm, value in needed_perms.items() if current_perms[perm] != value]

        if missing:
            raise commands.BotMissingPermissions(missing)

        return True

    async def start(self, *args, **kwargs):

        setproctitle.setproctitle('LifeBot')

        try:
            db = await asyncpg.create_pool(**self.config.database_info)
        except Exception as e:
            print(f'\n[DATABASE] An error occurred while connecting to postgresql: {e}\n')
        else:
            self.db = db
            print(f'\n[DATABASE] Connected to the postgresql database.\n')

        try:
            redis = aredis.StrictRedis(**self.config.redis_info)
        except aredis.ConnectionError:
            print(f'[REDIS] An error occurred while connecting to redis.\n')
        else:
            self.redis = redis
            print(f'[REDIS] Connected to the redis database.\n')

        for extension in self.config.extensions:
            try:
                self.load_extension(extension)
            except commands.ExtensionNotFound:
                print(f'[EXT] Failed - {extension}')
            else:
                print(f'[EXT] Loaded - {extension}')

        await super().start(*args)

    async def close(self):

        print("\n[BOT] Closing bot down.")

        music = self.get_cog('Music')
        if music:
            await music.unload()

        print("[DB] Closing database connection.")
        await self.db.close()

        print("[CS] Closing aiohttp client session.")
        await self.session.close()

        print("Bye bye!")
