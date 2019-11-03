import codecs
import os
import pathlib
import random
import time

import discord


def random_colour():
    return "%02X%02X%02X" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def linecount():
    file_amount = 0
    functions = 0
    comments = 0
    lines = 0
    for path, subdirs, files in os.walk("."):
        for name in files:
            if name.endswith(".py"):
                file_amount += 1
                with codecs.open("./" + str(pathlib.PurePath(path, name)), "r", "utf-8") as f:
                    for i, l in enumerate(f):
                        if len(l.strip()) == 0:
                            continue
                        elif l.strip().startswith("#"):
                            comments += 1
                        elif l.strip().startswith("async def") or l.strip().startswith("async"):
                            functions += 1
                            lines += 1
                        else:
                            lines += 1
    return file_amount, functions, comments, lines

async def ping(bot, ctx):
    # Define variables.
    pings = []
    total_ping = 0

    # Get typing time and append.
    typing_start = time.monotonic()
    await ctx.trigger_typing()
    typing_end = time.monotonic()
    typingms = round((typing_end - typing_start) * 1000, 2)
    pings.append(typingms)

    # Get latency and append.
    latencyms = round(bot.latency * 1000, 2)
    pings.append(latencyms)

    # Ping discord and append.
    discord_start = time.monotonic()
    async with bot.session.get("https://discordapp.com/") as resp:
        if resp.status == 200:
            discord_end = time.monotonic()
            discordms = round((discord_end - discord_start) * 1000, 2)
            pings.append(discordms)
        else:
            discordms = "Failed"

    # Calculate the average.
    for ping_ms in pings:
        total_ping += ping_ms
    averagems = round(total_ping / len(pings), 2)

    # Return values.
    return typingms, latencyms, discordms, averagems

def user_activity(user):
    # If the user is offline they wont have an activity.
    if user.status == discord.Status.offline:
        return "N/A"
    # If the user is doing nothing.
    if not user.activity:
        return "N/A"
    activity = ""
    if user.activity.type == discord.ActivityType.playing:
        activity += f"Playing **{user.activity.name}**"
        if not isinstance(user.activity, discord.Game) and user.activity.details:
            activity += f" ** - {user.activity.details}**"
    if user.activity.type == discord.ActivityType.streaming:
        activity += f"Streaming **[{user.activity.name}]({user.activity.url})**"
    if user.activity.type == discord.ActivityType.watching:
        activity += f"Watching **{user.activity.name}**"
    if user.activity.type == discord.ActivityType.listening:
        if user.activity.name == "Spotify":
            activity += f"Listening to **{user.activity.title}** by **{user.activity.artist}**"
            if user.activity.album:
                activity += f" from the album **{user.activity.album}**"
        else:
            activity += f"Listening to **{user.activity.name}**"
    return activity

def user_colour(user):
    colours = {
        discord.Status.online: 0x008000,
        discord.Status.idle: 0xFF8000,
        discord.Status.dnd: 0xFF0000,
        discord.Status.offline: 0x808080
    }
    return colours[user.status]

def user_status(user):
    status = {
        discord.Status.online: "Online",
        discord.Status.idle: "Idle",
        discord.Status.dnd: "Do not disturb",
        discord.Status.offline: "Offline"
    }
    return status[user.status]

def guild_user_status(guild):
    online = sum(1 for member in guild.members if member.status == discord.Status.online)
    idle = sum(1 for member in guild.members if member.status == discord.Status.idle)
    dnd = sum(1 for member in guild.members if member.status == discord.Status.do_not_disturb)
    offline = sum(1 for member in guild.members if member.status == discord.Status.offline)
    return online, idle, dnd, offline

def guild_region(guild):
    regions = {
        discord.VoiceRegion.amsterdam: "Amsterdam",
        discord.VoiceRegion.brazil: "Brazil",
        discord.VoiceRegion.eu_central: "EU-Central",
        discord.VoiceRegion.eu_west: "EU-West",
        discord.VoiceRegion.europe: "Europe",
        discord.VoiceRegion.frankfurt: "Frankfurt",
        discord.VoiceRegion.hongkong: "Hong kong",
        discord.VoiceRegion.india: "India",
        discord.VoiceRegion.japan: "Japan",
        discord.VoiceRegion.london: "Londom",
        discord.VoiceRegion.russia: "Russia",
        discord.VoiceRegion.singapore: "Singapore",
        discord.VoiceRegion.southafrica: "South Africa",
        discord.VoiceRegion.sydney: "Sydney",
        discord.VoiceRegion.us_central: "US-Central",
        discord.VoiceRegion.us_east: "US-East",
        discord.VoiceRegion.us_south: "US-South",
        discord.VoiceRegion.us_west: "US-West"
    }
    return regions[guild.region]

def guild_mfa_level(guild):
    mfa_levels = {
        0: "Not required",
        1: "Required"
    }
    return mfa_levels[guild.mfa_level]

def guild_verification_level(guild):
    verification_levels = {
        discord.VerificationLevel.none: "None - No criteria set.",
        discord.VerificationLevel.low: "Low - Must have a verified email.",
        discord.VerificationLevel.medium: "Medium - Must have a verified email and be registered on discord for more than 5 minutes.",
        discord.VerificationLevel.high: "High - Must have a verified email, be registered on discord for more than 5 minutes and be a member of the guild for more then 10 minutes.",
        discord.VerificationLevel.extreme: "Extreme - Must have a verified email, be registered on discord for more than 5 minutes, be a member of the guild for more then 10 minutes and a have a verified phone number."
    }
    return verification_levels[guild.verification_level]

def guild_content_filter_level(guild):
    explicit_content_filters = {
        discord.ContentFilter.disabled: "None - Content filter disabled.",
        discord.ContentFilter.no_role: "No role - Content filter enabled only for users with no roles.",
        discord.ContentFilter.all_members: "All members - Content filter enabled for all users.",
    }
    return explicit_content_filters[guild.explicit_content_filter]

