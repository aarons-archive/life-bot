import asyncio
import math

import discord


class Paginator:

    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.title = kwargs.get("title")
        self.original_entries = kwargs.get("entries")
        self.entries_per_page = kwargs.get("entries_per_page")
        self.total_entries = kwargs.get("total_entries")

        self.entries = []
        self.pages = 0

        self.page = 0
        self.message = None
        self.looping = True
        self.emotes = {
            "\u2b05": self.page_backward,
            "\u27a1": self.page_forward,
            "\u23f9": self.stop
        }

        # If the title is not set.
        if self.title is None:
            self.title = f"There are `{self.total_entries}` entries in this list and I am showing `{self.entries_per_page}` entries per page.\n\n"

    async def react(self):
        # If the amount of pages is bigger then 1, add the full range of emotes to the message.
        if self.pages > 1:
            for emote in self.emotes.keys():
                await self.message.add_reaction(emote)
        # Otherwise just add the "stop" emote.
        else:
            return await self.message.add_reaction("\u23f9")

    async def stop(self):
        # Delete the message.
        return await self.message.delete()

    async def page_forward(self):
        # If the current page is bigger then or equal to the amount of pages, return
        if self.page >= self.pages - 1:
            return
        # Edit the message to show the next page.
        await self.message.edit(content=f"{self.title}{self.entries[self.page + 1]}\n\nPage: `{self.page + 2}`/`{self.pages}`")
        self.page += 1

    async def page_backward(self):
        # If the current page is smaller then or equal to 0, return
        if self.page <= 0:
            return
        # Edit the message to show the previous page
        await self.message.edit(content=f"{self.title}{self.entries[self.page - 1]}\n\nPage: `{self.page}`/`{self.pages}`")
        self.page -= 1

    async def paginate(self):

        # Calculate the amount of pages we need and round it up.
        self.pages = math.ceil(len(self.original_entries) / self.entries_per_page)

        # Create a loop for the amount of pages needed.
        for i in range(self.pages):

            # Define a new entry for us to add amount of "entries_per_page" of entries to.
            new_entry = ""

            # Because range starts at 0, add +1 to offset it.
            i += 1

            # Loop through the entries, getting the first amount of "entries_per_page" and then the next amount of "entries_per_page" in next page cycle.
            for entry in self.original_entries[self.entries_per_page * i - self.entries_per_page:self.entries_per_page * i]:
                new_entry += f"{entry}\n"

            # Append the new entry to the new entry list
            self.entries.append(new_entry)

        # Send the message for the first page.
        self.message = await self.ctx.send(f"{self.title}{self.entries[self.page]}\n\nPage: `{self.page + 1}`/`{self.pages}`")

        # Add the reactions.
        await self.react()

        # While we are looping.
        while self.looping:
            try:

                # Wait for a reaction to be added and if the reaction is valid, then execute the function linked to that reaction.
                reaction, _ = await self.ctx.bot.wait_for("reaction_add", timeout=600.0, check=lambda r, u: u == self.ctx.author and str(r.emoji) in self.emotes.keys() and r.message.id == self.message.id)

                # If the reaction is the "stop" reaction, stop looping.
                if str(reaction.emoji) == "\u23f9":
                    self.looping = False
                # Else execute the function linked to the reaction added.
                else:
                    await self.emotes[str(reaction.emoji)]()

            # Stop looping after 600 seconds.
            except asyncio.TimeoutError:
                self.looping = False

        # Delete the message.
        return await self.stop()


