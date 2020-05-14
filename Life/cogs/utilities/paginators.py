import asyncio
import math

import discord
from discord.ext import commands


class BasePaginator:

    def __init__(self, **kwargs):

        self.ctx = kwargs.get('ctx')

        self.original_entries = kwargs.get('entries')
        self.entries_per_page = kwargs.get('entries_per_page')

        self.pages = math.ceil(len(self.original_entries) / self.entries_per_page)
        self.entries = []

        for page_number in range(1, self.pages + 1):
            self.entries.append('\n'.join([str(entry) for entry in self.original_entries[self.entries_per_page * page_number - self.entries_per_page:self.entries_per_page * page_number]]))

        self.page = 0
        self.message = None
        self.looping = True

        self.emote_thresholds = {
            '\u23ea': 15,
            '\u2b05': 0,
            '\u23f9': 0,
            '\u27a1': 0,
            '\u23e9': 15,
        }

    async def react(self):
        try:
            if self.pages == 1:
                return await self.message.add_reaction('\u23f9')
            else:
                for emote, threshold in self.emote_thresholds.items():
                    if self.pages >= int(threshold):
                        await self.message.add_reaction(emote)
                    else:
                        continue
        except discord.Forbidden:
            raise commands.BotMissingPermissions(['Add Reactions'])

    async def stop(self):
        # Stop pagination by deleting the message.
        return await self.message.delete()


