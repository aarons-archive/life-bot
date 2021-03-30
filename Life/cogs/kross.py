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
from discord.ext import commands

from bot import Life
from utilities import exceptions


class Kross(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.KROSS_GUILD_ID = 491312179476299786
        self.KROSS_USER_ROLE_ID = 548604302768209920
        self.KROSS_POINTS_CHANNEL_ID = 547156691985104896

        self.KROSS_LOG_CHANNEL_ID = 736757690239287416

        self.VALID_HOUSES = ['phoenix', 'leviathan', 'kodama', 'sylph']
        self.VALID_OPERATIONS = ['add', 'subtract', 'minus', 'remove']

        self.HOUSE_MESSAGE_IDS = {
            'kodama': 787893120855310347,
            'phoenix': 787893121580924958,
            'leviathan': 787893122595946507,
            'sylph': 787893124202102834
        }

        self.HOUSE_ROLE_IDS = {
            'kodama': 492112809543335946,
            'phoenix': 492111519182618627,
            'leviathan': 492112319695028235,
            'sylph': 492110784348946433
        }

    @commands.command(name='points', hidden=True)
    async def points(self, ctx, house: str = None, operation: str = None, points: int = None):
        """
        Command to manage house points.

        If all 3 parameters are left blank it will display how many points each house currently has.

        `house`: The house to add points too, can be one of `phoenix`, `leviathan`, `kodama` or `sylph`.
        `operation`: The point operation to perform. Can be `add`, `minus`, `subtract` or `remove`.
        `points`: The amount of points to add or subtract.
         """

        guild = ctx.bot.get_guild(self.KROSS_GUILD_ID)
        if ctx.guild != guild:
            raise commands.CheckFailure(f'You must be in the guild `{guild.name}` to use this command.')

        role = ctx.guild.get_role(self.KROSS_USER_ROLE_ID)
        if role not in ctx.author.roles:
            raise commands.CheckFailure(f'You must have the role `{role.name}` to use this command.')

        if not house and not operation and not points:

            data = await self.bot.db.fetch('SELECT * FROM kross')

            message = '```py\nHouse     | Points\n'
            for entry in sorted(data, key=lambda e: e['points'], reverse=True):
                message += f'{entry["house"].title():10}| {entry["points"]}\n'
            message += '\n```'

            await ctx.send(message)
            return

        if not house or not operation or not points:
            raise exceptions.ArgumentError('You must provide the `house`, `operation` and `points` arguments.')

        house = house.lower()
        operation = operation.lower()

        if house not in self.VALID_HOUSES:
            raise exceptions.ArgumentError(f'`{house}` is not a valid house. Please choose one of {", ".join(f"`{house}`" for house in self.VALID_HOUSES)}.')

        if operation not in self.VALID_OPERATIONS:
            raise exceptions.ArgumentError(f'`{operation}` is not a valid operation. Please choose on of {", ".join(f"`{operation}`" for operation in self.VALID_OPERATIONS)}.')

        current_points = await self.bot.db.fetchrow('SELECT points FROM kross WHERE house = $1', house)
        current_points = current_points['points']

        if operation == 'add':
            new_points = current_points + points
            await self.bot.db.fetch('UPDATE kross SET points = $1 WHERE house = $2', new_points, house)
            await ctx.send(f'Added `{points}` to house `{house}`. They had `{current_points}` points and now they have `{new_points}`.')
        elif operation in ['minus', 'subtract', 'remove']:
            new_points = current_points - points
            await self.bot.db.fetch('UPDATE kross SET points = $1 WHERE house = $2', new_points, house)
            await ctx.send(f'Subtracted `{points}` from house `{house}`. They had `{current_points}` points and now they have `{new_points}`.')

        try:
            channel = ctx.guild.get_channel(self.KROSS_POINTS_CHANNEL_ID)
            points = await self.bot.db.fetchrow('SELECT points FROM kross WHERE house = $1', house)
            message = await channel.fetch_message(self.HOUSE_MESSAGE_IDS[house])
            await message.edit(content=f'{house.title()} has {points["points"]} points.')
        except discord.Forbidden:
            raise exceptions.LifeError('Could not update points.')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):

        if member.guild.id != self.KROSS_GUILD_ID:
            return

        channel = self.bot.get_channel(self.KROSS_LOG_CHANNEL_ID)

        if member.bot is True:
            return await channel.send(f'{member.mention} just joined. They are a bot so they will not be sorted into a house.')

        row = await self.bot.db.fetchrow('SELECT * FROM kross_roles WHERE member_id = $1', member.id)

        if row:

            guild_role_ids = [role.id for role in member.guild.roles]
            roles = [member.guild.get_role(role_id) for role_id in row['role_ids'] if role_id in guild_role_ids]
            if not roles:
                return await channel.send(f'{member.mention} just joined. They had roles before they left but none of them are available now.')

            try:
                await member.add_roles(*roles)
                await channel.send(f'{member.mention} just joined and was given `{len(roles)}` role(s) back.')
                return await self.bot.db.execute('DELETE FROM kross_roles WHERE member_id = $1', member.id)
            except discord.Forbidden:
                return await channel.send(f'{member.mention} just joined. I do not have permissions to give them roles.')

        roles = sorted(
                {
                    'phoenix': member.guild.get_role(self.HOUSE_ROLE_IDS['phoenix']),
                    'leviathan': member.guild.get_role(self.HOUSE_ROLE_IDS['leviathan']),
                    'sylph': member.guild.get_role(self.HOUSE_ROLE_IDS['sylph']),
                    'kodama': member.guild.get_role(self.HOUSE_ROLE_IDS['kodama'])}.items(),
                key=lambda role: len(role[1].members)
        )

        try:
            await member.add_roles(roles[0][1])
            return await channel.send(f'{member.mention} just joined and was sorted into the `{roles[0][0].title()}` house.')
        except discord.Forbidden:
            return channel.send(f'{member.mention} just joined. I do not have permissions to give them roles but they should be in the `{roles[0][0].upper()}` house.')

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):

        if member.guild.id != self.KROSS_GUILD_ID:
            return

        channel = self.bot.get_channel(self.KROSS_LOG_CHANNEL_ID)

        if member.bot is True:
            return await channel.send(f'`{member}` just left. They are bot so i will not save their roles.')

        role_ids = [role.id for role in member.roles if role.position != 0]
        if not role_ids:
            return await channel.send(f'`{member}` just left. They did not have any roles.')

        await self.bot.db.execute('INSERT INTO kross_roles values ($1, $2)', member.id, role_ids)
        return await channel.send(f'`{member}` just left. I have saved their roles and if they rejoin i will give them back.')


def setup(bot: Life):
    bot.add_cog(Kross(bot))
