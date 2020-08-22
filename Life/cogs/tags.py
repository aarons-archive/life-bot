"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

from datetime import datetime

import discord
from discord.ext import commands

from utilities import context, converters, exceptions


class Tags(commands.Cog):

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.group(name='tag', aliases=['tags'], invoke_without_command=True)
    async def tag(self, ctx: context.Context, *, name: converters.TagName) -> None:
        """
        Get a tag by it's name or alias's.

        `name`: The name or alias of the tag you want to find.
        """

        tags = await self.bot.db.fetch('SELECT * FROM tags WHERE guild_id = $1 AND name % $2 ORDER BY name <-> $2 LIMIT 5', ctx.guild.id, name)
        if not tags:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`.')

        if not tags[0]['name'] == name:

            extra_msg = ''
            if len(tags) > 0:
                extras = '\n'.join([f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags[0:])])
                extra_msg = f'Maybe you meant one of these?\n{extras}'

            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`. {extra_msg}')

        if tags[0]['alias'] is not None:
            tags = await self.bot.db.fetch('SELECT * FROM tags WHERE guild_id = $1 AND name = $2', ctx.guild.id, tags[0]['alias'])

        await ctx.send(tags[0]['content'])

    @tag.command(name='raw')
    async def tag_raw(self, ctx: context.Context, *, name: converters.TagName) -> None:
        """
        Get a tags raw content.

        `name`: The name of the tag you want to find.
        """

        tags = await self.bot.db.fetch('SELECT * FROM tags WHERE guild_id = $1 AND name % $2 ORDER BY name <-> $2 LIMIT 5', ctx.guild.id, name)
        if not tags:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`.')

        if not tags[0]['name'] == name:

            extra_msg = ''
            if len(tags) > 0:
                extras = '\n'.join([f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags[0:])])
                extra_msg = f'Maybe you meant one of these?\n{extras}'

            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`. {extra_msg}')

        if tags[0]['alias'] is not None:
            tags = await self.bot.db.fetch('SELECT * FROM tags WHERE guild_id = $1 AND name = $2', ctx.guild.id, tags[0]['alias'])

        await ctx.send(discord.utils.escape_markdown(tags[0]['content']))

    @tag.command(name='create', aliases=['make'])
    async def tag_create(self, ctx: context.Context, name: converters.TagName, *, content: commands.clean_content) -> None:
        """
        Create a tag.

        `name`: The name of the tag to create.
        `content`: The content of your tag.
        """

        tag = await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = $1 AND name = $2', ctx.guild.id, name)
        if tag:
            raise exceptions.ArgumentError(f'There is already a tag in this server with the name `{name}`.')

        if len(str(content)) > 1024:
            raise exceptions.ArgumentError('Your tag content can not be more than 1024 characters.')

        await self.bot.db.execute('INSERT INTO tags VALUES ($1, $2, $3, $4, $5, $6)', ctx.author.id, ctx.guild.id, name, content, None, datetime.now())

        embed = discord.Embed(colour=ctx.colour, title='Tag created:')
        embed.add_field(name='Name:', value=f'{name}', inline=False)
        embed.add_field(name='Content:', value=f'{content}', inline=False)
        await ctx.send(embed=embed)

    @tag.command(name='edit')
    async def tag_edit(self, ctx: context.Context, name: converters.TagName, *, content: commands.clean_content) -> None:
        """
        Edit a tags content.

        `name`: The name of the tag to edit the content of.
        `content:` The content of the edited tag.
        """

        tag = await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = $1 AND owner_id = $2 and name = $3', ctx.guild.id, ctx.author.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'You do not have any tags in this server with the name `{name}`.')

        if len(str(content)) > 1024:
            raise exceptions.ArgumentError('Your tag content can not be more than 1024 characters.')

        await self.bot.db.execute('UPDATE tags SET content = $1 WHERE guild_id = $2 AND name = $3', content, ctx.guild.id, name)

        embed = discord.Embed(colour=ctx.colour, title='Tag edited:')
        embed.add_field(name='Old content:', value=f'{tag["content"]}', inline=False)
        embed.add_field(name='New content:', value=f'{content}', inline=False)
        await ctx.send(embed=embed)

    @tag.command(name='claim')
    async def tag_claim(self, ctx: context.Context, *, name: converters.TagName) -> None:
        """
        Claim a tag if it's owner has left the server.

        `name`: The name of the tag to claim.
        """

        tag = await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = $1 AND name = $2', ctx.guild.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`.')

        owner = ctx.guild.get_member(tag['owner_id'])
        if owner is not None:
            raise exceptions.ArgumentError(f'The owner of that tag is still in the server.')

        await self.bot.db.execute('UPDATE tags SET owner_id = $1 WHERE guild_id = $2 AND name = $3', ctx.author.id, ctx.guild.id, name)

        embed = discord.Embed(colour=ctx.colour, title='Tag claimed:')
        embed.add_field(name='Previous owner:', value=f'{tag["owner_id"]}', inline=False)
        embed.add_field(name='New owner:', value=f'{ctx.author.mention}', inline=False)
        await ctx.send(embed=embed)

    @tag.command(name='alias')
    async def tag_alias(self, ctx: context.Context, alias: converters.TagName, original: converters.TagName) -> None:
        """
        Alias a name to a tag.

        `alias`: The alias of the tag you want.
        `name`: The name of the tag to point the alias at.
        """

        alias_tag = await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = $1 AND alias = $2', ctx.guild.id, alias)
        if alias_tag:
            raise exceptions.ArgumentError(f'There is already a tag alias in this server with the name `{alias}`.')

        original_tag = await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = $1 AND name = $2', ctx.guild.id, original)
        if not original_tag:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{original}`.')

        await self.bot.db.execute('INSERT INTO tags VALUES ($1, $2, $3, $4, $5, $6)', ctx.author.id, ctx.guild.id, alias, None, original, datetime.now())

        embed = discord.Embed(colour=ctx.colour, title='Tag alias created:')
        embed.add_field(name='Alias:', value=f'{alias}', inline=False)
        embed.add_field(name='Links to:', value=f'{original}', inline=False)
        await ctx.send(embed=embed)

    @tag.command(name='transfer')
    async def tag_transfer(self, ctx: context.Context, name: converters.TagName, *, member: discord.Member) -> None:
        """
        Transfer a tag to another member.

        `name`: The name of the tag to transfer.
        `member`: The member to transfer the tag too. Can be a name, id or mention.
        """

        if member.bot:
            raise exceptions.ArgumentError('You can not transfer tags to bots.')

        tag = await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = $1 AND owner_id = $2 and name = $3', ctx.guild.id, ctx.author.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'You do not have any tags in this server with the name `{name}`.')

        await self.bot.db.execute('UPDATE tags SET owner_id = $1 WHERE guild_id = $2 AND name = $3', member.id, ctx.guild.id, name)

        embed = discord.Embed(colour=ctx.colour, title='Tag transferred:')
        embed.add_field(name='Previous owner:', value=f'{ctx.author.mention}', inline=False)
        embed.add_field(name='New owner:', value=f'{member.mention}', inline=False)
        await ctx.send(embed=embed)

    @tag.command(name='delete', aliases=['remove'])
    async def tag_delete(self, ctx: context.Context, *, name: converters.TagName) -> None:
        """
        Delete a tag.

        `name`: The name of the tag to delete.
        """

        tag = await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = $1 AND owner_id = $2 AND name = $3', ctx.guild.id, ctx.author.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'You do not have any tags in this server with the name `{name}`.')

        await self.bot.db.execute('DELETE FROM tags WHERE guild_id = $1 AND owner_id = $2 AND name = $3', ctx.guild.id, ctx.author.id, name)
        await self.bot.db.execute('DELETE FROM tags WHERE guild_id = $1 AND alias = $2', ctx.guild.id, name)

        embed = discord.Embed(colour=ctx.colour, title='Tag deleted:')
        embed.add_field(name='Name:', value=f'{name}', inline=False)
        embed.add_field(name='Content:', value=f'{tag["content"]}', inline=False)
        await ctx.send(embed=embed)

    @tag.command(name='search')
    async def tag_search(self, ctx: context.Context, *, name: converters.TagName) -> None:
        """
        Display a list of tags that are similar to the search.

        `name`: The search terms to look for tags with.
        """

        tags = await self.bot.db.fetch('SELECT * FROM tags WHERE guild_id = $1 AND name % $2 ORDER BY name <-> $2 LIMIT 100', ctx.guild.id, name)
        if not tags:
            raise exceptions.ArgumentError(f'There are no tags in this server similar to the term `{name}`.')

        entries = [f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags)]
        await ctx.paginate_embed(entries=entries, per_page=25, header=f'Tags matching: `{name}`\n\n')

    @tag.command(name='list')
    async def tag_list(self, ctx: context.Context, *, member: discord.Member = None) -> None:
        """
        Get a list of yours or someones else's tags.

        `member`: The member to get a tag list for. Can be a name, id or mention.
        """

        if not member:
            member = ctx.author

        tags = await self.bot.db.fetch('SELECT * FROM tags WHERE guild_id = $1 and owner_id = $2', ctx.guild.id, member.id)
        if not tags:
            raise exceptions.ArgumentError(f'`{member}` has no tags in this server.')

        entries = [f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags)]
        await ctx.paginate_embed(entries=entries, per_page=25, title=f'{member}\'s tags')

    @tag.command(name='all')
    async def tag_all(self, ctx: context.Context) -> None:
        """
        Get a list of all tags in this server.
        """

        tags = await self.bot.db.fetch('SELECT * FROM tags WHERE guild_id = $1', ctx.guild.id)
        if not tags:
            raise exceptions.ArgumentError(f'There are no tags in this server.')

        entries = [f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags)]
        await ctx.paginate_embed(entries=entries, per_page=25, title=f'{ctx.guild}\'s tags')

    @tag.command(name='info')
    async def tag_info(self, ctx: context.Context, *, name: converters.TagName) -> None:
        """
        Displays information about a tag.

        `name`: The name of the tag to get the information for.
        """

        tag = await self.bot.db.fetchrow('SELECT * FROM tags WHERE guild_id = $1 AND name = $2', ctx.guild.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`.')

        owner = ctx.guild.get_member(tag['owner_id'])

        embed = discord.Embed(colour=ctx.colour, title=f'{tag["name"]}')
        embed.description = f'`Owner:` {owner.mention if owner else "None"} ({tag["owner_id"]})\n`Claimable:` {owner is None}\n`Alias:` {tag["alias"]}'
        embed.set_footer(text=f'Created on {datetime.strftime(tag["created_at"], self.bot.time_format)}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Tags(bot))
