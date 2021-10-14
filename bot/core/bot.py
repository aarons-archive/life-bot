# Future
from __future__ import annotations

# Standard Library
import collections
import copy
import logging
import re
import time
import traceback
from typing import Any, Type

# Packages
import aiohttp
import aioredis
import aioscheduler
import asyncpg
import discord
import mystbin
import psutil
import topgg
from discord.ext import commands, ipc
# noinspection PyUnresolvedReferences
from discord.ext.alternatives import converter_dict
from pendulum.tz.timezone import Timezone
from slate import obsidian

# My stuff
import utilities.utils
from core import config, values
from utilities import checks, converters, custom, enums, managers, objects, utils


__log__: logging.Logger = logging.getLogger("bot")

CONVERTERS = {
    objects.Reminder:         converters.ReminderConverter,
    enums.ReminderRepeatType: converters.EnumConverter(enums.ReminderRepeatType, "Repeat type"),
    enums.NotificationType:   converters.EnumConverter(enums.NotificationType, "Notification type"),
    Timezone:                 converters.TimezoneConverter,
}


class Life(commands.AutoShardedBot):

    converters: dict[Type[Any], Type[Any]]

    def __init__(self) -> None:
        super().__init__(
            status=discord.Status.dnd,
            activity=discord.Activity(type=discord.ActivityType.playing, name="aaaaa!"),
            allowed_mentions=discord.AllowedMentions(everyone=False, users=True, roles=True, replied_user=False),
            help_command=custom.HelpCommand(),
            intents=discord.Intents.all(),
            command_prefix=self.get_prefix,
            case_insensitive=True,
            owner_ids=config.OWNER_IDS,
        )
        self._BotBase__cogs = commands.core._CaseInsensitiveDict()

        self.session: aiohttp.ClientSession = aiohttp.ClientSession()
        self.process: psutil.Process = psutil.Process()
        self.socket_stats: collections.Counter = collections.Counter()

        self.ERROR_LOG: discord.Webhook = discord.Webhook.from_url(session=self.session, url=config.ERROR_WEBHOOK_URL)
        self.GUILD_LOG: discord.Webhook = discord.Webhook.from_url(session=self.session, url=config.GUILD_WEBHOOK_URL)
        self.DMS_LOG: discord.Webhook = discord.Webhook.from_url(session=self.session, url=config.DM_WEBHOOK_URL)

        self.db: asyncpg.Pool = utils.MISSING
        self.redis: aioredis.Redis | None = None

        self.scheduler: aioscheduler.Manager = aioscheduler.Manager()
        self.mystbin: mystbin.Client = mystbin.Client(session=self.session)
        self.slate: obsidian.NodePool[Life, custom.Context, custom.Player] = obsidian.NodePool()
        self.ipc: ipc.Server = ipc.Server(bot=self, secret_key=config.SECRET_KEY, multicast_port=config.MULTICAST_PORT)

        self.topgg: topgg.DBLClient | None = topgg.DBLClient(
            bot=self,
            token=config.TOPGG,
            autopost=True
        ) if config.ENV is enums.Environment.PRODUCTION else None

        self.user_manager: managers.UserManager = managers.UserManager(bot=self)
        self.guild_manager: managers.GuildManager = managers.GuildManager(bot=self)

        self.first_ready: bool = True
        self.start_time: float = time.time()

        self.add_check(checks.global_check, call_once=True)  # type: ignore

        self.converters |= CONVERTERS

    #

    async def get_prefix(self, message: discord.Message) -> list[str]:

        if not message.guild:
            return commands.when_mentioned_or(config.PREFIX, "I-", "")(self, message)

        guild_config = await self.guild_manager.get_config(message.guild.id)
        return commands.when_mentioned_or(config.PREFIX, "I-", *guild_config.prefixes)(self, message)

    async def process_commands(self, message: discord.Message) -> None:

        if message.author.bot:
            return

        ctx = await self.get_context(message)

        if ctx.command and ctx.command.name in values.FLAG_COMMANDS and ctx.invoked_with:

            content = message.content
            start = content.index(ctx.invoked_with) + len(ctx.invoked_with) + 1
            try:
                end = content.index(" --")
            except ValueError:
                end = len(content)

            new_message = copy.copy(message)
            new_content = (content[:start] + ('"' + content[start:end] + '"') + content[end:]).replace('""', "")
            new_message.content = re.sub(r"--([^\s]+)\s*", r"--\1 true ", new_content)

            ctx = await self.get_context(new_message)

        await self.invoke(ctx)

    async def get_context(self, message: discord.Message, *, cls: Type[commands.Context] = custom.Context) -> commands.Context:
        return await super().get_context(message=message, cls=cls)

    async def is_owner(self, user: discord.User | discord.Member) -> bool:
        return user.id in config.OWNER_IDS

    #

    async def start(self, token: str, *, reconnect: bool = True) -> None:

        try:
            __log__.debug("[POSTGRESQL] Attempting connection.")
            db = await asyncpg.create_pool(**config.POSTGRESQL, max_inactive_connection_lifetime=0)
        except Exception as e:
            __log__.critical(f"[POSTGRESQL] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[POSTGRESQL] Successful connection.")
            self.db = db

        try:
            __log__.debug("[REDIS] Attempting connection.")
            redis = aioredis.from_url(url=config.REDIS, decode_responses=True, retry_on_timeout=True)
            await redis.ping()
        except (aioredis.ConnectionError, aioredis.ResponseError) as e:
            __log__.critical(f"[REDIS] Error while connecting.\n{e}\n")
            raise ConnectionError()
        else:
            __log__.info("[REDIS] Successful connection.")
            self.redis = redis

        for extension in config.EXTENSIONS:
            try:
                self.load_extension(extension)
                __log__.info(f"[EXTENSIONS] Loaded - {extension}")
            except commands.ExtensionNotFound:
                __log__.warning(f"[EXTENSIONS] Extension not found - {extension}")
            except commands.NoEntryPointError:
                __log__.warning(f"[EXTENSIONS] No entry point - {extension}")
            except commands.ExtensionFailed as error:
                __log__.warning(f"[EXTENSIONS] Failed - {extension} - Reason: {traceback.print_exception(type(error), error, error.__traceback__)}")

        await super().start(token=token, reconnect=reconnect)

    async def close(self) -> None:

        await self.session.close()

        if self.db:
            await self.db.close()
        if self.redis:
            await self.redis.close()

        await super().close()

    #

    async def on_ready(self) -> None:

        if self.first_ready is True:
            self.first_ready = False

        self.scheduler.start()

        await self.cogs["Voice"].load()  # type: ignore

    @staticmethod
    async def on_ipc_error(endpoint: Any, error: Any) -> Any:
        print(endpoint, "raised", error)
