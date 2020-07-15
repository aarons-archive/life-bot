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
from discord.ext import commands

from cogs.utilities import utils
from config import config
from utilities import context, help

os.environ['JISHAKU_HIDE'] = 'True'
os.environ['JISHAKU_NO_UNDERSCORE'] = 'True'

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class Life(commands.AutoShardedBot):

    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, reconnect=True,
                         help_command=help.HelpCommand())

        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)

        self.config = config.LifeConfig(self)
        self.utils = utils.Utils(self)

        self.log = logging.getLogger("Life")
        self.start_time = time.time()

        self.guild_blacklist = {}
        self.user_blacklist = {}
        self.redis = None
        self.db = None

        self.owner_ids = {238356301439041536}
        self.allowed_blacklisted_commands = ['help', 'support']
        self.allowed_dm_commands = ['help', 'support', 'invite']

        self.activity = discord.Activity(type=discord.ActivityType.playing, name=f'{self.config.prefix}help')
        self.voice_perms = discord.Permissions(connect=True, speak=True)
        self.permissions = discord.Permissions(read_messages=True, send_messages=True, embed_links=True,
                                               attach_files=True, read_message_history=True,
                                               external_emojis=True, add_reactions=True)
        self.add_check(self.can_run_commands)

    async def get_context(self, message: discord.Message, *, cls=context.Context):
        return await super().get_context(message, cls=cls)

    async def get_prefix(self, message: discord.Message):
        if not message.guild:
            prefixes = [self.config.prefix]
        else:
            prefixes = [self.config.prefix]

        return commands.when_mentioned_or(*prefixes)(self, message)

    async def can_run_commands(self, ctx: commands.Context):

        if not ctx.guild and ctx.command.name not in self.allowed_dm_commands:
            raise commands.NoPrivateMessage()

        if ctx.author.id in self.user_blacklist.keys() and ctx.command.name not in self.allowed_blacklisted_commands:
            raise commands.CheckFailure(f'You are blacklisted from using this bot for the following reason:\n\n'
                                        f'`{self.user_blacklist[ctx.author.id]}`\n\nIf you would like to appeal this '
                                        f'please use the command `{self.config.prefix}appeal`.')

        me = ctx.guild.me if ctx.guild else self.user
        needed = {perm: value for perm, value in dict(self.permissions).items() if value is True}
        current = dict(me.permissions_in(ctx.channel))

        if ctx.command.cog and ctx.command.cog.qualified_name == 'Music' and ctx.author.voice:
            voice_channel = ctx.author.voice.channel
            needed.update({perm: value for perm, value in dict(self.voice_perms).items() if value is True})
            current.update({perm: value for perm, value in me.permissions_in(voice_channel) if value is True})

        missing = [perm for perm, value in needed.items() if current[perm] != value]

        if missing:
            raise commands.BotMissingPermissions(missing)

        return True

    async def start(self, *args, **kwargs):

        try:
            self.db = await asyncpg.create_pool(**self.config.database_info)
        except Exception as e:
            print(f'\n[DB] An error occurred while connecting to postgresql: {e}\n')
        else:
            print(f'\n[DB] Connected to the postgresql database.\n')

            blacklisted_users = await self.db.fetch('SELECT * FROM blacklist WHERE type = $1', 'user')
            for user in blacklisted_users:
                self.user_blacklist[user['id']] = user['reason']
            print(f'[BLACKLIST] Loaded user blacklist. [{len(blacklisted_users)} users]')

            blacklisted_guilds = await self.db.fetch('SELECT * FROM blacklist WHERE type = $1', 'guild')
            for guild in blacklisted_guilds:
                self.guild_blacklist[guild['id']] = guild['reason']
            print(f'[BLACKLIST] Loaded guild blacklist. [{len(blacklisted_guilds)} guilds]\n')

        try:
            redis = aredis.StrictRedis(**self.config.redis_info)
            await redis.set('connected', True)
        except aredis.ConnectionError:
            print(f'[REDIS] An error occurred while connecting to redis.\n')
        else:
            self.redis = redis
            print(f'[REDIS] Connected to the redis database.\n')

        for extension in self.config.extensions:
            try:
                self.load_extension(extension)
                print(f'[EXT] Loaded - {extension}')
            except commands.ExtensionNotFound:
                print(f'[EXT] Failed - {extension}')

        await super().start(*args)

    async def close(self):

        print("\n[BOT] Closing bot down.")

        music = self.get_cog('Music')
        if music:
            await music.unload()

        print("[EXT] Unloading all extensions.")
        for extension in self.config.extensions:
            try:
                self.unload_extension(extension)
            except commands.ExtensionNotFound:
                pass

        print("[DB] Closing database connection.")
        await self.db.close()

        print("[CS] Closing aiohttp client session.")
        await self.session.close()

        print("Bye bye!")
