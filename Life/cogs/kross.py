from discord.ext import commands
import discord

from cogs.utilities import checks


class Kross(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.valid_houses = ["phoenix", "leviathan", "kodama", "sylph"]
        self.valid_operations = ["add", "subtract", "minus"]

        self.house_message_ids = {
            "kodama": 662048639149146122,
            "phoenix": 662048640336134174,
            "leviathan": 662048641703477248,
            "sylph": 662048642856910848
        }

    @commands.Cog.listener()
    async def on_member_join(self, member):

        if member.guild.id != 491312179476299786 or member.bot is True:
            return

        kodama = discord.utils.get(member.guild.roles, name="Kodama")
        sylph = discord.utils.get(member.guild.oles, name="Sylph")
        leviathan = discord.utils.get(member.guild.roles, name="Leviathan")
        phoenix = discord.utils.get(member.guild.roles, name="Phoenix")
        kodama_count = len(kodama.members)
        sylph_count = len(sylph.members)
        leviathan_count = len(leviathan.members)
        phoenix_count = len(phoenix.members)

        try:
            if phoenix_count < kodama_count and phoenix_count < leviathan_count and phoenix_count < sylph_count:
                await member.add_roles(phoenix)
            elif kodama_count < leviathan_count and kodama_count < sylph_count and kodama_count < phoenix_count:
                await member.add_roles(kodama)
            elif leviathan_count < sylph_count and leviathan_count < phoenix_count and leviathan_count < kodama_count:
                await member.add_roles(leviathan)
            elif sylph_count < phoenix_count and sylph_count < kodama_count and sylph_count < leviathan_count:
                await member.add_roles(sylph)
            else:
                await member.add_roles(phoenix)

        except discord.Forbidden:
            return

    @checks.is_krossbot_user()
    @checks.is_kross_guild()
    @commands.command(name="roles")
    async def roles(self, ctx):
        """
        Display how many members there are in each house.
        """

        bots = sum([1 for member in ctx.guild.members if member.bot])
        heathens = len(discord.utils.get(ctx.guild.roles, name="Heathen").members)
        phoenixs = len(discord.utils.get(ctx.guild.roles, name="Phoenix").members)
        leviathans = len(discord.utils.get(ctx.guild.roles, name="Leviathan").members)
        kodamas = len(discord.utils.get(ctx.guild.roles, name="Kodama").members)
        sylphs = len(discord.utils.get(ctx.guild.roles, name="Sylph").members)
        banshees = len(discord.utils.get(ctx.guild.roles, name="Banshee").members)
        lost_souls = len(discord.utils.get(ctx.guild.roles, name="The Lost Souls").members)

        role_counts = {"Bots": bots, "Heathens": heathens, "Phoenixs": phoenixs, "Leviathans": leviathans,
                       "Kodamas": kodamas, "Sylphs": sylphs, "Banshees": banshees, "Lost souls": lost_souls}

        message = f"```py\nRole       | Count\n"
        for role, count in sorted(role_counts.items(), reverse=True, key=lambda item: item[1]):
            message += f"{role:11}| {count}\n"
        message += "\n```"

        return await ctx.send(message)

    @checks.is_krossbot_user()
    @checks.is_kross_guild()
    @commands.group(name="points")
    async def points(self, ctx, house: str = None, operation: str = None, points: int = None):
        """
        Command to manage house points.

        If all 3 parameters are left black it will display how many points each house currently has.

        `house`: The house to add points too, can be one of `phoenix`, `leviathan`, `kodama` or `sylph`.
        `operation`: The point operation to perform. Can be `add`, `minus` or `subtract`.
        `points`: The amount of points to add or subtract.
         """

        if not house and not operation and not points:

            data = await self.bot.db.fetch("SELECT * FROM kross")

            message = "```py\nHouse     | Points\n"
            for entry in sorted(data, key=lambda e: e["points"], reverse=True):
                message += f"{entry['house'].title():10}| {entry['points']}\n"
            message += "\n```"

            return await ctx.send(message)

        if not house or not operation or not points:
            return await ctx.send("You must provide the `house`, `operation` and `points` arguments.")

        if house.lower() not in self.valid_houses:
            return await ctx.send(f"`{house.lower()}` is not a valid house. Please choose one of `phoenix`, `leviathan`, `kodama` or `sylph`.")

        if operation.lower() not in self.valid_operations:
            return await ctx.send(f"`{operation.lower()}` is not a valid operation. Please choose either `add` `subtract` or `minus`.")

        current_points = await self.bot.db.fetchrow("SELECT points FROM kross WHERE house = $1", house)
        current_points = current_points["points"]

        if operation == "add":
            new_points = current_points + points
            await self.bot.db.fetch("UPDATE kross SET points = $1 WHERE house = $2", new_points, house)
            await ctx.send(f"Added `{points}` to house `{house}`. They had `{current_points}` points and now they have `{new_points}`.")
        elif operation == "minus" or operation == "subtract":
            new_points = current_points - points
            await self.bot.db.fetch("UPDATE kross SET points = $1 WHERE house = $2", new_points, house)
            await ctx.send(f"Subtracted `{points}` from house `{house}`. They had `{current_points}` points and now they have `{new_points}`.")
        else:
            return await ctx.send("Something went wrong. Please ping my owner.")

        try:
            channel = ctx.guild.get_channel(547156691985104896)
            points = await self.bot.db.fetchrow("SELECT points FROM kross WHERE house = $1", house)
            message = await channel.fetch_message(self.house_message_ids[house])
            return await message.edit(content=f"{house.title()} has {points['points']} points.")

        except discord.Forbidden:
            return await ctx.send("Could not update points, you used the wrong the bot prefix.")


def setup(bot):
    bot.add_cog(Kross(bot))
