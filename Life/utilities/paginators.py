"""
Life
Copyright (C) 2020 Axel#3456

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio

import discord


class BasePaginator:

    def __init__(self, **kwargs) -> None:

        self.kwargs = kwargs

        self.ctx = kwargs.get('ctx')
        self.entries = [str(entry) for entry in kwargs.get('entries')]
        self.per_page = kwargs.get('per_page')

        self.delete_when_done = kwargs.get('delete_when_done', True)
        self.bot = kwargs.get('bot', self.ctx.bot)
        self.timeout = kwargs.get('timeout', 300)

        self.codeblock = kwargs.get('codeblock')
        self.codeblock_start = '```\n' if self.codeblock else ''
        self.codeblock_end = '\n```' if self.codeblock else ''

        self.pages = ['\n'.join(self.entries[page:page + self.per_page]) for page in range(0, len(self.entries), self.per_page)]

        self.task_loop = None
        self.message = None
        self.looping = True
        self.page = 0

        self.buttons = {
            ':first:737826967910481931': self.first,
            ':backward:737826960885153800': self.backward,
            ':stop:737826951980646491': self.stop,
            ':forward:737826943193448513': self.forward,
            ':last:737826943520473198': self.last
        }

    def check_reaction(self, payload: discord.RawReactionActionEvent) -> bool:

        if self.message is None:
            return False

        if payload.message_id != self.message.id:
            return False

        if payload.user_id not in (self.bot.owner_id, self.ctx.author.id):
            return False

        return str(payload.emoji).strip('<>') in self.buttons.keys()

    async def react(self) -> None:

        if len(self.pages) == 1:
            await self.message.add_reaction(':stop:737826951980646491')
        else:
            for emote in self.buttons.keys():
                if emote in (':start:737826967910481931', ':end:737826943520473198') and len(self.pages) < 5:
                    continue
                await self.message.add_reaction(emote)

    async def loop(self) -> None:

        await self.react()

        while self.looping is True:

            try:
                tasks = [
                    asyncio.ensure_future(self.bot.wait_for('raw_reaction_add', check=self.check_reaction)),
                    asyncio.ensure_future(self.bot.wait_for('raw_reaction_remove', check=self.check_reaction))
                ]
                done, pending = await asyncio.wait(tasks, timeout=self.timeout, return_when=asyncio.FIRST_COMPLETED)

                for task in pending:
                    task.cancel()

                if len(done) == 0:
                    raise asyncio.TimeoutError()

                await self.buttons[str(done.pop().result().emoji).strip('<>')]()

            except asyncio.TimeoutError:
                self.looping = False

        if not self.message:
            return

        if self.delete_when_done is False:
            for reaction in self.buttons.keys():
                await self.message.remove_reaction(reaction, self.bot.user)

        return await self.stop(delete=self.delete_when_done)

    async def first(self) -> None:
        pass

    async def backward(self) -> None:
        pass

    async def stop(self, delete: bool = True) -> None:
        pass

    async def forward(self) -> None:
        pass

    async def last(self) -> None:
        pass


class Paginator(BasePaginator):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.header = kwargs.get('header', '')

    @property
    def footer(self) -> str:
        return self.kwargs.get('footer', f'\n\nPage: {self.page + 1}/{len(self.pages)} | Total entries: {len(self.entries)}')

    async def paginate(self) -> None:

        self.message = await self.ctx.send(f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}')
        self.task_loop = asyncio.create_task(self.loop())

    async def first(self) -> None:

        self.page = 0
        await self.message.edit(content=f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}')

    async def backward(self) -> None:

        if self.page <= 0:
            return

        self.page -= 1
        await self.message.edit(content=f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}')

    async def stop(self, delete: bool = True) -> None:

        self.task_loop.cancel()
        self.looping = False

        if delete is True:
            self.message = await self.message.delete()

    async def forward(self) -> None:

        if self.page >= len(self.pages) - 1:
            return

        self.page += 1
        await self.message.edit(content=f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}')

    async def last(self) -> None:

        self.page = len(self.pages) - 1
        await self.message.edit(content=f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}')


class EmbedPaginator(BasePaginator):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.header = kwargs.get('header', '')
        self.footer = kwargs.get('footer', '')

        self.title = kwargs.get('title', '')
        self.url = kwargs.get('url', '')

        self.colour = kwargs.get('colour', self.ctx.colour)
        self.image = kwargs.get('image', None)
        self.thumbnail = kwargs.get('thumbnail', None)

        self.embed = discord.Embed(colour=self.colour, title=self.title)
        self.embed.set_footer(text=self.embed_footer)

        if self.image:
            self.embed.set_image(url=self.image)
        if self.thumbnail:
            self.embed.set_thumbnail(url=self.thumbnail)
        if self.url:
            self.embed.url = self.url

    @property
    def embed_footer(self) -> str:
        additional_footer = f'| {self.kwargs.get("embed_add_footer")}' if self.kwargs.get('embed_add_footer') else ''
        return self.kwargs.get('embed_footer', f'\n\nPage: {self.page + 1}/{len(self.pages)} | Total entries: {len(self.entries)} {additional_footer}')

    async def paginate(self) -> None:

        self.embed.description = f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}'
        self.message = await self.ctx.send(embed=self.embed)

        self.task_loop = asyncio.create_task(self.loop())

    async def first(self) -> None:

        self.page = 0

        self.embed.description = f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}'
        self.embed.set_footer(text=self.embed_footer)
        await self.message.edit(embed=self.embed)

    async def backward(self) -> None:

        if self.page <= 0:
            return
        self.page -= 1

        self.embed.description = f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}'
        self.embed.set_footer(text=self.embed_footer)
        await self.message.edit(embed=self.embed)

    async def stop(self, delete: bool = True) -> None:

        self.task_loop.cancel()
        self.looping = False

        if delete is True:
            self.message = await self.message.delete()

    async def forward(self) -> None:

        if self.page >= len(self.pages) - 1:
            return
        self.page += 1

        self.embed.description = f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}'
        self.embed.set_footer(text=self.embed_footer)
        await self.message.edit(embed=self.embed)

    async def last(self) -> None:

        self.page = len(self.pages) - 1

        self.embed.description = f'{self.codeblock_start}{self.header}{self.pages[self.page]}{self.footer}{self.codeblock_end}'
        self.embed.set_footer(text=self.embed_footer)
        await self.message.edit(embed=self.embed)


class EmbedsPaginator:

    def __init__(self, **kwargs) -> None:

        self.kwargs = kwargs

        self.ctx = kwargs.get('ctx')
        self.entries = kwargs.get('entries')

        self.delete_when_done = kwargs.get('delete_when_done', True)
        self.bot = kwargs.get('bot', self.ctx.bot)
        self.timeout = kwargs.get('timeout', 300)

        self.task_loop = None
        self.message = None
        self.looping = True
        self.page = 0

        self.buttons = {
            ':first:737826967910481931': self.first,
            ':backward:737826960885153800': self.backward,
            ':stop:737826951980646491': self.stop,
            ':forward:737826943193448513': self.forward,
            ':last:737826943520473198': self.last
        }

    def check_reaction(self, payload: discord.RawReactionActionEvent) -> bool:

        if self.message is None:
            return False

        if payload.message_id != self.message.id:
            return False

        if payload.user_id not in (self.bot.owner_id, self.ctx.author.id):
            return False

        return str(payload.emoji).strip('<>') in self.buttons.keys()

    async def react(self) -> None:

        if len(self.entries) == 1:
            await self.message.add_reaction(':stop:737826951980646491')
        else:
            for emote in self.buttons.keys():
                if emote in (':start:737826967910481931', ':end:737826943520473198') and len(self.entries) < 5:
                    continue
                await self.message.add_reaction(emote)

    async def loop(self) -> None:

        await self.react()

        while self.looping is True:

            try:
                tasks = [
                    asyncio.ensure_future(self.bot.wait_for('raw_reaction_add', check=self.check_reaction)),
                    asyncio.ensure_future(self.bot.wait_for('raw_reaction_remove', check=self.check_reaction))
                ]
                done, pending = await asyncio.wait(tasks, timeout=self.timeout, return_when=asyncio.FIRST_COMPLETED)

                for task in pending:
                    task.cancel()

                if len(done) == 0:
                    raise asyncio.TimeoutError()

                await self.buttons[str(done.pop().result().emoji).strip('<>')]()

            except asyncio.TimeoutError:
                self.looping = False

        if not self.message:
            return

        if self.delete_when_done is False:
            for reaction in self.buttons.keys():
                await self.message.remove_reaction(reaction, self.bot.user)

        return await self.stop(delete=self.delete_when_done)

    async def paginate(self) -> None:

        self.message = await self.ctx.send(embed=self.entries[self.page])
        self.task_loop = asyncio.create_task(self.loop())

    async def first(self) -> None:

        self.page = 0
        await self.message.edit(embed=self.entries[self.page])

    async def backward(self) -> None:

        if self.page <= 0:
            return
        self.page -= 1

        await self.message.edit(embed=self.entries[self.page])

    async def stop(self, delete: bool = True) -> None:

        self.task_loop.cancel()
        self.looping = False

        if delete is True:
            self.message = await self.message.delete()

    async def forward(self) -> None:

        if self.page >= len(self.entries) - 1:
            return
        self.page += 1

        await self.message.edit(embed=self.entries[self.page])

    async def last(self) -> None:

        self.page = len(self.entries) - 1
        await self.message.edit(embed=self.entries[self.page])

