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
#

import collections
import logging
import time
import typing

import aiohttp
import aredis
import asyncpg
import discord
import psutil
from discord.ext import commands

from config import config
from managers import guild_manager, user_manager
from utilities import context, help, objects, utils


class Life(commands.AutoShardedBot):

    def __init__(self, loop) -> None:
        super().__init__(command_prefix=self.get_prefix, reconnect=True, help_command=help.HelpCommand(), loop=loop,
                         activity=discord.Streaming(name=f'{config.Config(bot=self).prefix}help', url='https://www.twitch.tv/axelancerr'),
                         intents=discord.Intents(guilds=True, members=True, bans=False, emojis=False, integrations=False, webhooks=False, invites=False, voice_states=True,
                                                 presences=True, messages=True, reactions=True, typing=False)
                         )

        self.text_permissions = discord.Permissions(read_messages=True, send_messages=True, embed_links=True, attach_files=True, read_message_history=True,
                                                    add_reactions=True, external_emojis=True)
        self.voice_permissions = discord.Permissions(connect=True, speak=True, use_voice_activation=True)

        self.session = aiohttp.ClientSession(loop=self.loop)
        self.log = logging.getLogger(name='bot')
        self.config = config.Config(bot=self)
        self.utils = utils.Utils(bot=self)

        self.guild_manager = guild_manager.GuildConfigManager(bot=self)
        self.user_manager = user_manager.UserConfigManager(bot=self)

        self.socket_stats = collections.Counter()
        self.process = psutil.Process()
        self.start_time = time.time()

        self.mentions_dms_webhook = discord.Webhook.from_url(url=self.config.mentions_dms_url, adapter=discord.AsyncWebhookAdapter(self.session))
        self.logging_webhook = discord.Webhook.from_url(url=self.config.logging_url, adapter=discord.AsyncWebhookAdapter(self.session))
        self.errors_webhook = discord.Webhook.from_url(url=self.config.errors_url, adapter=discord.AsyncWebhookAdapter(self.session))

        self.invite = f'https://discord.com/oauth2/authorize?client_id=628284183579721747&scope=bot&permissions=37080128'
        self.github = f'https://github.com/Axelancerr/Life'
        self.dashboard = f'https://dashboard.mrrandom.xyz/'
        self.support = f'https://discord.gg/xP8xsHr'

        self.commands_not_allowed_dms = {
            'join', 'play', 'leave', 'skip', 'pause', 'unpause', 'seek', 'volume', 'now_playing', 'queue', 'queue detailed', 'queue loop', 'queue sort', 'queue shuffle',
            'queue remove', 'queue history', 'queue history detailed', 'queue history clear', 'queue clear', 'queue reverse', 'queue move', 'lavalink',

            'icon', 'banner', 'splash', 'server', 'channels', 'member',

            'tag', 'tag alias', 'tag list', 'tag edit', 'tag create', 'tag transfer', 'tag all', 'prefix search', 'tag delete', 'tag info', 'tag claim', 'tag raw',

            'settings prefix add', 'settings prefix remove', 'settings prefix clear', 'settings colour set', 'settings colour clear'
        }

        self.first_ready = True

        self.wolframalpha = None
        self.http_client = None
        self.http_server = None
        self.lavalink = None
        self.imaging = None
        self.ksoft = None
        self.redis = None
        self.db = None

    async def get_context(self, message: discord.Message, *, cls=context.Context) -> context.Context:
        return await super().get_context(message, cls=cls)

    async def is_owner(self, person: typing.Union[discord.User, discord.Member]) -> bool:
        return person.id in self.config.owner_ids

    async def can_run_commands(self, ctx: context.Context) -> bool:

        if not ctx.guild and ctx.command.qualified_name in self.commands_not_allowed_dms:
            raise commands.NoPrivateMessage()

        if ctx.user_config.blacklisted is True and ctx.command.qualified_name not in {'help', 'support'}:
            raise commands.CheckFailure(f'You are blacklisted from using this bot with the reason:\n\n`{ctx.user_config.blacklisted_reason}`')
        elif ctx.guild_config.blacklisted is True and ctx.command.qualified_name not in {'help', 'support'}:
            raise commands.CheckFailure(f'This guild is blacklisted from using this bot with the reason:\n\n`{ctx.guild_config.blacklisted_reason}`')

        needed_permissions = {permission: value for permission, value in dict(self.text_permissions).items() if value is True}
        current_permissions = dict(ctx.channel.permissions_for(ctx.guild.me)) if ctx.guild else dict(ctx.channel.me.permissions_in(ctx.channel))

        if ctx.command.cog and ctx.command.cog == self.get_cog('Music') and hasattr(ctx.author, 'voice') and ctx.author.voice is not None:
            needed_permissions.update({permission: value for permission, value in dict(self.voice_permissions).items() if value is True})
            current_permissions.update({permission: value for permission, value in getattr(ctx.author.voice, 'channel', None).permissions_for(ctx.guild.me) if value is True})

        missing = [permissions for permissions, value in needed_permissions.items() if current_permissions[permissions] != value]
        if missing:
            raise commands.BotMissingPermissions(missing)

        return True

    async def get_prefix(self, message: discord.Message) -> list:

        if not message.guild:
            return commands.when_mentioned_or(self.config.prefix, '')(self, message)

        guild_config = self.guild_manager.get_guild_config(guild_id=message.guild.id)
        if isinstance(guild_config, objects.DefaultGuildConfig):
            return commands.when_mentioned_or(self.config.prefix)(self, message)

        return commands.when_mentioned_or(self.config.prefix, *guild_config.prefixes)(self, message)

    async def on_ready(self) -> None:

        if self.first_ready is False:
            return

        self.first_ready = False
        await self.load()

    async def load(self) -> None:

        await self.guild_manager.load()
        await self.user_manager.load()

        for cog in self.cogs.values():
            if hasattr(cog, 'load'):
                await cog.load()

    async def start(self, *args, **kwargs) -> None:

        try:
            db = await asyncpg.create_pool(**self.config.postgresql)
        except Exception as e:
            print(f'\n[POSTGRESQL] An error occurred while connecting to PostgreSQL: {e}')
        else:
            print(f'\n[POSTGRESQL] Connected to the PostgreSQL database.')
            self.db = db

        try:
            redis = aredis.StrictRedis(**self.config.redis)
        except aredis.ConnectionError:
            print(f'[REDIS] An error occurred while connecting to Redis.\n')
        else:
            print(f'[REDIS] Connected to Redis.\n')
            self.redis = redis

        for extension in self.config.extensions:
            try:
                self.load_extension(extension)
                print(f'[EXTENSIONS] Loaded - {extension}')
            except commands.ExtensionNotFound:
                print(f'[EXTENSIONS] Extension not found - {extension}')
            except commands.NoEntryPointError:
                print(f'[EXTENSIONS] No entry point - {extension}')
            except commands.ExtensionFailed as error:
                print(f'[EXTENSIONS] Failed - {extension} - Reason: {error}')

        self.add_check(self.can_run_commands)
        await super().start(*args, **kwargs)

    async def close(self) -> None:

        print("\n[BOT] Closing bot down.")

        print("[DB] Closing database connection.")
        await self.db.close()

        print("[CS] Closing aiohttp client session.")
        await self.session.close()

        print("Bye bye!")
        await super().close()
