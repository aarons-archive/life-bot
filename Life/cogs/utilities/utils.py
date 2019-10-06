import discord
import pathlib
import codecs
import random
import time
import ssl
import os


def random_colour():
    return "%02X%02X%02X" % (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


# noinspection PyArgumentEqualDefault
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
                        if l.strip().startswith("#"):
                            comments += 1
                        if l.strip().startswith("async def") or l.strip().startswith("async"):
                            functions += 1
                        if len(l.strip()) == 0:
                            continue
                        else:
                            lines += 1
    return file_amount, functions, comments, lines


async def ping(bot, ctx):
    # Define variables.
    pings = []
    number = 0

    # Get typing time and append.
    typings = time.monotonic()
    await ctx.trigger_typing()
    typinge = time.monotonic()
    typingms = round((typinge - typings) * 1000, 2)
    pings.append(typingms)

    # Get latency and append.
    latencyms = round(bot.latency * 1000, 2)
    pings.append(latencyms)

    # Ping discord and append.
    discords = time.monotonic()
    try:
        async with bot.session.get("https://discordapp.com/") as resp:
            if resp.status == 200:
                discorde = time.monotonic()
                discordms = round((discorde - discords) * 1000, 2)
                pings.append(discordms)
            else:
                discordms = "Failed"
    except ssl.SSLError:
        pass

    # Calculate the average.
    for ms in pings:
        number += ms
    averagems = round(number / len(pings), 2)

    # Return values.
    return typingms, latencyms, discordms, averagems


def embed_color(user):
    if user.status == discord.Status.online:
        return 0x008000
    elif user.status == discord.Status.idle:
        return 0xFF8000
    elif user.status == discord.Status.dnd:
        return 0xFF0000
    elif user.status == discord.Status.offline:
        return 0x808080
    else:
        return 0xFF8000


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


def user_status(user):
    if user.status == discord.Status.online:
        return "Online"
    elif user.status == discord.Status.idle:
        return "Idle"
    elif user.status == discord.Status.dnd:
        return "Do not Disturb"
    elif user.status == discord.Status.offline:
        return "Offline"
    else:
        return "Offline"


def guild_user_status_count(guild):
    online = 0
    offline = 0
    idle = 0
    dnd = 0
    for member in guild.members:
        if member.status == discord.Status.online:
            online += 1
        if member.status == discord.Status.idle:
            idle += 1
        if member.status == discord.Status.dnd:
            dnd += 1
        if member.status == discord.Status.offline:
            offline += 1
    return online, offline, idle, dnd


def guild_region(guild):
    if guild.region == discord.VoiceRegion.amsterdam:
        return "Amsterdam"
    elif guild.region == discord.VoiceRegion.brazil:
        return "Brazil"
    elif guild.region == discord.VoiceRegion.eu_central:
        return "Central-Europe"
    elif guild.region == discord.VoiceRegion.eu_west:
        return "Western-Europe"
    elif guild.region == discord.VoiceRegion.frankfurt:
        return "Frankfurt"
    elif guild.region == discord.VoiceRegion.hongkong:
        return "Hong-Kong"
    elif guild.region == discord.VoiceRegion.india:
        return "India"
    elif guild.region == discord.VoiceRegion.japan:
        return "Japan"
    elif guild.region == discord.VoiceRegion.london:
        return "London"
    elif guild.region == discord.VoiceRegion.russia:
        return "Russia"
    elif guild.region == discord.VoiceRegion.singapore:
        return "Singapore"
    elif guild.region == discord.VoiceRegion.southafrica:
        return "South-Africa"
    elif guild.region == discord.VoiceRegion.sydney:
        return "Sydney"
    elif guild.region == discord.VoiceRegion.us_central:
        return "US-Central"
    elif guild.region == discord.VoiceRegion.us_east:
        return "US-East"
    elif guild.region == discord.VoiceRegion.us_south:
        return "US-South"
    elif guild.region == discord.VoiceRegion.us_west:
        return "US-West"
    else:
        return "N/A"


def guild_mfa_level(guild):
    if guild.mfa_level == 0:
        return "Not required"
    elif guild.mfa_level == 1:
        return "Required"
    else:
        return "N/A"


def guild_verification_level(guild):
    if guild.verification_level == discord.VerificationLevel.none:
        return "None - No criteria set."
    elif guild.verification_level == discord.VerificationLevel.low:
        return "Low - Must have a verified email."
    elif guild.verification_level == discord.VerificationLevel.medium:
        return "Medium - Must have a verified email and be registered on discord for more than 5 minutes."
    elif guild.verification_level == discord.VerificationLevel.high:
        return "High - Must have a verified email, be registered on discord for more than 5 minutes and be a member of the guild for more then 10 minutes."
    elif guild.verification_level == discord.VerificationLevel.extreme:
        return "Extreme - Must have a verified email, be registered on discord for more than 5 minutes, be a member of the guild for more then 10 minutes and a have a verified phone number."
    else:
        return "N/A"


def guild_content_filter_level(guild):
    if guild.explicit_content_filter == discord.ContentFilter.disabled:
        return "None - Content filter disabled."
    elif guild.explicit_content_filter == discord.ContentFilter.no_role:
        return "No role - Content filter enabled only for users with no roles."
    elif guild.explicit_content_filter == discord.ContentFilter.all_members:
        return "All members - Content filter enabled for all users."
    else:
        return "N/A"



