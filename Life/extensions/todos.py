from typing import Optional

from discord.ext import commands

from core import colours, emojis
from core.bot import Life
from utilities import context, converters, exceptions, utils


def setup(bot: Life) -> None:
    bot.add_cog(Todo(bot))


class Todo(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.group(name="todo", aliases=["todos"], invoke_without_command=True)
    async def todo(self, ctx: context.Context, *, content: Optional[str]) -> None:
        """
        Creates a todo.

        **content**: The content of your todo. Must be under 150 characters.

        **Usage:**
        `l-todo Finish documentation`
        """

        if content is not None:
            await ctx.invoke(self.todo_add, content=content)
            return

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        if not user_config.todos:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="You don't have any todos.")

        await ctx.paginate_embed(
                entries=[f"[**`{todo.id}:`**]({todo.jump_url}) {todo.content}" for todo in user_config.todos.values()],
                per_page=10,
                title=f"Todo list for **{ctx.author}**:"
        )

    @todo.command(name="list")
    async def todo_list(self, ctx: context.Context) -> None:
        """
        Shows your todos.

        **Usage:**
        `l-todo list`
        """

        await ctx.invoke(self.todo, content=None)

    @todo.command(name="add", aliases=["make", "create"])
    async def todo_add(self, ctx: context.Context, *, content: converters.TodoContentConverter) -> None:
        """
        Creates a todo.

        **content**: The content of your todo. Must be under 150 characters.

        **Usage:**
        `l-todo Finish documentation`
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)

        if len(user_config.todos) > 100:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="You have 100 todos, try finishing some before adding any more.")

        todo = await user_config.create_todo(content=str(content), jump_url=ctx.message.jump_url)

        embed = utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description=f"Todo **{todo.id}** created.")
        await ctx.reply(embed=embed)

    @todo.command(name="delete", aliases=["remove"])
    async def todo_delete(self, ctx: context.Context, todo_ids: commands.Greedy[int]) -> None:
        """
        Deletes todos.

        **todo_ids**: A list of todo ids to delete, separated by spaces.

        **Usage:**
        `l-todo delete 1 2`
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        if not user_config.todos:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="You don't have any todos.")

        todos = set()

        for todo_id in todo_ids:

            if not (todo := user_config.get_todo(todo_id)):
                raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"You don't have a todo with id **{todo_id}**.")

            todos.add(todo)

        for todo in todos:
            await todo.delete()

        await ctx.paginate_embed(
                entries=[f"[**`{todo.id}:`**]({todo.jump_url}) {todo.content}" for todo in todos],
                per_page=10,
                colour=colours.GREEN,
                title=f"Deleted **{len(todos)}** todo{'s' if len(todos) > 1 else ''}:"
        )

    @todo.command(name="clear")
    async def todo_clear(self, ctx: context.Context) -> None:
        """
        Clears your todos.

        **Usage:**
        `l-todo clear`
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        if not user_config.todos:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="You don't have any todos.")

        for todo in user_config.todos.copy().values():
            await todo.delete()

        embed = utils.embed(colour=colours.GREEN, emoji=emojis.TICK, description="Cleared your todo list.")
        await ctx.reply(embed=embed)

    @todo.command(name="edit", aliases=["update"])
    async def todo_edit(self, ctx: context.Context, todo_id: int, *, content: converters.TodoContentConverter) -> None:
        """
        Edits a todo.

        **todo_id**: The id of the todo to edit.
        **content**: The content of the todo.

        **Usage:**
        `l-todo edit 1 new content here`
        """

        user_config = await self.bot.user_manager.get_config(ctx.author.id)
        if not user_config.todos:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="You don't have any todos.")

        if not (todo := user_config.get_todo(todo_id)):
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description=f"You don't have a todo with id **{todo_id}**.")

        await todo.change_content(content=str(content), jump_url=ctx.message.jump_url)

        embed = utils.embed(
            colour=colours.GREEN,
            emoji=emojis.TICK,
            description='Edited content of todo.',
        )

        await ctx.reply(embed=embed)
