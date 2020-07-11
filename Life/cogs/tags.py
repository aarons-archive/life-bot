"""
Life Discord bot
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public
License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see
<https://www.gnu.org/licenses/>.
"""

from datetime import datetime

import discord
from discord.ext import commands

from cogs.utilities import exceptions, converters


class Tags(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='tag', invoke_without_command=True)
    async def tag(self, ctx, *, name: converters.TagName):
        """
        Get a tag by it's name or alias's.

        `name`: The name or alias of the tag you want to find.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND name % $2 ORDER BY name <-> $2 LIMIT 5'
        tags = await self.bot.db.fetch(query, ctx.guild.id, name)
        if not tags:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`.')

        if not tags[0]['name'] == name:

            extra_msg = ''
            if len(tags) > 0:
                extras = '\n'.join([f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags[0:])])
                extra_msg = f'Maybe you meant one of these?\n{extras}'

            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`. {extra_msg}')

        if tags[0]['alias'] is not None:
            query = 'SELECT * FROM tags WHERE server_id = $1 AND name = $2'
            tags = await self.bot.db.fetch(query, ctx.guild.id, tags[0]['alias'])

        return await ctx.send(tags[0]['content'])

    @tag.command(name='raw')
    async def tag_raw(self, ctx, *, name: converters.TagName):
        """
        Get a tags raw content.

        `name`: The name of the tag you want to find.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND name % $2 ORDER BY name <-> $2 LIMIT 5'
        tags = await self.bot.db.fetch(query, ctx.guild.id, name)
        if not tags:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`.')

        if not tags[0]['name'] == name:

            extra_msg = ''
            if len(tags) > 0:
                extras = '\n'.join([f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags[0:])])
                extra_msg = f'Maybe you meant one of these?\n{extras}'

            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`. {extra_msg}')

        if tags[0]['alias'] is not None:
            query = 'SELECT * FROM tags WHERE server_id = $1 AND name = $2'
            tags = await self.bot.db.fetch(query, ctx.guild.id, tags[0]['alias'])

        return await ctx.send(discord.utils.escape_markdown(tags[0]['content']))

    @tag.command(name='create', aliases=['make'])
    async def tag_create(self, ctx, name: converters.TagName, *, content: commands.clean_content):
        """
        Creates a tag.

        `name`: The name of the tag to create.
        `content`: The content of your tag.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND name = $2'
        tag = await self.bot.db.fetchrow(query, ctx.guild.id, name)
        if tag:
            raise exceptions.ArgumentError(f'There is already a tag in this server with the name `{name}`.')

        if len(str(content)) > 1024:
            raise exceptions.ArgumentError('Your tag content can not be more than 1024 characters.')

        query = 'INSERT INTO tags VALUES ($1, $2, $3, $4, $5, $6)'
        await self.bot.db.execute(query, ctx.author.id, ctx.guild.id, name, content, None, datetime.now())

        embed = discord.Embed(colour=discord.Colour.gold(), title='Tag created:')
        embed.add_field(name='Name:', value=f'{name}', inline=False)
        embed.add_field(name='Content:', value=f'{content}', inline=False)
        return await ctx.send(embed=embed)

    @tag.command(name='edit')
    async def tag_edit(self, ctx, name: converters.TagName, *, content: commands.clean_content):
        """
        Edits a tags content.

        `name`: The name of the tag to edit the content of.
        `content:` The content of the edited tag.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND owner_id = $2 and name = $3'
        tag = await self.bot.db.fetchrow(query, ctx.guild.id, ctx.author.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'You do not have any tags in this server with the name `{name}`.')

        if len(str(content)) > 1024:
            raise exceptions.ArgumentError('Your tag content can not be more than 1024 characters.')

        query = 'UPDATE tags SET content = $1 WHERE server_id = $2 AND name = $3'
        await self.bot.db.execute(query, content, ctx.guild.id, name)

        embed = discord.Embed(colour=discord.Colour.gold(), title='Tag edited:')
        embed.add_field(name='Old content:', value=f'{tag["content"]}', inline=False)
        embed.add_field(name='New content:', value=f'{content}', inline=False)
        return await ctx.send(embed=embed)

    @tag.command(name='claim')
    async def tag_claim(self, ctx, *, name: converters.TagName):
        """
        Claim a tag if it's owner has left the server.

        `name`: The name of the tag to claim.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND name = $2'
        tag = await self.bot.db.fetchrow(query, ctx.guild.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`.')

        owner = ctx.guild.get_member(tag['owner_id'])
        if owner is not None:
            raise exceptions.ArgumentError(f'The owner of that tag is still in the server.')

        query = 'UPDATE tags SET owner_id = $1 WHERE server_id = $2 AND name = $3'
        await self.bot.db.execute(query, ctx.author.id, ctx.guild.id, name)

        embed = discord.Embed(colour=discord.Colour.gold(), title='Tag claimed:')
        embed.add_field(name='Previous owner:', value=f'{tag["owner_id"]}', inline=False)
        embed.add_field(name='New owner:', value=f'{ctx.author.mention}', inline=False)
        return await ctx.send(embed=embed)

    @tag.command(name='alias')
    async def tag_alias(self, ctx, alias: converters.TagName, original: converters.TagName):
        """
        Alias a name to a tag.

        `alias`: The alias of the tag you want.
        `name`: The name of the tag to point the alias at.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND alias = $2'
        alias_tag = await self.bot.db.fetchrow(query, ctx.guild.id, alias)
        if alias_tag:
            raise exceptions.ArgumentError(f'There is already a tag alias in this server with the name `{alias}`.')

        query = 'SELECT * FROM tags WHERE server_id = $1 AND name = $2'
        original_tag = await self.bot.db.fetchrow(query, ctx.guild.id, original)
        if not original_tag:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{original}`.')

        query = 'INSERT INTO tags VALUES ($1, $2, $3, $4, $5, $6)'
        await self.bot.db.execute(query, ctx.author.id, ctx.guild.id, alias, None, original, datetime.now())

        embed = discord.Embed(colour=discord.Colour.gold(), title='Tag alias created:')
        embed.add_field(name='Alias:', value=f'{alias}', inline=False)
        embed.add_field(name='Links to:', value=f'{original}', inline=False)
        return await ctx.send(embed=embed)

    @tag.command(name='transfer')
    async def tag_transfer(self, ctx, name: converters.TagName, *, member: discord.Member):
        """
        Transfer a tag to another member.

        `name`: The name of the tag to transfer.
        `member`: The member to transfer the tag too. Can be a name, id or mention.
        """

        if member.bot:
            raise exceptions.ArgumentError('You can not transfer tags to bots.')

        query = 'SELECT * FROM tags WHERE server_id = $1 AND owner_id = $2 and name = $3'
        tag = await self.bot.db.fetchrow(query, ctx.guild.id, ctx.author.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'You do not have any tags in this server with the name `{name}`.')

        query = 'UPDATE tags SET owner_id = $1 WHERE server_id = $2 AND name = $3'
        await self.bot.db.execute(query, member.id, ctx.guild.id, name)

        embed = discord.Embed(colour=discord.Colour.gold(), title='Tag transferred:')
        embed.add_field(name='Previous owner:', value=f'{ctx.author.mention}', inline=False)
        embed.add_field(name='New owner:', value=f'{member.mention}', inline=False)
        return await ctx.send(embed=embed)

    @tag.command(name='delete', aliases=['remove'])
    async def tag_delete(self, ctx, *, name: converters.TagName):
        """
        Deletes a tag.

        `name`: The name of the tag to delete.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND owner_id = $2 AND name = $3'
        tag = await self.bot.db.fetchrow(query, ctx.guild.id, ctx.author.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'You do not have any tags in this server with the name `{name}`.')

        query = 'DELETE FROM tags WHERE server_id = $1 AND owner_id = $2 AND name = $3'
        await self.bot.db.execute(query, ctx.guild.id, ctx.author.id, name)

        query = 'DELETE FROM tags WHERE server_id = $1 AND alias = $2'
        await self.bot.db.execute(query, ctx.guild.id, name)

        embed = discord.Embed(colour=discord.Colour.gold(), title='Tag deleted:')
        embed.add_field(name='Name:', value=f'{name}', inline=False)
        embed.add_field(name='Content:', value=f'{tag["content"]}', inline=False)
        return await ctx.send(embed=embed)

    @tag.command(name='search')
    async def tag_search(self, ctx, *, name: converters.TagName):
        """
        Displays a list of tags that are similar to the search.

        `name`: The search terms to look for tags with.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND name % $2 ORDER BY name <-> $2 LIMIT 100'
        tags = await self.bot.db.fetch(query, ctx.guild.id, name)
        if not tags:
            raise exceptions.ArgumentError(f'There are no tags in this server similar to the term `{name}`.')

        entries = [f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags)]
        return await ctx.paginate_embed(entries=entries, entries_per_page=25, header=f'Tags matching: `{name}`\n\n')

    @tag.command(name='list')
    async def tag_list(self, ctx, *, member: discord.Member = None):
        """
        Get a list of yours or someones else's tags.

        `member`: The member to get a tag list for. Can be a name, id or mention.
        """

        if not member:
            member = ctx.author

        query = 'SELECT * FROM tags WHERE server_id = $1 and owner_id = $2'
        tags = await self.bot.db.fetch(query, ctx.guild.id, member.id)
        if not tags:
            raise exceptions.ArgumentError(f'`{member}` has no tags in this server.')

        entries = [f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags)]
        return await ctx.paginate_embed(entries=entries, entries_per_page=25, title=f'{member}\'s tags')

    @tag.command(name='all')
    async def tag_all(self, ctx):
        """
        Get a list of all tags in this server.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1'
        tags = await self.bot.db.fetch(query, ctx.guild.id)
        if not tags:
            raise exceptions.ArgumentError(f'There are no tags in this server.')

        entries = [f'`{index + 1}.` {tag["name"]}' for index, tag in enumerate(tags)]
        return await ctx.paginate_embed(entries=entries, entries_per_page=25, title=f'{ctx.guild}\'s tags')

    @tag.command(name='info')
    async def tag_info(self, ctx, *, name: converters.TagName):
        """
        Displays information about a tag.

        `name`: The name of the tag to get the information for.
        """

        query = 'SELECT * FROM tags WHERE server_id = $1 AND name = $2'
        tag = await self.bot.db.fetchrow(query, ctx.guild.id, name)
        if not tag:
            raise exceptions.ArgumentError(f'There are no tags in this server with the name `{name}`.')

        owner = ctx.guild.get_member(tag['owner_id'])

        embed = discord.Embed(colour=discord.Colour.gold())
        embed.set_footer(text=f'Created on {datetime.strftime(tag["created_at"], "%A %d %B %Y at %H:%M")}')
        embed.title = f'{tag["name"]}'
        embed.description = f'`Owner:` {owner.mention if owner else "None"}\n`Claimable:` {owner is None}\n' \
                            f'`Alias:` {tag["alias"]}'
        return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Tags(bot))
