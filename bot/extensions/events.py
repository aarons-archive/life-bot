# Future
from __future__ import annotations

# Standard Library
import contextlib
import logging
import traceback
from typing import Any

# Packages
import discord
import pendulum
import slate.obsidian
from discord.ext import commands

# My stuff
from core import colours, config, emojis, values
from core.bot import Life
from utilities import custom, enums, exceptions, utils


__log__: logging.Logger = logging.getLogger("extensions.events")

BAD_ARGUMENT_ERRORS = {
    commands.BadArgument:                   "I couldn't convert one of the arguments you passed. Use **{help}** for help.",
    commands.MessageNotFound:               "I couldn't find a message that matches **{argument}**.",
    commands.MemberNotFound:                "I couldn't find a member that matches **{argument}**.",
    commands.GuildNotFound:                 "I couldn't find a server that matches **{argument}**.",
    commands.UserNotFound:                  "I couldn't find a user that matches **{argument}**.",
    commands.ChannelNotFound:               "I couldn't find a channel that matches **{argument}**.",
    commands.ChannelNotReadable:            "I don't have permission to read messages in **{argument.mention}**.",
    commands.BadColourArgument:             "I couldn't find a colour that matches **{argument}**.",
    commands.RoleNotFound:                  "I couldn't find a role that matches **{argument}**.",
    commands.BadInviteArgument:             "That is not a valid invite.",
    commands.EmojiNotFound:                 "I couldn't find an emoji that matches **{argument}**.",
    commands.PartialEmojiConversionFailure: "**{argument}** does not match the emoji format.",
    commands.BadBoolArgument:               "**{argument}** is not a valid true or false value.",
    commands.ThreadNotFound:                "I couldn't find a thread that matches **{argument}**.",
    commands.BadFlagArgument:               "I couldn't convert a value for one of the flags you passed.",
    commands.MissingFlagArgument:           "You missed a value for the **{error.flag.name}** flag.",
    commands.TooManyFlags:                  "You passed too many values to the **{error.flag.name}** flag.",
    commands.MissingRequiredFlag:           "You missed the **{error.flag.name}** flag.",
}

COOLDOWN_BUCKETS = {
    commands.BucketType.default:  "for the whole bot",
    commands.BucketType.user:     "for you",
    commands.BucketType.member:   "for you",
    commands.BucketType.role:     "for your role",
    commands.BucketType.guild:    "for this server",
    commands.BucketType.channel:  "for this channel",
    commands.BucketType.category: "for this channel category",
}

CONCURRENCY_BUCKETS = {
    commands.BucketType.default:  "for all users",
    commands.BucketType.user:     "per user",
    commands.BucketType.member:   "per member",
    commands.BucketType.role:     "per role",
    commands.BucketType.guild:    "per server",
    commands.BucketType.channel:  "per channel",
    commands.BucketType.category: "per channel category",
}

OTHER_ERRORS = {
    commands.TooManyArguments:              "You used too many arguments. Use **{prefix}help {command.qualified_name}** for help.",
    commands.UnexpectedQuoteError:          "There was an unexpected quote character in the arguments you passed.",
    commands.InvalidEndOfQuotedStringError: "There was an unexpected space after a quote character in the arguments you passed.",
    commands.ExpectedClosingQuoteError:     "There is a missing quote character in the arguments you passed.",
    commands.CheckFailure:                  "{error}",
    commands.CheckAnyFailure:               "PUT SOMETHING HERE",
    commands.PrivateMessageOnly:            "This command can only be used in private messages.",
    commands.NoPrivateMessage:              "This command can not be used in private messages.",
    commands.NotOwner:                      "You don't have permission to use this command.",
    commands.MissingRole:                   "You don't have the {error.missing_role.mention} role which is required to run this command.",
    commands.BotMissingRole:                "I don't have the {error.missing_role.mention} role which I require to run this command.",
    commands.NSFWChannelRequired:           "This command can only be run in NSFW channels.",
    commands.DisabledCommand:               "This command is currently disabled.",
    commands.MissingAnyRole:                "You are missing roles required to run this command.",
    commands.BotMissingAnyRole:             "I am missing roles required to run this command.",
}


def setup(bot: Life) -> None:
    bot.add_cog(Events(bot=bot))


