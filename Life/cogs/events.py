import traceback

import discord
from discord.ext import commands

from cogs.utilities import exceptions


class Events(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        self.bot.log_channel = self.bot.get_channel(697324016658022441)
        self.bot.dm_channel = self.bot.get_channel(714307639609131018)
        self.bot.mention_channel = self.bot.get_channel(714601090771058719)

        print(f'\n[BOT] The bot is now ready. Name: {self.bot.user} | ID: {self.bot.user.id}\n')
        self.bot.log.info(f'Bot is now ready. Name: {self.bot.user} | ID: {self.bot.user.id}')

        for guild in self.bot.guilds:
            if guild.id in self.bot.guild_blacklist:
                await guild.leave()
            continue

        await self.bot.change_presence(activity=self.bot.activity)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):

        embed = discord.Embed(colour=discord.Colour.gold())
        embed.set_thumbnail(url=self.bot.utils.guild_icon(guild))
        embed.title = f'Joined a guild'
        embed.description = f'**Name:** {guild.name}\n**ID:** {guild.id}\n**Owner:** {guild.owner}'

        self.bot.log.info(f'Joined a guild. Name: {guild.name} | ID: {guild.id} | Owner: {guild.owner}')
        await self.bot.log_channel.send(embed=embed)

        if guild.id in self.bot.guild_blacklist.keys():
            return await guild.leave()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):

        embed = discord.Embed(colour=discord.Colour.gold())
        embed.set_thumbnail(url=self.bot.utils.guild_icon(guild))
        embed.title = f'Left a {"blacklisted " if guild.id in self.bot.guild_blacklist.keys() else ""}guild'
        embed.description = f'**Name:** {guild.name}\n**ID:** {guild.id}\n**Owner:** {guild.owner}'

        self.bot.log.info(f'{embed.title}. Name: {guild.name} | ID: {guild.id} | Owner: {guild.owner}')
        return await self.bot.log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        ctx = await self.bot.get_context(message)

        if self.bot.user in message.mentions:

            guild = f'**Guild:** {ctx.guild}\n' if ctx.guild else ''
            guild_id = f'**Guild ID:** {ctx.guild.id}\n' if ctx.guild else ''
            channel = f'#{ctx.channel}' if isinstance(ctx.channel, discord.TextChannel) else ctx.channel
            info = f'{guild}{guild_id}**Channel:** {channel}\n**Channel ID:** {ctx.channel.id}'

            embed = discord.Embed(colour=discord.Colour.gold())
            embed.set_author(name=f'Mentioned by {ctx.author}', icon_url=self.bot.utils.member_avatar(ctx.author))
            embed.description = f'{message.content}'
            embed.add_field(name='**Info:**', value=info)
            await self.bot.mention_channel.send(embed=embed)

        if message.guild is None:

            embed = discord.Embed(colour=discord.Colour.gold())
            embed.set_author(name=f'DM from {ctx.author}', icon_url=self.bot.utils.member_avatar(ctx.author))

            embed.description = f'{message.content}'
            embed.add_field(name='**Info:**', value=f'**Channel:** {ctx.channel}\n**Channel ID:** {ctx.channel.id}')
            await self.bot.dm_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):

        if before.author.bot:
            return

        if before.content == after.content:
            return

        await self.bot.process_commands(after)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, 'original', error)
        command = ctx.command
        prefix = self.bot.config.PREFIX

        error_messages = {
            exceptions.BotNotReadyError: f'The bot is not ready yet.',
            exceptions.ArgumentError: f'{error}',
            commands.CheckFailure: f'{error}',
            exceptions.LifePlaylistError: f'{error}',
            exceptions.LifeVoiceError: f'{error}',
            commands.TooManyArguments: f'You used too many parameters for the command `{command}`. '
                                       f'Use `{prefix}help {command}` for more information on what parameters to use.',
            commands.BadArgument: f'I was unable to understand a parameter that you used for the command `{command}`. '
                                  f'Use `{prefix}help {command}` for more information on what parameters to use.',
            commands.BadUnionArgument: f'I was unable to understand a parameter that you used for the command '
                                       f'`{command}`. Use `{prefix}help {command}` for more information on what '
                                       f'parameters to use.',
            commands.NoPrivateMessage: f'The command `{command}` can not be used in private messages.',
            commands.NotOwner: f'The command `{command}` is owner only.',
            commands.NSFWChannelRequired: f'The command `{command}` can only be ran in a NSFW channel.',
            commands.DisabledCommand: f'The command `{command}` has been disabled.',
        }

        error_message = error_messages.get(type(error))

        if isinstance(error, commands.MissingRequiredArgument):
            error_message = f'You missed the `{error.param.name}` parameter for the command `{command}`. ' \
                            f'Use `{prefix}help {command}` for more information on what parameters to use.'

        elif isinstance(error, commands.MissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            error_message = f'You are missing the following permissions required to run the command ' \
                            f'`{command}`.\n{permissions}'

        elif isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join([f'> {permission}' for permission in error.missing_perms])
            error_message = f'I am missing the following permissions required to run the command ' \
                            f'`{command}`.\n{permissions}'

        elif isinstance(error, commands.CommandOnCooldown):
            cooldowns = {
                commands.BucketType.default: f'The command `{command}` is on cooldown for the whole bot.',
                commands.BucketType.user: f'The command `{command}` is on cooldown for you.',
                commands.BucketType.guild: f'The command `{command}` is on cooldown for this server.',
                commands.BucketType.channel: f'The command `{command}` is on cooldown for this channel.',
                commands.BucketType.member: f'The command `{command}` is on cooldown for you.',
                commands.BucketType.category: f'The command `{command}` is on cooldown for this channel category.',
                commands.BucketType.role: f'The command `{command}` is on cooldown for your role.'
            }
            error_message = f'{cooldowns[error.cooldown.type]} You can retry in ' \
                            f'`{self.bot.utils.format_time(error.retry_after, friendly=True)}`'

        elif isinstance(error, commands.MaxConcurrencyReached):
            cooldowns = {
                commands.BucketType.default: f'.',
                commands.BucketType.user: f' per user.',
                commands.BucketType.guild: f' per guild.',
                commands.BucketType.channel: f' per channel.',
                commands.BucketType.member: f' per member.',
                commands.BucketType.category: f' per channel category.',
                commands.BucketType.role: f' per role.'
            }
            error_message = f'The command `{command}` is already being ran at its maximum of ' \
                            f'{error.number} time(s){cooldowns[error.per]} Retry a bit later.'

        elif isinstance(error, commands.CommandNotFound):
            return

        if error_message:
            try:
                return await ctx.send(error_message)
            except discord.Forbidden:
                try:
                    return await ctx.author.send(error_message)
                except discord.Forbidden:
                    return

        traceback.print_exception(type(error), error, error.__traceback__)

    @commands.Cog.listener()
    async def on_command(self, ctx):

        self.bot.log.info(f'Command used. Command: {ctx.command.qualified_name} | '
                          f'Guild: {ctx.guild} | Channel: {ctx.channel} | Author:  {ctx.author}')

        if ctx.author.id in self.bot.owner_ids:
            ctx.command.reset_cooldown(ctx)

    @commands.Cog.listener()
    async def on_socket_response(self, msg):

        event = msg.get('t', 'None')
        if event is not None:
            self.bot.socket_stats[event] += 1


def setup(bot):
    bot.add_cog(Events(bot))
