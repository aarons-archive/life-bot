# Future
from __future__ import annotations

# Packages
import discord

# My stuff
from core import values


class SupportButton(discord.ui.View):

    def __init__(self) -> None:
        super().__init__()

        self.add_item(discord.ui.Button(label='Support server', url=values.SUPPORT_LINK))
