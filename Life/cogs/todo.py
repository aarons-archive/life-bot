#  Life
#  Copyright (C) 2020 Axel#3456
#
#  Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
#  Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
#  PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.

from typing import Optional

import discord
from discord.ext import commands

import config
from bot import Life
from utilities import context, exceptions


class Todo(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.group(name='todo', aliases=['todos'], invoke_without_command=True)
    async def todo(self, ctx: context.Context, *, content: Optional[str]) -> None:
        """
        Display a list of your todos.
        """

        if content is not None:
            await ctx.invoke(self.todo_add, content=content)
            return

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not user_config.todos:
            raise exceptions.GeneralError('You do not have any todos.')

        entries = [f'[`{todo.id}`]({todo.jump_url}) {todo.content}' for todo in user_config.todos.values()]
        await ctx.paginate_embed(entries=entries, per_page=10, title=f'`{ctx.author.name}`\'s todo list:')

    @todo.command(name='list')
    async def todo_list(self, ctx: context.Context) -> None:
        """
        View a list of your todos.
        """
        await ctx.invoke(self.todo, content=None)

    @todo.command(name='add', aliases=['make', 'create'])
    async def todo_add(self, ctx: context.Context, *, content: commands.clean_content) -> None:
        """
        Create a todo.

        `content`: The content of your todo. Can not be more than 180 characters.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if len(user_config.todos) > 100:
            raise exceptions.GeneralError('You have too many todos. Try doing some of them before adding more.')

        if len(str(content)) > 180:
            raise exceptions.ArgumentError('Your todo can not be more than 180 characters long.')

        todo = await user_config.create_todo(content=str(content), jump_url=ctx.message.jump_url)
        await ctx.reply(f'Todo with id `{todo.id}` was created.')

    @todo.command(name='delete', aliases=['remove'])
    async def todo_delete(self, ctx: context.Context, *, todo_ids: str) -> None:
        """
        Delete todos with the given ids.

        `todo_ids`: A list of todo id's to delete, separated by spaces.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not user_config.todos:
            raise exceptions.GeneralError('You do not have any todos.')

        todos_to_delete = []
        for todo_id in todo_ids.split(' '):

            try:
                todo_id = int(todo_id)
            except ValueError:
                raise exceptions.ArgumentError(f'`{todo_id}` is not a valid todo id.')

            if not (todo := user_config.get_todo(todo_id)):
                raise exceptions.ArgumentError(f'You do not have a todo with the id `{todo_id}`.')
            if todo in todos_to_delete:
                raise exceptions.ArgumentError(f'You provided the id `{todo_id}` more than once.')

            todos_to_delete.append(todo)

        embed = discord.Embed(colour=config.MAIN, title=f'Deleted `{len(todos_to_delete)}` todo{"s" if len(todos_to_delete) > 1 else ""}:')
        embed.add_field(name='Contents: ', value='\n'.join(f'[`{todo.id}`]({todo.jump_url}) {todo.content}' for todo in todos_to_delete))

        for todo in todos_to_delete:
            await todo.delete()

        await ctx.reply(embed=embed)

    @todo.command(name='clear')
    async def todo_clear(self, ctx: context.Context) -> None:
        """
        Clear your todo list.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not user_config.todos:
            raise exceptions.GeneralError('You do not have any todos.')

        count = len(user_config.todos)
        for todo in user_config.todos.copy().values():
            await todo.delete()

        await ctx.reply(f'Cleared your todo list of `{count}` todo{"s" if count > 1 else ""}.')

    @todo.command(name='edit', aliases=['update'])
    async def todo_edit(self, ctx: context.Context, todo_id: str, *, content: commands.clean_content) -> None:
        """
        Edit the todo with the given id.

        `todo_id`: The id of the todo to edit.
        `content`: The content of the new todo.
        """

        user_config = await self.bot.user_manager.get_or_create_config(ctx.author.id)

        if not user_config.todos:
            raise exceptions.GeneralError('You do not have any todos.')

        if len(str(content)) > 180:
            raise exceptions.ArgumentError('Your todo can not be more than 180 characters long.')

        try:
            id = int(todo_id)
        except ValueError:
            raise exceptions.ArgumentError(f'`{todo_id}` is not a valid todo id.')

        if not (todo := user_config.todos.get(id)):
            raise exceptions.ArgumentError(f'You do not have a todo with the id `{todo_id}`.')

        await todo.change_content(content=str(content), jump_url=ctx.message.jump_url)
        await ctx.reply(f'Edited content of todo with id `{todo_id}`.')


def setup(bot: Life) -> None:
    bot.add_cog(Todo(bot=bot))
