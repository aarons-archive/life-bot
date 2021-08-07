import os
import pathlib

from discord.ext import commands, tasks

from core.bot import Life


IGNORE_EXTENSIONS = ["jishaku"]


def path_from_extension(extension: str) -> pathlib.Path:
    return pathlib.Path(extension.replace(".", os.sep)+".py")


def setup(bot: Life):
    bot.add_cog(HotReload(bot=bot))


class HotReload(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.last_modified_time = {}

        self.hot_reload_loop.start()

    def cog_unload(self):
        self.hot_reload_loop.stop()

    @tasks.loop(seconds=3)
    async def hot_reload_loop(self) -> None:

        for extension in list(self.bot.extensions.keys()):
            if extension in IGNORE_EXTENSIONS:
                continue
            path = path_from_extension(extension)
            time = os.path.getmtime(path)

            try:
                if self.last_modified_time[extension] == time:
                    continue
            except KeyError:
                self.last_modified_time[extension] = time

            try:
                self.bot.reload_extension(extension)
            except commands.ExtensionError:
                print(f"Couldn't reload extension: {extension}")
            else:
                print(f"Reloaded extension: {extension}")
            finally:
                self.last_modified_time[extension] = time

    @hot_reload_loop.before_loop
    async def cache_last_modified_time(self) -> None:

        for extension in self.bot.extensions.keys():

            if extension in IGNORE_EXTENSIONS:
                continue

            path = path_from_extension(extension)
            time = os.path.getmtime(path)
            self.last_modified_time[extension] = time