class EmbedPaginator:

    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.title = kwargs.get("title")
        self.original_entries = kwargs.get("entries")
        self.entries_per_page = kwargs.get("entries_per_page")
        self.total_entries = kwargs.get("total_entries")
        self.footer = kwargs.get("footer")

        self.entries = []
        self.pages = 0

        self.page = 0
        self.message = None
        self.looping = True
        self.emotes = {
            "\u2b05": self.page_backward,
            "\u27a1": self.page_forward,
            "\u23f9": self.stop
        }

        # If the title is not set.
        if self.title is None:
            self.title = f"There are `{self.total_entries}` entries in this list and I am showing `{self.entries_per_page}` entries per page.\n\n"

        # If the footer is not set.
        if self.footer is None:
            self.footer = ""

    async def react(self):
        # If the amount of pages is bigger then 1, add the full range of emotes to the message.
        if self.pages > 1:
            for emote in self.emotes.keys():
                await self.message.add_reaction(emote)
        # Otherwise just add the "stop" emote.
        else:
            return await self.message.add_reaction("\u23f9")

    async def stop(self):
        # Delete the message.
        return await self.message.delete()

    async def page_forward(self):
        # If the current page is bigger then or equal to the amount of pages, return
        if self.page >= self.pages - 1:
            return

        # Edit the embed.
        embed = discord.Embed(
            colour=discord.Color.gold(),
            description=f"{self.title}{self.entries[self.page + 1]}{self.footer}"
        )
        embed.set_footer(text=f"Page: {self.page + 2}/{self.pages} | Total entries: {self.total_entries}")
        await self.message.edit(embed=embed)

        self.page += 1

    async def page_backward(self):
        # If the current page is smaller then or equal to 0, return
        if self.page <= 0:
            return

        # Edit the embed.
        embed = discord.Embed(
            colour=discord.Color.gold(),
            description=f"{self.title}{self.entries[self.page - 1]}{self.footer}"
        )
        embed.set_footer(text=f"Page: {self.page}/{self.pages} | Total entries: {self.total_entries}")
        await self.message.edit(embed=embed)

        self.page -= 1

    async def paginate(self):

        # Calculate the amount of pages we need and round it up.
        self.pages = math.ceil(len(self.original_entries) / self.entries_per_page)

        # Create a loop for the amount of pages needed.
        for i in range(self.pages):

            # Define a new entry for us to add amount of "entries_per_page" of entries to.
            new_entry = ""

            # Because range starts at 0, add +1 to offset it.
            i += 1

            # Loop through the entries, getting the first amount of "entries_per_page" and then the next amount of "entries_per_page" in next page cycle.
            for entry in self.original_entries[self.entries_per_page * i - self.entries_per_page:self.entries_per_page * i]:
                new_entry += f"{entry}\n"

            # Append the new entry to the new entry list
            self.entries.append(new_entry)

        # Send the message for the first page.
        embed = discord.Embed(
            colour=discord.Color.gold(),
            description=f"{self.title}{self.entries[self.page]}{self.footer}"
        )
        embed.set_footer(text=f"Page: {self.page + 1}/{self.pages} | Total entries: {self.total_entries}")
        self.message = await self.ctx.send(embed=embed)

        # Add the reactions.
        await self.react()

        # While we are looping.
        while self.looping:
            try:
                # Wait for a reaction to be added and if the reaction is valid, then execute the function linked to that reaction.
                reaction, _ = await self.ctx.bot.wait_for("reaction_add", timeout=600.0, check=lambda r, u: u == self.ctx.author and str(r.emoji) in self.emotes.keys() and r.message.id == self.message.id)

                # If the reaction is the "stop" reaction, stop looping.
                if str(reaction.emoji) == "\u23f9":
                    self.looping = False
                # Else execute the function linked to the reaction added.
                else:
                    await self.emotes[str(reaction.emoji)]()

            # Stop looping after 600 seconds.
            except asyncio.TimeoutError:
                self.looping = False

        # Delete the message.
        return await self.stop()


