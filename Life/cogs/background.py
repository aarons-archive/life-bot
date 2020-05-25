from datetime import datetime

import asyncpg
from discord.ext import tasks, commands


class Background(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.log_bot_growth.start()
        self.log_bot_ping.start()

    @tasks.loop(hours=1.0)
    async def log_bot_growth(self):

        if self.bot.user.id == 628284183579721747:
            try:
                await self.bot.db.execute(f'INSERT INTO bot_growth VALUES ($1, $2, $3)',
                                          datetime.now().strftime('%Y-%m-%d: %H:00'),
                                          len(self.bot.users), len(self.bot.guilds))
            except asyncpg.UniqueViolationError:
                pass

    @log_bot_growth.before_loop
    async def before_log_bot_growth(self):

        await self.bot.wait_until_ready()
        print('\n[BACKGROUND] Started log bot growth task.')

    @tasks.loop(minutes=1.0)
    async def log_bot_ping(self):

        self.bot.pings.append((datetime.now().strftime('%m-%d: %H:%M'), round(self.bot.latency * 1000)))

    @log_bot_ping.before_loop
    async def before_log_bot_ping(self):

        await self.bot.wait_until_ready()
        print('[BACKGROUND] Started log bot ping task.')


def setup(bot):
    bot.add_cog(Background(bot))
