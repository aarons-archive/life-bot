import asyncio
import os

from discord.ext import commands
from tornado import httpserver, web

from cogs.dashboard.utilities import http, utils


class DashboardManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.endpoints = [endpoint.setup(bot=self.bot) for endpoint in self.bot.config.endpoints]
        self.application = web.Application([endpoint for endpoints in self.endpoints for endpoint in endpoints],
                                           static_path=os.path.join(os.path.dirname(__file__), 'static/'),
                                           template_path=os.path.join(os.path.dirname(__file__), 'templates/'),
                                           default_host='0.0.0.0', ui_methods=utils, debug=True,
                                           cookie_secret=self.bot.config.cookie_secret)

        self.bot.http_server = httpserver.HTTPServer(self.application, xheaders=True)
        self.bot.http_client = http.HTTPClient(bot=self.bot)

        asyncio.create_task(self.initialize())

    async def initialize(self):

        self.bot.http_server.bind(self.bot.config.port, '0.0.0.0')
        self.bot.http_server.start()

        print(f'\n[DASHBOARD] Dashboard has connected.')


def setup(bot):
    bot.add_cog(DashboardManager(bot))
