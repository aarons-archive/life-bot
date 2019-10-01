from discord.ext import commands
from .utils import imageOps
import asyncpg
import discord
import re
import os


class Accounts(commands.Cog):
    """
    Account commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="account", aliases=["profile"], invoke_without_command=True)
    async def account(self, ctx):
        """
        Get information about your account.
        """

        # Check if the user has an account.
        data = await self.bot.db.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")

        # Send information.
        embed = discord.Embed(
            color=discord.Color.green(),
            title=f"Information about {ctx.author.name}'s account.",
        )
        embed.add_field(name=f"Configuration:", value=f"Background: {data['background']}", inline=False)
        embed.add_field(name=f"Economy information:", value=f"Bank: £{data['bank']}\n"
                                                            f"Cash: £{data['cash']}\n", inline=False)
        embed.add_field(name=f"Economy information:", value=f"Timezone: {data['timezone']}\n"
                                                            f"Votes: {data['vote_count']}\n", inline=False)
        return await ctx.send(embed=embed)

    @account.command(name="create")
    async def create_account(self, ctx):
        """
        Create an account.
        """

        # Try to create an account, except error if they already have one.
        try:
            await self.bot.db.execute(f"INSERT INTO user_config VALUES ($1, 'bg_default', NULL, False, False, 0, 1000, 1000)", ctx.author.id)
            return await ctx.send(f"Account created with ID `{ctx.author.id}`")
        except asyncpg.UniqueViolationError:
            return await ctx.send("You already have an account.")

    @account.command(name="delete")
    async def delete_account(self, ctx):
        """
        Delete your account.
        """

        # Check if the user has an account.
        data = await self.bot.db.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account.")

        # The user has an account, so delete it.
        await self.bot.db.execute(f"DELETE FROM user_config WHERE key = $1", ctx.author.id)
        return await ctx.send("Deleted your account.")

    @commands.command(name="background", aliases=["bg"])
    async def background(self, ctx):
        """
        Get your current background.
        """

        # Check if the user has an account.
        data = await self.bot.db.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")
        # Get current background and upload picture of it.
        return await ctx.send(content=f"Your current background is `{data['background']}`.", file=discord.File(filename=f"{data['background']}.png", fp=f"files/images/backgrounds/{data['background']}.png"))

    @commands.command(name="background_change", aliases=["bgc"])
    async def background_change(self, ctx, new_background: str = None):
        """
        Change your background to the one specified.

        `new_background`: This can be a pre-existing background as seen in `mb bgl`, a url or an attachment.
        """

        # Check if the user has an account.
        data = await self.bot.db.fetchrow("SELECT * FROM user_config WHERE key = $1", ctx.author.id)
        if not data:
            return await ctx.send("You don't have an account. Use `mb account create` to make one.")

        # Check if the user has not attached any images/has not provided a link.
        if not new_background and not ctx.message.attachments:
            return await ctx.send("You have to attach an image or provide an image URL to use this command.")

        # if the user passed a string
        if new_background:

            # If what the user entered is a valid background.
            if os.path.isfile(f"files/images/backgrounds/{new_background}.png"):
                await self.bot.db.execute(f"UPDATE user_config SET background = $1 WHERE key = $2", new_background, ctx.author.id)
                return await ctx.send(f"Your background was changed from `{data['background']}` to `{new_background}`.")

            # If what the user passed was a url.
            re_url = re.compile("https?://(?:www\.)?.+/?")
            check = re_url.match(new_background)
            # Check if it as acctually a url.
            if check is False:
                return await ctx.send("That was not a valid URL.")

            # Check if it has a png or jpeg extension.
            if not new_background.endswith((".jpg", ".jpeg", ".png")):
                return await ctx.send("That was not a valid URL. It must be a PNG or JPEG image.")

            # Get the image, resize it, and save it.
            background_bytes = await imageOps.get_image(self.bot, new_background)
            background_resized = await self.bot.loop.run_in_executor(None, imageOps.resize_image, background_bytes, 1000, 1000)
            background_resized.save(f"files/images/backgrounds/{ctx.author.id}.png")

            # Set the users background to that image.
            await self.bot.db.execute(f"UPDATE user_config SET background = $1 WHERE key = $2", str(ctx.author.id), ctx.author.id)
            return await ctx.send(f"Your background was changed from `{data['background']}` to `{ctx.author.id}`.")

        # If the user attached something to the message.
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url

            # If the attachemnts url does not end in .png or .jpeg
            if not url.endswith((".jpg", ".jpeg", ".png")):
                return await ctx.send("That was not a valid attachment. It must be a PNG or JPEG image.")

            # Get the image, resize it, and save it.
            background_bytes = await imageOps.get_image(self.bot, url)
            background_resized = await self.bot.loop.run_in_executor(None, imageOps.resize_image, background_bytes, 1000, 1000)
            background_resized.save(f"files/images/backgrounds/{ctx.author.id}.png")

            # Set the users background to that image.
            await self.bot.db.execute(f"UPDATE user_config SET background = $1 WHERE key = $2", str(ctx.author.id), ctx.author.id)
            return await ctx.send(f"Your background was changed from `{data['background']}` to `{ctx.author.id}`.")


def setup(bot):
    bot.add_cog(Accounts(bot))
