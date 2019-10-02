from discord.ext import commands
from .utils import imaging
import asyncpg
import discord
import os
import re


class Accounts(commands.Cog):
    """
    Account commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create")
    async def create(self, ctx):
        """
        Create an account
        """

        # Try to create an account, accept error if they already have one.
        try:
            await self.bot.db.execute(f"INSERT INTO accounts VALUES ($1, 'bg_default', 1000, 1000)", ctx.author.id)
            return await ctx.send(f"Account created with ID `{ctx.author.id}`")
        except asyncpg.UniqueViolationError:
            return await ctx.send("You already have an account.")

    @commands.command(name="delete")
    async def delete(self, ctx):
        """
        Delete your account.
        """

        # Check if the user has an account.
        data = await self.bot.db.fetchrow("SELECT * FROM accounts WHERE id = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account.")

        # The user has an account, so delete it.
        await self.bot.db.execute(f"DELETE FROM accounts WHERE id = $1", ctx.author.id)
        return await ctx.send("Deleted your account.")

    @commands.command(name="background", aliases=["bg"])
    async def background(self, ctx, background: str = None):
        """
        Display your background or change it.

        `background`: If this parameter is given, your background will be changed to the image at the URL or the pre-existing image.
        """

        # Check if the user has an account.
        data = await self.bot.db.fetchrow("SELECT * FROM accounts WHERE id = $1", ctx.author.id)
        if not data:
            return await ctx.send(f"You don't have an account. Use `{ctx.prefix}create` to make one.")

        # Check if the user has not attached any images/has not provided a link.
        if not background and not ctx.message.attachments:
            return await ctx.send(content=f"Your current background is `{data['background']}`.", file=discord.File(filename=f"{data['background']}.png", fp=f"files/images/backgrounds/{data['background']}.png"))

        # if the user passed a string
        if background:
            # If what the user entered is a valid background.
            if os.path.isfile(f"files/images/backgrounds/{background}.png"):
                await self.bot.db.execute(f"UPDATE accounts SET background = $1 WHERE id = $2", background, ctx.author.id)
                return await ctx.send(f"Your background was changed from `{data['background']}` to `{background}`.")

            # If what the user passed was a url.
            re_url = re.compile("https?://(?:www\.)?.+/?")
            check = re_url.match(background)
            if check is False:
                return await ctx.send("That was not a valid URL.")

            # Check if it has a png or jpeg extension.
            if not background.endswith((".jpg", ".jpeg", ".png")):
                return await ctx.send("That was not a valid URL. It must be a PNG or JPEG image.")

            # Get the image, resize it, and save it.
            background_bytes = await imaging.get_image(self.bot, background)
            background_resized = await self.bot.loop.run_in_executor(None, imaging.resize_image, background_bytes, 1000, 1000)
            background_resized.save(f"files/images/backgrounds/{ctx.author.id}.png")

            # Set the users background to that image.
            await self.bot.db.execute(f"UPDATE accounts SET background = $1 WHERE id = $2", str(ctx.author.id), ctx.author.id)
            return await ctx.send(f"Your background was changed from `{data['background']}` to `{ctx.author.id}`.")

        # If the user attached something to the message.
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url

            # If the attachemnts url does not end in .png or .jpeg
            if not url.endswith((".jpg", ".jpeg", ".png")):
                return await ctx.send("That was not a valid attachment. It must be a PNG or JPEG image.")

            # Get the image, resize it, and save it.
            background_bytes = await imaging.get_image(self.bot, url)
            background_resized = await self.bot.loop.run_in_executor(None, imaging.resize_image, background_bytes, 1000, 1000)
            background_resized.save(f"files/images/backgrounds/{ctx.author.id}.png")

            # Set the users background to that image.
            await self.bot.db.execute(f"UPDATE accounts SET background = $1 WHERE id = $2", str(ctx.author.id), ctx.author.id)
            return await ctx.send(f"Your background was changed from `{data['background']}` to `{ctx.author.id}`.")


def setup(bot):
    bot.add_cog(Accounts(bot))