class Events(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: custom.Context, error: Any) -> discord.Message | None:

        error = getattr(error, "original", error)

        __log__.error(
            f"Error in command. Error: {type(error)} | Content: {getattr(ctx.message, 'content', None)} | "
            f"Channel: {ctx.channel} ({getattr(ctx.channel, 'id', None)}) | Author: {ctx.author} ({getattr(ctx.author, 'id', None)}) | "
            f"Guild: {ctx.guild} ({getattr(ctx.guild, 'id', None)})"
        )

        if isinstance(error, exceptions.EmbedError):
            await ctx.reply(embed=error.embed)
            return

        if isinstance(error, commands.CommandNotFound):
            await ctx.message.add_reaction(emojis.CROSS)
            return

        if isinstance(error, commands.MissingPermissions):
            permissions = values.NL.join([f"- {permission}" for permission in error.missing_permissions])
            await ctx.reply(
                f"You are missing permissions required to run the command `{ctx.command.qualified_name}` in `{ctx.guild}`.\n```diff\n{permissions}\n```"
            )
            return

        if isinstance(error, commands.BotMissingPermissions):
            permissions = values.NL.join([f"- {permission}" for permission in error.missing_permissions])
            await ctx.try_dm(
                f"I am missing permissions required to run the command `{ctx.command.qualified_name}` in `{ctx.guild}`.\n```diff\n{permissions}\n```"
            )
            return

        #

        message = None

        if isinstance(error, commands.MissingRequiredArgument):
            message = f"You missed the **{error.param.name}** argument. Use **{config.PREFIX}help {ctx.command.qualified_name}** for help."

        elif isinstance(error, commands.BadArgument):
            argument = getattr(error, "argument", None)
            message = BAD_ARGUMENT_ERRORS.get(type(error), "None").format(
                argument=argument,
                help=f"{config.PREFIX}help {ctx.command.qualified_name}",
                error=error
            )

        elif isinstance(error, commands.BadUnionArgument):
            message = f"I couldn't understand the **{error.param.name}** argument. Use **{config.PREFIX}help {ctx.command.qualified_name}** for help."

        elif isinstance(error, commands.BadLiteralArgument):
            message = f"The argument **{error.param.name}** must be one of {', '.join([f'**{arg}**' for arg in error.literals])}."

        elif isinstance(error, commands.CommandOnCooldown):
            message = f"This command is on cooldown **{COOLDOWN_BUCKETS.get(error.type)}**. " \
                      f"You can retry in `{utils.format_seconds(error.retry_after, friendly=True)}`"

        elif isinstance(error, commands.MaxConcurrencyReached):
            message = f"This command is being ran at its maximum of **{error.number} time{'s' if error.number > 1 else ''}** " \
                      f"{CONCURRENCY_BUCKETS.get(error.per)}."

        embed = discord.Embed(colour=colours.RED)

        if message:
            embed.description = f"{emojis.CROSS}  {message}"
            await ctx.reply(embed=embed)

        elif (message := OTHER_ERRORS.get(type(error))) is not None:
            embed.description = f"{emojis.CROSS}  {message.format(command=ctx.command, error=error, prefix=config.PREFIX)}"
            await ctx.reply(embed=embed)

        else:
            await self.handle_traceback(ctx, error)

    async def handle_traceback(self, ctx: custom.Context, exception: Exception) -> None:

        embed = utils.embed(
            colour=colours.RED,
            emoji=emojis.CROSS,
            description=f"Something went wrong! Join my [support server]({values.SUPPORT_LINK}) for help.",
        )
        await ctx.reply(embed=embed)

        message = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        __log__.error(f"Traceback:", exc_info=exception)

        embed = discord.Embed(
            colour=colours.RED,
            description=await utils.safe_content(self.bot.mystbin, ctx.message.content, syntax="python", max_characters=2000),
        ).add_field(
            name="Info:",
            value=f"{f'`Guild:` {ctx.guild} `{ctx.guild.id}`{values.NL}' if ctx.guild else ''}"
                  f"`Channel:` {ctx.channel} `{ctx.channel.id}`\n"
                  f"`Author:` {ctx.author} `{ctx.author.id}`\n"
                  f"`Time:` {utils.format_datetime(pendulum.now(tz='UTC'))}",
        )

        message = await utils.safe_content(self.bot.mystbin, f"```py\n{message}```", syntax="python", max_characters=2000)

        await self.bot.ERROR_LOG.send(embed=embed, username=f"{ctx.author}", avatar_url=utils.avatar(ctx.author))
        await self.bot.ERROR_LOG.send(content=message, username=f"{ctx.author}", avatar_url=utils.avatar(ctx.author))

    # Bot events

    @commands.Cog.listener()
    async def on_socket_event_type(self, event_type: str) -> None:
        self.bot.socket_stats[event_type] += 1

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:

        if before.content == after.content:
            return

        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        __log__.info(f"Bot is now ready. Name: {self.bot.user} | ID: {self.bot.user.id}")

    # Guild logging

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:

        total = len(guild.members)
        bots = sum(1 for member in guild.members if member.bot)
        bots_percent = f"{round((bots / total) * 100, 2)}%"

        embed = discord.Embed(
            colour=colours.GREEN,
            title=f"Joined guild: **{guild}**",
            description=f"`Name:` {guild.name}\n"
                        f"`ID:` {guild.id}\n"
                        f"`Owner:` {guild.owner}\n"
                        f"`Created on:` {utils.format_datetime(guild.created_at)}\n"
                        f"`Joined:` {utils.format_datetime(guild.me.joined_at)}\n"
                        f"`Members:` {total}\n"
                        f"`Bots:` {bots}\n"
                        f"`Bot%:` {bots_percent}",
        ).set_thumbnail(
            url=str(utils.icon(guild))
        )

        __log__.info(
            f"Joined a guild. Name: {guild.name} | ID: {guild.id} | Owner: {guild.owner} | "
            f"Members: {len(guild.members)} | Bots: {bots} | Bots%: {bots_percent}"
        )
        await self.bot.GUILD_LOG.send(embed=embed, avatar_url=str(utils.icon(guild)))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:

        total = len(guild.members)
        bots = sum(1 for member in guild.members if member.bot)
        bots_percent = f"{round((bots / total) * 100, 2)}%"

        embed = discord.Embed(
            colour=colours.RED,
            title=f"Left guild: **{guild}**",
            description=f"`Name:` {guild.name}\n"
                        f"`ID:` {guild.id}\n"
                        f"`Owner:` {guild.owner}\n"
                        f"`Created on:` {utils.format_datetime(guild.created_at)}\n"
                        f"`Joined:` {utils.format_datetime(guild.me.joined_at)}\n"
                        f"`Members:` {total}\n"
                        f"`Bots:` {bots}\n"
                        f"`Bot%:` {bots_percent}",
        ).set_thumbnail(
            url=str(utils.icon(guild))
        )

        __log__.info(
            f"Left a guild. Name: {guild.name} | ID: {guild.id} | Owner: {guild.owner} | "
            f"Members: {len(guild.members)} | Bots: {bots} | Bots%: {bots_percent}"
        )
        await self.bot.GUILD_LOG.send(embed=embed, avatar_url=str(utils.icon(guild)))

    # DM Logging

    @staticmethod
    async def _log_attachments(webhook: discord.Webhook, message: discord.Message) -> None:

        with contextlib.suppress(discord.HTTPException, discord.NotFound, discord.Forbidden):
            for attachment in message.attachments:
                await webhook.send(
                    content=f"Attachment from message with id **{message.id}**:",
                    file=await attachment.to_file(use_cached=True),
                    username=f"{message.author}",
                    avatar_url=utils.avatar(message.author),
                )

    @staticmethod
    async def _log_embeds(webhook: discord.Webhook, message: discord.Message) -> None:

        for embed in message.embeds:
            await webhook.send(
                content=f"Embed from message with id **{message.id}**:",
                embed=embed,
                username=f"{message.author}",
                avatar_url=utils.avatar(message.author),
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:

        if config.ENV == enums.Environment.DEVELOPMENT:
            return

        if message.guild or message.is_system():
            return

        content = await utils.safe_content(self.bot.mystbin, message.content) if message.content else "*No content*"

        embed = discord.Embed(
            colour=colours.GREEN,
            title=f"DM from **{message.author}**:",
            description=content
        ).add_field(
            name="Info:",
            value=f"`Channel:` {message.channel} `{message.channel.id}`\n"
                  f"`Author:` {message.author} `{message.author.id}`\n"
                  f"`Time:` {utils.format_datetime(pendulum.now(tz='UTC'))}\n"
                  f"`Jump:` [Click here]({message.jump_url})",
        ).set_footer(
            text=f"ID: {message.id}"
        )

        __log__.info(f"DM from {message.author} ({message.author.id}) | Content: {content}")
        await self.bot.DMS_LOG.send(embed=embed, username=f"{message.author}", avatar_url=utils.avatar(message.author))

        await self._log_attachments(webhook=self.bot.DMS_LOG, message=message)
        await self._log_embeds(webhook=self.bot.DMS_LOG, message=message)
