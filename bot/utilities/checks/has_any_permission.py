# Future
from __future__ import annotations

# Standard Library
from typing import Callable, TypeVar

# Packages
from discord.ext import commands


T = TypeVar("T")


def has_any_permissions(**permissions) -> Callable[[T], T]:
    return commands.check_any(*(commands.has_permissions(**{permission: value}) for permission, value in permissions.items()))  # type: ignore
