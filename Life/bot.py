#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.

import collections
import copy
import logging
import re
import time
import traceback
from typing import Literal, Optional, Type, Union

import aiohttp
import aioscheduler
import aredis
import asyncpg
import discord
import ksoftapi
import mystbin
import psutil
import spotify
from discord.ext import commands

import config
import slate
from utilities import context, help, managers


__log__ = logging.getLogger(__name__)


class Life(commands.AutoShardedBot):

    def __init__(self) -> None:
        super().__init__(
                command_prefix=self.get_prefix, help_command=help.HelpCommand(), owner_ids=config.OWNER_IDS, intents=discord.Intents.all(),
                activity=discord.Activity(type=discord.ActivityType.playing, name='the game of life'), max_messages=10000,
                allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True, replied_user=False), case_insensitive=True
        )

        self.text_permissions = discord.Permissions(read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, add_reactions=True, external_emojis=True)
        self.voice_permissions = discord.Permissions(
                read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True, add_reactions=True, external_emojis=True, connect=True, speak=True,
                use_voice_activation=True
        )

        self.session = aiohttp.ClientSession()
        self.start_time = time.time()
        self.process = psutil.Process()
        self.socket_stats = collections.Counter()

        self.ERROR_LOG = discord.Webhook.from_url(session=self.session, url=config.ERROR_WEBHOOK_URL)
        self.GUILD_LOG = discord.Webhook.from_url(session=self.session, url=config.GUILD_WEBHOOK_URL)
        self.DMS_LOG = discord.Webhook.from_url(session=self.session,  url=config.DM_WEBHOOK_URL)

        self.first_ready: bool = True

        self.db: Optional[asyncpg.Pool] = None
        self.redis: Optional[aredis.StrictRedis] = None

        self.mystbin: mystbin.Client = mystbin.Client(session=self.session)
        self.ksoft: ksoftapi.Client = ksoftapi.Client(config.KSOFT_TOKEN)
        self.slate: Type[slate.NodePool] = slate.NodePool
        self.spotify: spotify.Client = spotify.Client(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
        self.spotify_http: spotify.HTTPClient = spotify.HTTPClient(client_id=config.SPOTIFY_CLIENT_ID, client_secret=config.SPOTIFY_CLIENT_SECRET)
        self.scheduler: aioscheduler.Manager = aioscheduler.Manager(2)

        self.user_manager: managers.UserManager = managers.UserManager(bot=self)
        self.guild_manager: managers.GuildManager = managers.GuildManager(bot=self)

    async def get_context(self, message: discord.Message, *, cls=context.Context) -> context.Context:
        return await super().get_context(message, cls=cls)

    async def is_owner(self, user: Union[discord.User, discord.Member]) -> bool:
        return user.id in config.OWNER_IDS

    async def process_commands(self, message: discord.Message) -> None:

        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if ctx.command and ctx.command.name in ['play', 'yt-music', 'soundcloud', 'search', 'play-now', 'play-next']:

            content = message.content
            start = content.index(ctx.invoked_with) + len(ctx.invoked_with) + 1
            try:
                end = content.index(" --")
            except ValueError:
                end = len(content)
            query = '"' + content[start:end] + '"'

            content = content[:start] + query + content[end:]

            message = copy.copy(message)
            message.content = re.sub(r"--([^\s]+)\s*", r"--\1 true ", content)

            ctx = await self.get_context(message)

        await self.invoke(ctx)

    async def get_prefix(self, message: discord.Message) -> list[str]:

        if not message.guild:
            return commands.when_mentioned_or(config.PREFIX, 'I-', '')(self, message)

        guild_config = self.guild_manager.get_config(message.guild.id)
        return commands.when_mentioned_or(config.PREFIX, 'I-', *guild_config.prefixes)(self, message)

    async def start(self, token: str, *, reconnect: bool = True) -> None:

        try:
            __log__.debug('[POSTGRESQL] Attempting connection.')
            db = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)
        except Exception as e:
            __log__.critical(f'[POSTGRESQL] Error while connecting.\n{e}\n')
            print(f'\n[POSTGRESQL] Error while connecting: {e}')
            raise ConnectionError
        else:
            __log__.info('[POSTGRESQL] Successful connection.')
            print('\n[POSTGRESQL] Successful connection.')
            self.db = db

        try:
            __log__.debug('[REDIS] Attempting connection')
            redis = aredis.StrictRedis(**config.REDIS)
            await redis.set('connected', 0)
        except (aredis.ConnectionError, aredis.ResponseError) as e:
            __log__.critical(f'[REDIS] Error while connecting.\n{e}\n')
            print(f'[REDIS] Error while connecting: {e}')
            raise ConnectionError()
        else:
            __log__.info('[REDIS] Successful connection.')
            print(f'[REDIS] Successful connection to Redis DB number \'{config.REDIS["db"]}\'. \n')
            self.redis = redis

        for extension in config.EXTENSIONS:
            try:
                self.load_extension(extension)
                __log__.info(f'[EXTENSIONS] Loaded - {extension}')
                print(f'[EXTENSIONS] Loaded - {extension}')
            except commands.ExtensionNotFound:
                __log__.warning(f'[EXTENSIONS] Extension not found - {extension}')
                print(f'\n[EXTENSIONS] Extension not found - {extension}\n')
            except commands.NoEntryPointError:
                __log__.warning(f'[EXTENSIONS] No entry point - {extension}')
                print(f'\n[EXTENSIONS] No entry point - {extension}\n')
            except commands.ExtensionFailed as error:
                __log__.warning(f'[EXTENSIONS] Failed - {extension} - Reason: {traceback.print_exception(type(error), error, error.__traceback__)}')
                print(f'\n[EXTENSIONS] Failed - {extension} - Reason: {error}\n')

        print('')
        await super().start(token=token, reconnect=reconnect)

    async def close(self) -> None:

        __log__.info('[BOT] Closing aiohttp client sessions.')
        print('\n[CS] Closing aiohttp client sessions.')
        await self.session.close()
        await self.ksoft.close()
        await self.spotify.close()
        await self.spotify_http.close()

        __log__.info('[BOT] Closing bot down.')
        print('[BOT] Closing bot down.')

        __log__.info('[BOT] Closing database connection.')
        print('[DB] Closing database connection.')
        await self.db.close()

        __log__.info('[BOT] Bot has shutdown.')
        print('\nBye bye!')
        await super().close()

    #

    async def on_ready(self) -> None:

        if self.first_ready is False:
            return
        self.first_ready = False

        self.add_check(self.command_check)
        self.scheduler.start()

        await self.user_manager.load()
        await self.guild_manager.load()

        for cog in self.cogs.values():
            if hasattr(cog, 'load'):
                await cog.load()

    async def command_check(self, ctx: context.Context) -> Literal[True]:

        if ctx.user_config.blacklisted is True and ctx.command.qualified_name not in {'help', 'support'}:
            raise commands.CheckFailure(f'You are blacklisted from using this bot with the reason:\n\n`{ctx.user_config.blacklisted_reason}`')
        if ctx.guild_config.blacklisted is True and ctx.command.qualified_name not in {'help', 'support'}:
            raise commands.CheckFailure(f'This guild is blacklisted from using this bot with the reason:\n\n`{ctx.guild_config.blacklisted_reason}`')

        needed_permissions = {permission: value for permission, value in self.text_permissions if value is True}
        current_permissions = dict(ctx.channel.permissions_for(ctx.me))
        if not ctx.guild:
            current_permissions['read_messages'] = True

        if ctx.command.cog and ctx.command.cog in {self.get_cog('Music')}:
            if isinstance(ctx.author, discord.Member) and (channel := getattr(ctx.author.voice, 'channel', None)) is not None:
                needed_permissions = {permission: value for permission, value in self.voice_permissions if value is True}
                current_permissions.update({permission: value for permission, value in ctx.me.permissions_in(channel) if value is True})

        if missing := [permissions for permissions, value in needed_permissions.items() if current_permissions[permissions] != value]:
            raise commands.BotMissingPermissions(missing)

        return True
