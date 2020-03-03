import json
from datetime import datetime

import asyncpg
import discord
from discord.ext import tasks, commands


class Background(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.current_presence = 0
        self.bot.presences = []

        self.change_presence.start()
        self.log_bot_stats.start()
        self.log_ping.start()

    def cog_unload(self):
        self.change_presence.stop()
        self.log_bot_stats.stop()
        self.log_ping.stop()

    @tasks.loop(hours=1.0)
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
    async def log_bot_stats(self):

        if self.bot.user.id == 627491967391236097:
            return

        try:
            await self.bot.db.execute(f"INSERT INTO bot_growth VALUES ($1, $2, $3)", datetime.utcnow().strftime('%Y-%m-%d: %H:00'), len(self.bot.users), len(self.bot.guilds))
        except asyncpg.UniqueViolationError:
            pass

        for guild_id, guild_usage in self.bot.usage.items():
            try:
                await self.bot.db.execute("INSERT INTO bot_usage VALUES ($1, $2)", guild_id, json.dumps(guild_usage))

            except asyncpg.UniqueViolationError:
                data = await self.bot.db.fetchrow("SELECT * FROM bot_usage WHERE id = $1", guild_id)
                db_usage = json.loads(data["usage"])

                for guild_command_name, guild_command_usage in guild_usage.items():
                    db_usage[guild_command_name] = guild_command_usage

                await self.bot.db.execute("UPDATE bot_usage SET usage = $1 where id = $2", json.dumps(db_usage), guild_id)

    @log_bot_stats.before_loop
    async def before_store_bot_growth(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=1.0)
    async def log_ping(self):
        self.bot.pings.append((datetime.utcnow().strftime('%H:%M'), round(self.bot.latency * 1000)))

    @log_ping.before_loop
    async def before_log_ping(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Background(bot))
