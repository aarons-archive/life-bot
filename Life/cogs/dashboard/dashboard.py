"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import os

from discord.ext import commands
from tornado import httpserver, web

from bot import Life
from cogs.dashboard.endpoints import dashboard, main, metrics, websocket
from cogs.dashboard.utilities import http


class Dashboard(commands.Cog):

    def __init__(self, bot: Life):
        self.bot = bot

        self.endpoints = [main, dashboard, metrics, websocket]

        self.application = web.Application(
            [endpoint for endpoints in [endpoint.setup(bot=self.bot) for endpoint in self.endpoints] for endpoint in endpoints],
            static_path=os.path.join(os.path.dirname(__file__), 'static/'), template_path=os.path.join(os.path.dirname(__file__), 'templates/'),
            cookie_secret=self.bot.config.cookie_secret, default_host='0.0.0.0', debug=True
        )

        self.bot.http_server = httpserver.HTTPServer(self.application, xheaders=True)
        self.bot.http_client = http.HTTPClient(bot=self.bot)

        asyncio.create_task(self.initialize())

    async def initialize(self):

        self.bot.http_server.bind(self.bot.config.port, '0.0.0.0')
        self.bot.http_server.start()

        print(f'\n[DASHBOARD] Dashboard has connected.')


def setup(bot):
    bot.add_cog(Dashboard(bot))
