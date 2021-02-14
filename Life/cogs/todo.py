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
#

import discord
import pendulum
from discord.ext import commands

from bot import Life
from utilities import context, exceptions


class Todo(commands.Cog):

    def __init__(self, bot: Life):
        self.bot = bot

    @commands.group(name='todo', aliases=['todos'], invoke_without_command=True)
    async def todo(self, ctx: context.Context, content: str = None) -> None:
        """
        Display a list of your todos.
        """

        if content is not None:
            await ctx.invoke(self.todo_add, content=content)
            return

        todos = await self.bot.db.fetch('SELECT * FROM todos WHERE owner_id = $1 ORDER BY time_added', ctx.author.id)
        if not todos:
            raise exceptions.GeneralError('You do not have any todos.')

        entries = [f'[`{index + 1}`]({todo["link"]}) {todo["todo"]}' for index, todo in enumerate(todos)]
        await ctx.paginate_embed(entries=entries, per_page=10, header=f'**{ctx.author}\'s todo list:**\n\n')

    @todo.command(name='add', aliases=['make', 'create'])
    async def todo_add(self, ctx: context.Context, *, content: commands.clean_content) -> None:
        """
        Creates a todo.

        `content`: The content of your todo. Can not be more than 180 characters.
        """
        content = str(content)

        if len(content) > 180:
            raise exceptions.ArgumentError('Your todo can not be more than 180 characters long.')

        todo_count = await self.bot.db.fetchrow('SELECT count(*) as c FROM todos WHERE owner_id = $1', ctx.author.id)
        if todo_count['c'] > 100:
            raise exceptions.GeneralError(f'You have too many todos, try removing some of them before adding more.')

        query = 'INSERT INTO todos (owner_id, time_added, todo, link) VALUES ($1, $2, $3, $4)'
        await self.bot.db.execute(query, ctx.author.id, pendulum.now(tz='UTC'), content, ctx.message.jump_url)

        await ctx.send('Your todo was created.')

    @todo.command(name='delete', aliases=['remove'])
    async def todo_delete(self, ctx: context.Context, *, todo_ids: str) -> None:
        """
        Deletes a todo.

        `todo_ids`: The ids of the todos to delete. You can provide a list of ids and they will all be deleted.
        """

        todos = await self.bot.db.fetch('SELECT * FROM todos WHERE owner_id = $1 ORDER BY time_added', ctx.author.id)
        if not todos:
            raise exceptions.GeneralError(f'You do not have any todos.')

        todos = {index + 1: todo for index, todo in enumerate(todos)}
        todos_to_remove = []

        for todo_id in todo_ids.split(' '):

            try:
                todo_id = int(todo_id)
            except ValueError:
                raise exceptions.ArgumentError(f'`{todo_id}` is not a valid todo id.')

            if todo_id not in todos.keys():
                raise exceptions.ArgumentError(f'You do not have a todo with the id `{todo_id}`.')
            if todo_id in todos_to_remove:
                raise exceptions.ArgumentError(f'You provided the todo id `{todo_id}` more than once.')
            todos_to_remove.append(todo_id)

        query = 'DELETE FROM todos WHERE owner_id = $1 and time_added = $2'
        entries = [(todos[todo_id]['owner_id'], todos[todo_id]['time_added']) for todo_id in todos_to_remove]
        await self.bot.db.executemany(query, entries)

        embed = discord.Embed(colour=ctx.colour, description=f'**Deleted** `{len(todos_to_remove)}` **todo(s):**')
        embed.add_field(name='Contents:', value='\n'.join(f'[`{todo_id}`]({todos[todo_id]["link"]}) {todos[todo_id]["todo"]}' for todo_id in todos_to_remove))
        await ctx.send(embed=embed)

    @todo.command(name='clear')
    async def todo_clear(self, ctx: context.Context) -> None:
        """
        Clears your todo list.
        """

        todos = await self.bot.db.fetch('SELECT * FROM todos WHERE owner_id = $1 ORDER BY time_added', ctx.author.id)
        if not todos:
            raise exceptions.GeneralError('You don not have any todos.')

        await self.bot.db.execute('DELETE FROM todos WHERE owner_id = $1 RETURNING *', ctx.author.id)
        await ctx.send(f'Cleared your todo list of `{len(todos)}` todo(s).')

    @todo.command(name='edit', aliases=['update'])
    async def todo_edit(self, ctx: context.Context, todo_id: str, *, content: commands.clean_content) -> None:
        """
        Edits the todo with the given id.

        `todo_id`: The id of the todo to edit.
        `content`: The content of the new todo.
        """

        todos = await self.bot.db.fetch('SELECT * FROM todos WHERE owner_id = $1 ORDER BY time_added', ctx.author.id)
        if not todos:
            raise exceptions.GeneralError('You do not have any todos.')

        content = str(content)
        if len(content) > 180:
            raise exceptions.ArgumentError('Your todo can not be more than 180 characters long.')

        todos = {index + 1: todo for index, todo in enumerate(todos)}

        try:
            todo_id = int(todo_id)
        except ValueError:
            raise exceptions.ArgumentError(f'`{todo_id}` is not a valid todo id.')

        if todo_id not in todos.keys():
            raise exceptions.ArgumentError(f'You do not have a todo with the id `{todo_id}`.')

        todo = todos[todo_id]

        query = 'UPDATE todos SET todo = $1, link = $2 WHERE owner_id = $3 and time_added = $4'
        await self.bot.db.execute(query, content, ctx.message.jump_url, todo['owner_id'], todo['time_added'])

        embed = discord.Embed(colour=ctx.colour, description=f'**Updated your todo:**')
        embed.add_field(name='Old content:', value=todo['todo'], inline=False)
        embed.add_field(name='New content:', value=content, inline=False)
        await ctx.send(embed=embed)


def setup(bot: Life):
    bot.add_cog(Todo(bot))
