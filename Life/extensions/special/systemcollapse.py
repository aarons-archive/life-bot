import discord
from discord.ext import commands

from core.bot import Life


SYSTEMCOLLAPSE_GUILD_ID = 350247597862158347

VERIFIED_ROLE_ID = 768226910903468033
CONTENT_ROLE_ID = 768620502297083915
EVENTS_ROLE_ID = 768620661563850783
ANNOUNCEMENTS_ROLE_ID = 768620823480893481

VERIFY_CHANNEL_ID = 768233187704176651
VERIFY_MESSAGE_ID = 768904890042548245

REACTION_ROLE_CHANNEL_ID = 768619511372841020
REACTION_ROLE_MESSAGE_ID = 768907337888956457

WAVE_EMOJI = "\U0001f44b"
BANGBANG_EMOJI = "\U0000203c\U0000fe0f"
PARTY_EMOJI = "\U0001f973"
FORWARD_EMOJI = "\U000025b6\U0000fe0f"


def setup(bot: Life) -> None:
    bot.add_cog(SystemCollapse(bot=bot))


class SystemCollapse(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:

        if payload.guild_id != SYSTEMCOLLAPSE_GUILD_ID:
            return

        guild = self.bot.get_guild(SYSTEMCOLLAPSE_GUILD_ID)
        member = guild.get_member(payload.user_id)

        if payload.channel_id == VERIFY_CHANNEL_ID and payload.message_id == VERIFY_MESSAGE_ID:

            if payload.emoji.name == WAVE_EMOJI:
                await member.add_roles(discord.Object(VERIFIED_ROLE_ID))

        elif payload.channel_id == REACTION_ROLE_CHANNEL_ID and payload.message_id == REACTION_ROLE_MESSAGE_ID:

            if payload.emoji.name == PARTY_EMOJI:
                await member.add_roles(discord.Object(EVENTS_ROLE_ID))
            elif payload.emoji.name == BANGBANG_EMOJI:
                await member.add_roles(discord.Object(ANNOUNCEMENTS_ROLE_ID))
            elif payload.emoji.name == FORWARD_EMOJI:
                await member.add_roles(discord.Object(CONTENT_ROLE_ID))

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent) -> None:

        if payload.guild_id != SYSTEMCOLLAPSE_GUILD_ID:
            return

        guild = self.bot.get_guild(SYSTEMCOLLAPSE_GUILD_ID)
        member = guild.get_member(payload.user_id)

        if payload.channel_id == VERIFY_CHANNEL_ID and payload.message_id == VERIFY_MESSAGE_ID:

            if payload.emoji.name == WAVE_EMOJI:
                await member.remove_roles(discord.Object(VERIFIED_ROLE_ID))

        elif payload.channel_id == REACTION_ROLE_CHANNEL_ID and payload.message_id == REACTION_ROLE_MESSAGE_ID:

            if payload.emoji.name == PARTY_EMOJI:
                await member.remove__roles(discord.Object(EVENTS_ROLE_ID))
            elif payload.emoji.name == BANGBANG_EMOJI:
                await member.remove_roles(discord.Object(ANNOUNCEMENTS_ROLE_ID))
            elif payload.emoji.name == FORWARD_EMOJI:
                await member.remove_roles(discord.Object(CONTENT_ROLE_ID))