class CodeblockPaginator:

    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.title = kwargs.get("title")
        self.original_entries = kwargs.get("entries")
        self.entries_per_page = kwargs.get("entries_per_page")
        self.total_entries = kwargs.get("total_entries")

        self.entries = []
        self.pages = 0

        self.page = 0
        self.message = None
        self.looping = True
        self.emotes = {
            "\u2b05": self.page_backward,
            "\u27a1": self.page_forward,
            "\u23f9": self.stop
        }

        # If the title is not set.
        if self.title is None:
            self.title = f"There are {self.total_entries} entries in this list and I am showing {self.entries_per_page} entries per page.\n\n"

    async def react(self):
        # If the amount of pages is bigger then 1, add the full range of emotes to the message.
        if self.pages > 1:
            for emote in self.emotes.keys():
                await self.message.add_reaction(emote)
        # Otherwise just add the "stop" emote.
        else:
            return await self.message.add_reaction("\u23f9")

    async def stop(self):
        # Delete the message.
        return await self.message.delete()

    async def page_forward(self):
        # If the current page is bigger then or equal to the amount of pages, return
        if self.page >= self.pages - 1:
            return
        # Edit the message to show the next page.
        await self.message.edit(content=f"```\n\n{self.title}{self.entries[self.page + 1]}\n\nPage: {self.page + 2}/{self.pages}\n```")
        self.page += 1

    async def page_backward(self):
        # If the current page is smaller then or equal to 0, return
        if self.page <= 0:
            return
        # Edit the message to show the previous page
        await self.message.edit(content=f"```\n\n{self.title}{self.entries[self.page - 1]}\n\nPage: {self.page}/{self.pages}\n```")
        self.page -= 1

    async def paginate(self):

        # Calculate the amount of pages we need and round it up.
        self.pages = math.ceil(len(self.original_entries) / self.entries_per_page)

        # Create a loop for the amount of pages needed.
        for i in range(self.pages):

            # Define a new entry for us to add amount of "entries_per_page" of entries to.
            new_entry = ""

            # Because range starts at 0, add +1 to offset it.
            i += 1

            # Loop through the entries, getting the first amount of "entries_per_page" and then the next amount of "entries_per_page" in next page cycle.
            for entry in self.original_entries[self.entries_per_page * i - self.entries_per_page:self.entries_per_page * i]:
                new_entry += f"{entry}\n"

            # Append the new entry to the new entry list
            self.entries.append(new_entry)

        # Send the message for the first page.
        self.message = await self.ctx.send(f"```\n\n{self.title}{self.entries[self.page]}\n\nPage: {self.page + 1}/{self.pages}\n```")

        # Add the reactions.
        await self.react()

        # While we are looping.
        while self.looping:
            try:

                # Wait for a reaction to be added and if the reaction is valid, then execute the function linked to that reaction.
                reaction, _ = await self.ctx.bot.wait_for("reaction_add", timeout=600.0, check=lambda r, u: u == self.ctx.author and str(r.emoji) in self.emotes.keys() and r.message.id == self.message.id)

                # If the reaction is the "stop" reaction, stop looping.
                if str(reaction.emoji) == "\u23f9":
                    self.looping = False
                # Else execute the function linked to the reaction added.
                else:
                    await self.emotes[str(reaction.emoji)]()

            # Stop looping after 600 seconds.
            except asyncio.TimeoutError:
                self.looping = False

        # Delete the message.
        return await self.stop()


class EmbedsPaginator:

    def __init__(self, **kwargs):
        self.ctx = kwargs.get("ctx")
        self.entries = kwargs.get("entries")
        self.pages = len(self.entries)
        self.page = 0
        self.message = None
        self.looping = True
        self.emotes = {
            "\u2b05": self.page_backward,
            "\u27a1": self.page_forward,
            "\u23f9": self.stop
        }

    async def react(self):
        # If the amount of pages is bigger then 1, add the full range of emotes to the message.
        if self.pages > 1:
            for emote in self.emotes.keys():
                await self.message.add_reaction(emote)
        # Otherwise just add the "stop" emote.
        else:
            return await self.message.add_reaction("\u23f9")

    async def stop(self):
        # Delete the message.
        return await self.message.delete()

    async def page_forward(self):
        # If the current page is bigger then or equal to the amount of pages, return
        if self.page >= self.pages - 1:
            return

        # Edit the embed.
        await self.message.edit(embed=self.entries[self.page + 1])

        # Change the page that we are currently on
        self.page += 1

    async def page_backward(self):
        # If the current page is smaller then or equal to 0, return
        if self.page <= 0:
            return

        # Edit the embed.

        await self.message.edit(embed=self.entries[self.page - 1])

        # Change the page we are currently on.
        self.page -= 1

    async def paginate(self):

        # Send the message for the first page.
        self.message = await self.ctx.send(embed=self.entries[self.page])

        # Add the reactions.
        await self.react()

        # While we are looping.
        while self.looping:
            try:
                # Wait for a reaction to be added and if the reaction is valid, then execute the function linked to that reaction.
                reaction, _ = await self.ctx.bot.wait_for("reaction_add", timeout=600.0, check=lambda r, u: u == self.ctx.author and str(r.emoji) in self.emotes.keys() and r.message.id == self.message.id)

                # If the reaction is the "stop" reaction, stop looping.
                if str(reaction.emoji) == "\u23f9":
                    self.looping = False
                # Else execute the function linked to the reaction added.
                else:
                    await self.emotes[str(reaction.emoji)]()

            # Stop looping after 600 seconds.
            except asyncio.TimeoutError:
                self.looping = False

        # Delete the message.
        return await self.stop()


