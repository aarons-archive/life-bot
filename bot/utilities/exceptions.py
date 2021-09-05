# Future
from __future__ import annotations

# Standard Library
from typing import Optional

# Packages
import discord
from discord.ext import commands

# My stuff
from core import colours
from utilities import utils


class LifeError(commands.CommandError):
    pass


class EmbedError(LifeError):

    def __init__(
        self,
        footer_url: Optional[str] = None,
        footer: Optional[str] = None,
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
            footer_url=footer_url,
            footer=footer,
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
