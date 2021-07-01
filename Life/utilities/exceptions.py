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


class LifeError(commands.CommandError):
    pass


class EmbedError(LifeError):

    def __init__(
            self, colour: discord.Colour, title: Optional[str] = None, url: Optional[str] = None, description: Optional[str] = None, image: Optional[str] = None, thumbnail: Optional[str] = None
    ) -> None:

        self._colour: discord.Colour = colour
        self._title: Optional[str] = title
        self._url: Optional[str] = url
        self._description: Optional[str] = description
        self._image: Optional[str] = image
        self._thumbnail: Optional[str] = thumbnail

        self._embed: discord.Embed = discord.Embed(
                colour=self._colour, title=self._title or discord.embeds.EmptyEmbed, url=self._url or discord.embeds.EmptyEmbed, description=self._description or discord.embeds.EmptyEmbed
        )

        if self._image:
            self.embed.set_image(url=self._image)
        if self._thumbnail:
            self.embed.set_thumbnail(url=self._thumbnail)

    @property
    def embed(self) -> discord.Embed:
        return self._embed