class Paginator(BasePaginator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.header = kwargs.get('header', '')
        self.footer = kwargs.get('footer', '')

        self.emotes = {
            '\u23ea': self.page_first,
            '\u2b05': self.page_backward,
            '\u23f9': self.stop,
            '\u27a1': self.page_forward,
            '\u23e9': self.page_last,
        }

    async def paginate(self):

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        self.message = await self.ctx.send(f'{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}')
        await self.react()

        while self.looping:

            try:

                # Wait for reactions, check that they are on the same message, from the same author and are in the emoji list.
                reaction, _ = await self.ctx.bot.wait_for('reaction_add', timeout=300.0, check=lambda r, u: r.message.id == self.message.id and u.id == self.ctx.author.id and str(r.emoji) in self.emotes.keys())

                if str(reaction.emoji) == '\u23f9':
                    self.looping = False
                else:
                    await self.emotes[str(reaction.emoji)]()

            except asyncio.TimeoutError:
                self.looping = False

        return await self.stop()

    async def page_first(self):

        self.page = 0

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        await self.message.edit(content=f'{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}')

    async def page_backward(self):

        # If the current page is smaller then or equal too 0, do nothing.
        if self.page <= 0:
            return
        self.page -= 1

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        await self.message.edit(content=f'{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}')

    async def page_forward(self):

        # If the current page is bigger then or equal too the amount of the pages, do nothing.
        if self.page >= self.pages - 1:
            return
        self.page += 1

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        await self.message.edit(content=f'{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}')

    async def page_last(self):

        self.page = self.pages - 1

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        await self.message.edit(content=f'{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}')


class CodeBlockPaginator(BasePaginator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.header = kwargs.get('header', '')
        self.footer = kwargs.get('footer', '')

        self.emotes = {
            '\u23ea': self.page_first,
            '\u2b05': self.page_backward,
            '\u23f9': self.stop,
            '\u27a1': self.page_forward,
            '\u23e9': self.page_last,
        }

    async def paginate(self):

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        self.message = await self.ctx.send(f'```\n{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}\n```')

        await self.react()

        while self.looping:

            try:
                # Wait for reactions, check that they are on the same message, from the same author and are in the emoji list.
                reaction, _ = await self.ctx.bot.wait_for('reaction_add', timeout=300.0, check=lambda r, u: r.message.id == self.message.id and u.id == self.ctx.author.id and str(r.emoji) in self.emotes.keys())

                if str(reaction.emoji) == '\u23f9':
                    self.looping = False
                else:
                    await self.emotes[str(reaction.emoji)]()

            except asyncio.TimeoutError:
                self.looping = False

        return await self.stop()

    async def page_first(self):

        self.page = 0

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        await self.message.edit(content=f'```\n{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}\n```')

    async def page_backward(self):

        # If the current page is smaller then or equal too 0, do nothing.
        if self.page <= 0:
            return
        self.page -= 1

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        await self.message.edit(content=f'```\n{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}\n```')

    async def page_forward(self):

        # If the current page is bigger then or equal too the amount of the pages, do nothing.
        if self.page >= self.pages - 1:
            return
        self.page += 1

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        await self.message.edit(content=f'```\n{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}\n```')

    async def page_last(self):

        self.page = self.pages - 1

        footer = None
        if len(self.footer) == 0:
            footer = f'\n\nPage: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}'

        await self.message.edit(content=f'```\n{self.header}{self.entries[self.page]}{footer if len(self.footer) == 0 else self.footer}\n```')


class EmbedPaginator(BasePaginator):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.header = kwargs.get('header', '')
        self.footer = kwargs.get('footer', '')
        self.colour = kwargs.get('colour', discord.Colour.gold())
        self.title = kwargs.get('title', '')
        self.image = kwargs.get('image', None)
        self.thumbnail = kwargs.get('thumbnail', None)

        self.embed = discord.Embed(colour=self.colour)

        if self.title:
            self.embed.title = self.title
        if self.image:
            self.embed.set_image(url=self.image)
        if self.thumbnail:
            self.embed.set_thumbnail(url=self.thumbnail)

        self.emotes = {
            '\u23ea': self.page_first,
            '\u2b05': self.page_backward,
            '\u23f9': self.stop,
            '\u27a1': self.page_forward,
            '\u23e9': self.page_last,
        }

    async def paginate(self):

        self.embed.description = f'{self.header}{self.entries[self.page]}{self.footer}'
        self.embed.set_footer(text=f'Page: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}')

        self.message = await self.ctx.send(embed=self.embed)

        await self.react()

        while self.looping:

            try:
                # Wait for reactions, check that they are on the same message, from the same author and are in the emoji list.
                reaction, _ = await self.ctx.bot.wait_for('reaction_add', timeout=300.0, check=lambda r, u: r.message.id == self.message.id and u.id == self.ctx.author.id and str(r.emoji) in self.emotes.keys())

                if str(reaction.emoji) == '\u23f9':
                    self.looping = False
                else:
                    await self.emotes[str(reaction.emoji)]()

            except asyncio.TimeoutError:
                self.looping = False

        return await self.stop()

    async def page_first(self):

        self.page = 0

        self.embed.description = f'{self.header}{self.entries[self.page]}{self.footer}'
        self.embed.set_footer(text=f'Page: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}')

        await self.message.edit(embed=self.embed)

    async def page_backward(self):

        # If the current page is smaller then or equal too 0, do nothing.
        if self.page <= 0:
            return

        self.page -= 1

        self.embed.description = f'{self.header}{self.entries[self.page]}{self.footer}'
        self.embed.set_footer(text=f'Page: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}')

        await self.message.edit(embed=self.embed)

    async def page_forward(self):

        # If the current page is bigger then or equal too the amount of the pages, do nothing.
        if self.page >= self.pages - 1:
            return

        self.page += 1

        self.embed.description = f'{self.header}{self.entries[self.page]}{self.footer}'
        self.embed.set_footer(text=f'Page: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}')

        await self.message.edit(embed=self.embed)

    async def page_last(self):

        self.page = self.pages - 1

        self.embed.description = f'{self.header}{self.entries[self.page]}{self.footer}'
        self.embed.set_footer(text=f'Page: {self.page + 1}/{self.pages} | Total entries: {len(self.original_entries)}')

        await self.message.edit(embed=self.embed)


class EmbedsPaginator:

    def __init__(self, **kwargs):

        self.ctx = kwargs.get('ctx')

        self.entries = kwargs.get('entries')
        self.page = 0

        self.message = None
        self.looping = True

        self.emote_thresholds = {
            '\u23ea': 15,
            '\u2b05': 0,
            '\u23f9': 0,
            '\u27a1': 0,
            '\u23e9': 15,
        }

        self.emotes = {
            '\u23ea': self.page_first,
            '\u2b05': self.page_backward,
            '\u23f9': self.stop,
            '\u27a1': self.page_forward,
            '\u23e9': self.page_last,
        }

    async def react(self):
        try:
            if len(self.entries) == 1:
                return await self.message.add_reaction('\u23f9')
            else:
                for emote, threshold in self.emote_thresholds.items():
                    if len(self.entries) >= int(threshold):
                        await self.message.add_reaction(emote)
                    else:
                        continue
        except discord.Forbidden:
            raise commands.BotMissingPermissions(['Add Reactions'])

    async def stop(self):
        # Stop pagination by deleting the message.
        return await self.message.delete()

    async def paginate(self):

        self.message = await self.ctx.send(embed=self.entries[self.page])
        await self.react()

        while self.looping:

            try:
                # Wait for reactions, check that they are on the same message, from the same author and are in the emoji list.
                reaction, _ = await self.ctx.bot.wait_for('reaction_add', timeout=300.0, check=lambda r, u: r.message.id == self.message.id and u.id == self.ctx.author.id and str(r.emoji) in self.emotes.keys())

                if str(reaction.emoji) == '\u23f9':
                    self.looping = False
                else:
                    await self.emotes[str(reaction.emoji)]()

            except asyncio.TimeoutError:
                self.looping = False

        return await self.stop()

    async def page_first(self):

        self.page = 0

        await self.message.edit(embed=self.entries[self.page])

    async def page_backward(self):

        # If the current page is smaller then or equal too 0, do nothing.
        if self.page <= 0:
            return
        self.page -= 1

        await self.message.edit(embed=self.entries[self.page])

    async def page_forward(self):

        # If the current page is bigger then or equal too the amount of the pages, do nothing.
        if self.page >= len(self.entries) - 1:
            return
        self.page += 1

        await self.message.edit(embed=self.entries[self.page])

    async def page_last(self):

        self.page = len(self.entries) - 1

        await self.message.edit(embed=self.entries[self.page])

