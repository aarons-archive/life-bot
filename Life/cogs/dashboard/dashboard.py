import asyncio
import os

from discord.ext import commands
from tornado import httpserver, web

from cogs.dashboard.endpoints import dashboard, guilds, index, login, success
from cogs.dashboard.utilities import http, utils


class DashboardManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.endpoints = [index, login, success, dashboard, guilds]

        self.application = web.Application([endpoint.setup(bot=self.bot) for endpoint in self.endpoints],
                                           static_path=os.path.join(os.path.dirname(__file__), 'static/'),
                                           template_path=os.path.join(os.path.dirname(__file__), 'templates/'),
                                           cookie_secret=self.bot.config.cookie_secret, default_host='0.0.0.0',
                                           debug=True, ui_methods=utils)

        self.bot.http_server = httpserver.HTTPServer(self.application)
        self.bot.http_client = http.HTTPClient(bot=self.bot)

        asyncio.create_task(self.initialize())

    async def initialize(self):

        self.bot.http_server.bind(self.bot.config.port, '0.0.0.0')
        self.bot.http_server.start()

        print(f'\n[DASHBOARD] Dashboard has connected.')


def setup(bot):
    bot.add_cog(DashboardManager(bot))
