from datetime import datetime

import discord
from discord.ext import tasks, commands


class Background(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.current_presence = 0
        self.bot.presences = []

        self.change_presence.start()
        self.log_bot_growth.start()
        self.log_ping.start()

    def cog_unload(self):

        self.change_presence.stop()
        self.log_bot_growth.stop()
        self.log_ping.stop()

    @tasks.loop(minutes=30.0)
    async def change_presence(self):

        presences = [discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.guilds)} Guilds'),
                     discord.Activity(type=discord.ActivityType.watching, name=f'{len(self.bot.users)} Users'),
                     discord.Activity(type=discord.ActivityType.playing,  name=f"{self.bot.config.DISCORD_PREFIX}help")]

        await self.bot.change_presence(activity=presences[self.current_presence])
        self.current_presence = (self.current_presence + 1) % len(presences)

    @change_presence.before_loop
    async def before_change_presence(self):

        await self.bot.wait_until_ready()

    @tasks.loop(hours=1.0)
    async def log_bot_growth(self):

        if self.bot.user.id == 628284183579721747:
            await self.bot.db.execute(f"INSERT INTO bot_growth VALUES ($1, $2, $3)", datetime.now().strftime('%Y-%m-%d: %H:00'), len(self.bot.users), len(self.bot.guilds))

    @log_bot_growth.before_loop
    async def before_log_bot_growth(self):

        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1.0)
    async def log_ping(self):

        self.bot.pings.append((datetime.now().strftime('%m-%d: %H:%M'), round(self.bot.latency * 1000)))

    @log_ping.before_loop
    async def before_log_ping(self):

        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Background(bot))
