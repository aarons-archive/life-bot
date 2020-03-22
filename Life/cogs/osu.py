
import typing

import discord
from discord.ext import commands

import aiOsu


class Osu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.osu = aiOsu.Client(token=self.bot.config.OSU_TOKEN)

    @commands.group(name="osu", invoke_without_command=True)
    async def osu(self, ctx):
        """
        Base command for osu! api integration.
        """

        return await ctx.send(f"Please choose a valid subcommand. Use `{self.bot.config.DISCORD_PREFIX}help osu` for a list of commands.")

    @osu.command(name="user")
    async def osu_user(self, ctx, user: typing.Union[int, str], mode: str = "osu"):
        """
        Display an osu! users stats.

        `user`: The users name or id.
        `mode`: The mode to fetch the users stats of, can be `osu`, `taiko`, `catchthebeat` or `mania`
        """

        if mode.lower() not in self.bot.osu.valid_modes.keys():
            return await ctx.send("That was not a valid mode, please choose `osu`, `taiko`, `catchthebeat` or `mania`'")

        users = await self.bot.osu.get_user(user=user, mode=mode.lower())

        if not users:
            return await ctx.send(f"I could not find a user with the name or id: `{user}`")

        embeds = []
        for user in users:
            embed = discord.Embed(
                color=discord.Color.gold(),
                title=f"{user.name}'s osu! stats",
                url=f"https://osu.ppy.sh/users/{user.id}",
            )
            embed.set_thumbnail(url=f"https://s.ppy.sh/a/{user.id}")
            embed.set_footer(text=f"ID: {user.id}")
            embed.add_field(name="Account stats:", value=f"**Name:** {user.name} \n**Country:** {user.country} \n"
                                                         f"**Join date:** {user.join_date.strftime('%A %d %B %Y at %H:%M')}", inline=False)
            embed.add_field(name=f"Mode stats ({mode}): ", value=f"**Time played:** {self.bot.utils.format_time(user.total_seconds_played, friendly=True)} \n"
                                                                 f"**Accuracy:** {round(user.accuracy, 2)}% \n**Play count:** {user.play_count:,} \n"
                                                                 f"**Level:** {round(user.level, 2):,} \n**PP:** {round(user.pp_raw):,} \n"
                                                                 f"**Country rank:** #{user.pp_country_rank:,} \n **Overall rank:** #{user.pp_rank:,} \n"
                                                                 f"**Ranked score:** {user.ranked_score:,} \n**Total score:** {user.total_score:,} \n"
                                                                 f"**Total SSH:** {user.total_ssh} \n**Total SS:** {user.total_ss} \n"
                                                                 f"**Total SH:** {user.total_sh} \n **Total S:** {user.total_s} \n"
                                                                 f"**Total A:** {user.total_a}")
            embeds.append(embed)
        return await ctx.paginate_embeds(entries=embeds)


def setup(bot):
    bot.add_cog(Osu(bot))
