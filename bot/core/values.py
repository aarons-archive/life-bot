# Future
from __future__ import annotations

# Packages
import discord
from pendulum.tz.timezone import Timezone

# My stuff
from core import config
from utilities import converters, enums, objects


# Common values
ZWSP = "\u200b"
NL = "\n"
PERMISSIONS = discord.Permissions(
    read_messages=True,
    send_messages=True,
    embed_links=True,
    attach_files=True,
    read_message_history=True,
    add_reactions=True,
    external_emojis=True,
)


# Discord links
INVITE_LINK = discord.utils.oauth_url(
    client_id=config.BOT_ID,
    permissions=PERMISSIONS,
    scopes=["bot", "applications.commands"]
)
INVITE_LINK_NO_PERMISSIONS = discord.utils.oauth_url(
    client_id=config.BOT_ID,
    scopes=["bot"]
)

BETA_INVITE_LINK = discord.utils.oauth_url(
    client_id=config.BETA_BOT_ID,
    permissions=PERMISSIONS,
    scopes=["bot", "applications.commands"]
)
BETA_INVITE_LINK_NO_PERMISSIONS = discord.utils.oauth_url(
    client_id=config.BETA_BOT_ID,
    scopes=["bot"]
)


# External links
SUPPORT_LINK = "https://discord.gg/w9f6NkQbde"
GITHUB_LINK = "https://github.com/Axelancerr/Life-bot"

FLAG_COMMANDS = [
    "play",
    "search",
    "youtube-music",
    "soundcloud",
    "play-next",
    "play-now",
    "rolecounts",
]

CONVERTERS = {
    objects.PastPhrasedDatetimeSearch:   converters.PastPhrasedDatetimeConverter,
    objects.FuturePhrasedDatetimeSearch: converters.FuturePhrasedDatetimeConverter,
    enums.ReminderRepeatType:            converters.EnumConverter(enums.ReminderRepeatType, "Repeat type"),
    enums.NotificationType:              converters.EnumConverter(enums.NotificationType, "Notification type"),

    objects.Reminder:                    converters.ReminderConverter,
    Timezone:                            converters.TimezoneConverter,
}

DATE_PARSER_SETTINGS = {
    "DATE_ORDER":               "DMY",
    "TIMEZONE":                 "UTC",
    "RETURN_AS_TIMEZONE_AWARE": False,
    "PREFER_DAY_OF_MONTH":      "current",
    "PREFER_DATES_FROM":        "past",
    "PARSERS":                  ["relative-time", "absolute-time", "timestamp"],
}
