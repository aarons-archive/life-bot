# Future
from __future__ import annotations

# Standard Library
from typing import Generic, Type, TypeVar

# Packages
import discord
from discord.ext import commands

# My stuff
from core import colours, values
from utilities import custom, exceptions


EnumType = TypeVar("EnumType", bound=discord.Enum)


class EnumConverter(commands.Converter, Generic[EnumType]):

    def __init__(self, enum: Type[EnumType], name: str) -> None:
        self.enum = enum
        self.name = name

    async def convert(self, ctx: custom.Context, argument: str) -> EnumType:

        if enum := getattr(self.enum, argument.replace(" ", "_").upper(), None):
            return enum

        options = [f"- `{option}`" for option in [repeat_type.name.replace("_", " ").lower() for repeat_type in self.enum]]

        raise exceptions.EmbedError(
            colour=colours.RED,
            description=f"{self.name} must be one of:\n{values.NL.join(options)}",
        )
