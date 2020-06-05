from datetime import datetime

import discord
from discord.ext import commands

from cogs.utilities import exceptions


class Todo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='todo', invoke_without_command=True)
    async def todo(self, ctx):
        """
        Base command for todos.
        """

        return await ctx.send(f'Please choose a valid subcommand. Use `{self.bot.config.PREFIX}help todo` for more '
                              f'information.')

    @todo.command(name='list')
    async def todo_list(self, ctx):
        """
        Display a list of your current todo's.
        """

        query = 'SELECT * FROM todos WHERE owner_id = $1 ORDER BY time_added'

        todos = await self.bot.db.fetch(query, ctx.author.id)
        if not todos:
            return await ctx.send('You do not have any todos.')

        entries = [f'{index + 1}. {todo["todo"]}' for index, todo in enumerate(todos)]
        title = f"{ctx.author}'s todo list."
        return await ctx.paginate_embed(entries=entries, entries_per_page=10, title=title)

    @todo.command(name='add', aliases=['make', 'create'])
    async def todo_add(self, ctx, *, content: str):
        """
        Creates a todo.

        `content`: The content of your todo. Can not be more than 200 characters.
        """

        if len(content) > 180:
            raise exceptions.ArgumentError('Your todo can not be more than 180 characters long.')

        todo_count = await self.bot.db.fetchrow('SELECT count(*) as c FROM todos WHERE owner_id = $1', ctx.author.id)
        if todo_count['c'] > 200:
            message = f'You already have `{todo_count["c"]}` todos, you should do some of those before adding more.'
            return await ctx.send(message)

        await self.bot.db.execute('INSERT INTO todos VALUES ($1, $2, $3)', ctx.author.id, datetime.now(), content)

        embed = discord.Embed(title='Your todo was created.', colour=discord.Colour.gold())
        embed.add_field(name='Content:', value=content)
        return await ctx.send(embed=embed)

    @todo.command(name='delete', aliases=['remove'])
    async def todo_delete(self, ctx, *, todo_ids: str):
        """
        Deletes a todo.

        `todo_ids`: The ids of the todos to delete. You can provide a list of ids and they will all be deleted.
        """

        todos = await self.bot.db.fetch('SELECT * FROM todos WHERE owner_id = $1 ORDER BY time_added', ctx.author.id)
        if not todos:
            return await ctx.send('You do not have any todos.')

        todos = {f'{index + 1}': todo for index, todo in enumerate(todos)}
        todos_to_remove = []

        todo_ids = todo_ids.split(' ')
        for todo_id in todo_ids:

            if not todo_id.isdigit():
                return await ctx.send(f'`{todo_id}` is not a valid todo id.')
            if todo_id not in todos.keys():
                return await ctx.send(f'You do not have a todo with id `{todo_id}`.')
            if todo_id in todos_to_remove:
                return await ctx.send(f'You provided todo id `{todo_id}` more than once.')
            todos_to_remove.append(todo_id)

        query = 'DELETE FROM todos WHERE owner_id = $1 and time_added = $2'
        entries = [(todos[todo_id]['owner_id'], todos[todo_id]['time_added']) for todo_id in todos_to_remove]
        await self.bot.db.executemany(query, entries)

        contents = '\n'.join([f'{todo_id}. {todos[todo_id]["todo"]}' for todo_id in todos_to_remove])
        embed = discord.Embed(title=f'Deleted {len(todos_to_remove)} todo(s).', colour=discord.Colour.gold())
        embed.add_field(name='Contents:', value=contents)
        return await ctx.send(embed=embed)

    @todo.command(name='clear')
    async def todo_clear(self, ctx):
        """
        Clears your todo list.
        """

        todos = await self.bot.db.fetch('SELECT * FROM todos WHERE owner_id = $1 ORDER BY time_added', ctx.author.id)
        if not todos:
            return await ctx.send('You don not have any todos.')

        await self.bot.db.execute('DELETE FROM todos WHERE owner_id = $1 RETURNING *', ctx.author.id)

        embed = discord.Embed(title=f'Cleared your todo list of {len(todos)} todo(s).', colour=discord.Colour.gold())
        return await ctx.send(embed=embed)

    @todo.command(name='edit')
    async def todo_edit(self, ctx, todo_id: str, *, content: str):
        """
        Edits the todo with the given id.

        `todo_id`: The id of the todo to edit.
        `content`: The content of which to change the todo to.
        """

        todos = await self.bot.db.fetch('SELECT * FROM todos WHERE owner_id = $1 ORDER BY time_added', ctx.author.id)
        if not todos:
            return await ctx.send('You don not have any todos.')

        todos = {f'{index + 1}': todo for index, todo in enumerate(todos)}

        if not todo_id.isdigit():
            return await ctx.send(f'`{todo_id}` is not a valid todo id.')
        if todo_id not in todos.keys():
            return await ctx.send(f'You do not have a todo with id `{todo_id}`.')

        todo_to_edit = todos[todo_id]

        query = 'UPDATE todos SET todo = $1 WHERE owner_id = $2 and time_added = $3'
        await self.bot.db.execute(query, content, todo_to_edit['owner_id'], todo_to_edit['time_added'])

        embed = discord.Embed(title=f'Updated your todo.', colour=discord.Colour.gold())
        embed.add_field(name='Old content:', value=todo_to_edit['todo'], inline=False)
        embed.add_field(name='New content:', value=content, inline=False)
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Todo(bot))
