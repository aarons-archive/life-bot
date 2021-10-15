# Future
from __future__ import annotations

# Packages
import yarl
from discord.ext import commands

# My stuff
from utilities import custom, objects, utils


class ImageConverter(commands.Converter[objects.Image]):

    async def convert(self, ctx: custom.Context, argument: str) -> objects.Image:

        if (check := yarl.URL(argument)) and check.scheme and check.host:
            return objects.Image(argument)

        try:
            member = await commands.MemberConverter().convert(ctx=ctx, argument=argument)
        except commands.MemberNotFound:
            pass
        else:
            return objects.Image(utils.avatar(member))

        try:
            emoji = await commands.EmojiConverter().convert(ctx=ctx, argument=str(argument))
        except commands.EmojiNotFound:
            pass
        else:
            return objects.Image(emoji.url)

        try:
            partial_emoji = await commands.PartialEmojiConverter().convert(ctx=ctx, argument=str(argument))
        except commands.PartialEmojiConversionFailure:
            pass
        else:
            return objects.Image(partial_emoji.url)

        url = f"https://twemoji.maxcdn.com/v/latest/72x72/{ord(argument[0]):x}.png"

        async with ctx.bot.session.get(url=url) as response:
            if response.status == 200:
                return objects.Image(url)

        raise commands.BadArgument(message=argument)
