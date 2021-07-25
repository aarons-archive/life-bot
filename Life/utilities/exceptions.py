"""
Copyright (c) 2020-present Axelancerr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
