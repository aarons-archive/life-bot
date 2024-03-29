# Future
from __future__ import annotations

# Packages
import discord
from discord.ext import commands

# My stuff
from core import colours, emojis, values
from core.bot import Life
from utilities import converters, custom, exceptions, objects, utils


def setup(bot: Life) -> None:
    bot.add_cog(Tags(bot=bot))


class Tags(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

    @commands.group(name="tag", aliases=["tags"], invoke_without_command=True)
    async def _tag(self, ctx: custom.Context, *, name: converters.TagNameConverter) -> None:
        """
        Gets a tag.

        **name**: The name of the tag you want to get.
        """

        name = str(name)
        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if not (tags := guild_config.get_tags_matching(name=name)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There are no tags with the name **{name}**."
            )

        tag = tags[0]

        if tag.name != name:
            msg = f"Maybe you meant one of these?\n{values.NL.join(f'- **{tag.name}**' for tag in tags[0:])}" if len(tags) > 1 else ""
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There are no tags with the name **{name}**. {msg}"
            )

        if tag.alias:
            tag = guild_config.get_tag(tag_id=tag.alias)

        await ctx.reply(tag.content)

    @_tag.command(name="raw")
    async def tag_raw(self, ctx: custom.Context, *, name: converters.TagNameConverter) -> None:
        """
        Gets a tags raw content.

        **name**: The name of the tag you want to get.
        """

        name = str(name)
        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if not (tags := guild_config.get_tags_matching(name=name)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There are no tags with the name **{name}**."
            )

        tag = tags[0]

        if tag.name != name:
            msg = f"Maybe you meant one of these?\n{values.NL.join(f'- **{tag.name}**' for tag in tags[0:])}" if len(tags) > 1 else ""
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There are no tags with the name **{name}**. {msg}"
            )

        if tag.alias:
            tag = guild_config.get_tag(tag_id=tag.alias)

        await ctx.reply(discord.utils.escape_markdown(tag.content))

    @_tag.command(name="create", aliases=["make"])
    async def tag_create(self, ctx: custom.Context, name: converters.TagNameConverter, *, content: converters.TagContentConverter) -> None:
        """
        Creates a tag.

        **name**: The name of the tag.
        **content**: The content of the tag.
        """

        name = str(name)
        content = str(content)

        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if tag_check := guild_config.get_tag(tag_name=name):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There is already a tag with the name **{tag_check.name}**.",
            )

        tag = await guild_config.create_tag(user_id=ctx.author.id, name=name, content=content, jump_url=ctx.message.jump_url)

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Created tag with name **{tag.name}**."
            )
        )

    @_tag.command(name="alias")
    async def tag_alias(self, ctx: custom.Context, alias: converters.TagNameConverter, original: converters.TagNameConverter) -> None:
        """
        Alias a new tag to a pre-existing tag.

        **alias**: The alias, the name of this new tag.
        **name**: The name of the tag to point the alias at.
        """

        alias = str(alias)
        original = str(original)

        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if tag_check := guild_config.get_tag(tag_name=alias):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There is already a tag with the name **{tag_check.name}**.",
            )

        if not (original_tag := guild_config.get_tag(tag_name=original)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description=f"There are no tags with the name **{original}** to alias too.",
            )

        if original_tag.alias is not None:
            original_tag = guild_config.get_tag(tag_id=original_tag.alias)

        tag = await guild_config.create_tag_alias(user_id=ctx.author.id, name=alias, original=original_tag.id, jump_url=ctx.message.jump_url)

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Tag alias from **{tag.name}** to **{original}** was created.",
            )
        )

    @_tag.command(name="claim")
    async def tag_claim(self, ctx: custom.Context, *, tag: objects.Tag) -> None:
        """
        Claims a tag if its owner has left the server.

        **name**: The name of the tag to claim.
        """

        if ctx.guild.get_member(tag.user_id):
            raise exceptions.EmbedError(
                colour=colours.RED,
                emoji=emojis.CROSS,
                description="The owner of that tag is still in this server."
            )

        await tag.change_owner(ctx.author.id)

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Transferred tag **{tag.name}** to you."
            )
        )

    @_tag.command(name="transfer")
    async def tag_transfer(self, ctx: custom.Context, tag: objects.Tag, *, member: discord.Member) -> None:
        """
        Transfers a tag to another member.

        **name**: The name of the tag to transfer.
        **member**: The member to transfer the tag too. Can be their ID, Username, Nickname or @Mention.
        """

        if member.bot:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="You can not transfer tags to bots."
            )
        if tag.user_id != ctx.author.id:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="You do not own that tag."
            )
        if tag.user_id == member.id:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="You can not transfer tags to yourself."
            )

        await tag.change_owner(user_id=member.id)

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                emoji=emojis.TICK,
                description=f"Transferred tag **{tag.name}** from **{ctx.author}** to **{ctx.guild.get_member(tag.user_id)}**.",
            )
        )

    @_tag.command(name="edit")
    async def tag_edit(self, ctx: custom.Context, tag: objects.Tag, *, content: converters.TagContentConverter) -> None:
        """
        Edits a tags content.

        **name**: The name of the tag to edit the content of.
        **content:** The content to edit the tag with.
        """

        if tag.user_id != ctx.author.id:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="You do not own that tag."
            )

        await tag.change_content(str(content))

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                description=f"Edited content of tag with name **{tag.name}**."
            )
        )

    @_tag.command(name="delete", aliases=["remove"])
    async def tag_delete(self, ctx: custom.Context, *, tag: objects.Tag) -> None:
        """
        Deletes a tag.

        **name**: The name of the tag to delete.
        """

        if tag.user_id != ctx.author.id:
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="You do not own that tag."
            )

        await tag.delete()

        await ctx.reply(
            embed=utils.embed(
                colour=colours.GREEN,
                description=f"Deleted tag with name **{tag.name}**.")
        )

    @_tag.command(name="search")
    async def tag_search(self, ctx: custom.Context, *, name: converters.TagNameConverter) -> None:
        """
        Displays a list of tags that are similar to the search.

        **name**: The search term to look for tags with.
        """

        name = str(name)
        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if not (tags := guild_config.get_tags_matching(name=name, limit=100)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"There are no tags similar to the search **{name}**."
            )

        await ctx.paginate_embed(
            entries=[f"**{index + 1}.** {tag.name.replace(name, f'**{name}**')}" for index, tag in enumerate(tags)],
            per_page=25,
            title=f"Tags matching: **{name}**",
        )

    @_tag.command(name="list")
    async def tag_list(self, ctx: custom.Context, *, person: discord.Member = utils.MISSING) -> None:
        """
        Gets a list of yours or someone else's tags.

        **member**: The member to get a tag list for. Can be their ID, Username, Nickname or @Mention.
        """

        member = person or ctx.author
        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if not (tags := guild_config.get_user_tags(member.id)):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description=f"**{member}** does not have any tags."
            )

        await ctx.paginate_embed(
            entries=[f"**{index + 1}.** {tag.name}" for index, tag in enumerate(tags)],
            per_page=25,
            title=f"Tags for **{member}:**",
        )

    @_tag.command(name="all")
    async def tag_all(self, ctx: custom.Context) -> None:
        """
        Gets a list of all tags in this server.
        """

        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)

        if not (tags := guild_config.get_all_tags()):
            raise exceptions.EmbedError(
                colour=colours.RED,
                description="There are no available tags."
            )

        await ctx.paginate_embed(
            entries=[f"**{index + 1}.** {tag.name}" for index, tag in enumerate(tags)],
            per_page=25,
            title=f"Tags for **{ctx.guild}:**",
        )

    @_tag.command(name="info")
    async def tag_info(self, ctx: custom.Context, *, tag: objects.Tag) -> None:
        """
        Displays information about a tag.

        **name**: The name of the tag to get the information for.
        """

        guild_config = await self.bot.guild_manager.get_config(ctx.guild.id)
        owner = ctx.guild.get_member(tag.user_id)

        await ctx.reply(
            embed=discord.Embed(
                colour=colours.MAIN,
                title=f"{tag.name}",
                description=f"**Owner:** {owner.mention if owner else '*Not found*'} ({tag.user_id})\n"
                            f"**Claimable:** {owner is None}\n"
                            f"**Alias:** {guild_config.get_tag(tag_id=tag.alias).name if tag.alias else None}\n"
                            f"**Created on:** {utils.format_datetime(tag.created_at)}\n"
                            f"**Created:** {utils.format_difference(tag.created_at)} ago\n",
            )
        )
