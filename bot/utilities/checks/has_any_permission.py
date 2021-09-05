# Future
from __future__ import annotations

# Packages
from discord.ext import commands


def has_any_permissions(**permissions):
    return commands.check_any(*(commands.has_permissions(**{permission: value}) for permission, value in permissions.items()))
