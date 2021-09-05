# Future
from __future__ import annotations

# Packages
import yarl
from discord.ext import commands

# My stuff
from utilities import context, utils


class ImageConverter(commands.Converter):

    async def convert(self, ctx: context.Context, argument: str) -> str:

        try:
            member = await commands.MemberConverter().convert(ctx=ctx, argument=str(argument))
        except commands.MemberNotFound:
            pass
        else:
            await ctx.reply(f"Editing **{member}**'s avatar. If this is a mistake please specify the user/image you would like to edit before any extra arguments.")
            return utils.avatar(member)

        if (check := yarl.URL(argument)) and check.scheme and check.host:
            return argument

        try:
            emoji = await commands.EmojiConverter().convert(ctx=ctx, argument=str(argument))
        except commands.EmojiNotFound:
            pass
        else:
            return str(emoji.url)

        try:
            partial_emoji = await commands.PartialEmojiConverter().convert(ctx=ctx, argument=str(argument))
        except commands.PartialEmojiConversionFailure:
            pass
        else:
            return str(partial_emoji.url)

        url = f"https://twemoji.maxcdn.com/v/latest/72x72/{ord(argument[0]):x}.png"
        async with ctx.bot.session.get(url=f"https://twemoji.maxcdn.com/v/latest/72x72/{ord(argument[0]):x}.png") as response:
            if response.status == 200:
                return url

        raise commands.ConversionError(self, original=argument)
