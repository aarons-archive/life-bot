from discord.ext import commands
from .utils import imageOps
import discord
import time


class Images(commands.Cog):
    """
    Image manipulation commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="imginfo")
    async def imginfo(self, ctx, *, member: discord.Member = None):
        """
        Generate an image with information about you and your account.
        """

        if not member:
            member = ctx.author

        # Check if the user has a account
        if not await self.bot.db.fetchrow("SELECT key FROM user_config WHERE key = $1", member.id):
            return await ctx.send("You/the target does not have an account.")

        # Get the members info.
        data = await self.bot.db.fetchrow("SELECT * FROM user_config WHERE key = $1", member.id)

        # Start typing and timer.
        start = time.perf_counter()
        await ctx.trigger_typing()

        # Get the users avatar.
        avatar_url = str(member.avatar_url_as(format="png", size=1024))
        avatar_bytes = await imageOps.get_image(self.bot, avatar_url)

        # Generate image.
        imginfo = await self.bot.loop.run_in_executor(None, imageOps.do_imageinfo, data, member, avatar_bytes)

        # Send image.
        await ctx.send(file=discord.File(filename=f"{member.id}_imginfo.png", fp=imginfo))

        # End timer and log how long operation took.
        end = time.perf_counter()
        return await ctx.send(f"That took {end - start:.3f}sec to complete")


def setup(bot):
    bot.add_cog(Images(bot))
