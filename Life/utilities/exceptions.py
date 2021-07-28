from typing import Optional

import discord
from discord.ext import commands

from core import colours
from utilities import utils


class LifeError(commands.CommandError):
    pass


class EmbedError(LifeError):

    def __init__(
            self,
            embed_footer_url: Optional[str] = None,
            embed_footer: Optional[str] = None,
            image: Optional[str] = None,
            thumbnail: Optional[str] = None,
            author: Optional[str] = None,
            author_url: Optional[str] = None,
            author_icon_url: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            url: Optional[str] = None,
            colour: discord.Colour = colours.MAIN,
            emoji: Optional[str] = None
    ) -> None:
        self.embed = utils.embed(
                embed_footer_url=embed_footer_url,
                embed_footer=embed_footer,
                image=image,
                thumbnail=thumbnail,
                author=author,
                author_url=author_url,
                author_icon_url=author_icon_url,
                title=title,
                description=description,
                url=url,
                colour=colour,
                emoji=emoji
        )
