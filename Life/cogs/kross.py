from discord.ext import commands
import discord


class Kross(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):

        if ctx.guild.id == 491312179476299786:
            return True
        else:
            raise commands.CheckFailure("This command can only be used in a certain guild.")

    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild = member.guild

        if not guild.id == 491312179476299786:
            return
        if member.bot:
            return

        kodama = discord.utils.get(guild.roles, name="Kodama")
        sylph = discord.utils.get(guild.roles, name="Sylph")
        leviathan = discord.utils.get(guild.roles, name="Leviathan")
        phoenix = discord.utils.get(guild.roles, name="Phoenix")
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
            elif sylph_count < phoenix_count and sylph_count < kodama and sylph_count < leviathan_count:
                await member.add_roles(sylph)
            else:
                await member.add_roles(phoenix)
        except discord.Forbidden:
            return

    @commands.command(name="roles", hidden=True)
    async def roles(self, ctx):
        """
        Get how many members are in each role.
        """

        bots = sum([1 for member in ctx.guild.members if member.bot])
        heathens = len(discord.utils.get(ctx.guild.roles, name="Heathen").members)
        phoenixs = len(discord.utils.get(ctx.guild.roles, name="Phoenix").members)
        leviathans = len(discord.utils.get(ctx.guild.roles, name="Leviathan").members)
        kodamas = len(discord.utils.get(ctx.guild.roles, name="Kodama").members)
        sylphs = len(discord.utils.get(ctx.guild.roles, name="Sylph").members)
        banshees = len(discord.utils.get(ctx.guild.roles, name="Banshee").members)
        lost_souls = len(discord.utils.get(ctx.guild.roles, name="The Lost Souls").members)
        total = phoenixs + leviathans + kodamas + sylphs + banshees + lost_souls

        message = f"```py\n" \
                  f"Role       |Count\n" \
                  f"Heathens   |{heathens}\n" \
                  f"Phoenix    |{phoenixs}\n" \
                  f"Leviathan  |{leviathans}\n" \
                  f"Kodama     |{kodamas}\n" \
                  f"Sylph      |{sylphs}\n" \
                  f"Banshees   |{banshees}\n" \
                  f"Lost Souls |{lost_souls}\n" \
                  f"Bots       |{bots}\n" \
                  f"Total      |{total}\n" \
                  f"```"
        return await ctx.send(message)

    @commands.group(name="points", hidden=True, invoke_without_command=True)
    @commands.has_role(548604302768209920)
    async def points(self, ctx):
        """
        Displays a list of how many points each house has.
        """

        def key(house):
            return house["points"]

        data = await self.bot.db.fetch("SELECT * FROM kross")

        message = "```py\n" \
                  "House     |Points\n"
        for entry in sorted(data, key=key, reverse=True):
            message += f"{entry['house'].title():10}|{entry['points']}\n"
        message += "\n```"

        return await ctx.send(message)

    @points.group(name="leviathan", invoke_without_command=True)
    async def points_leviathan(self, ctx):
        """
        Points commands for Leviathan.
        """

        return await ctx.send("Please specify an operation, `add` or `remove`.")

    @points_leviathan.command(name="add")
    async def points_leviathan_add(self, ctx, points: int):
        """
        Add points to the Leviathan house.

        `points`: The amount of points to add.
        """

        data = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "leviathan")
        total_points = data["points"] + points
        await self.bot.db.execute(f"UPDATE kross SET points = $1 WHERE house = $2", total_points, "leviathan")
        await ctx.send(f"Added `{points}` points to the Leviathan house. They now have `{total_points}` points.")
        return await self.refresh_points(ctx)

    @points_leviathan.command(name="remove", aliases=["subtract", "minus"])
    async def points_leviathan_remove(self, ctx, points: int):
        """
        Remove points from the Leviathan house.

        `points`: The amount of points to remove.
        """

        data = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "leviathan")
        total_points = data["points"] - points
        await self.bot.db.execute(f"UPDATE kross SET points = $1 WHERE house = $2", total_points, "leviathan")
        await ctx.send(f"Removed `{points}` points from house Leviathan. They now have `{total_points}` points.")
        return await self.refresh_points(ctx)

    @points.group(name="phoenix", invoke_without_command=True)
    async def points_phoenix(self, ctx):
        """
        Points commands for Phoenix.
        """

        return await ctx.send("Please specify an operation, `add` or `remove`.")

    @points_phoenix.command(name="add")
    async def points_phoenix_add(self, ctx, points: int):
        """
        Add points to the Phoenix house.

        `points`: The amount of points to add.
        """

        data = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "phoenix")
        total_points = data["points"] + points
        await self.bot.db.execute(f"UPDATE kross SET points = $1 WHERE house = $2", total_points, "phoenix")
        await ctx.send(f"Added `{points}` points to Phoenix house. They now have `{total_points}` points.")
        return await self.refresh_points(ctx)

    @points_phoenix.command(name="remove", aliases=["subtract", "minus"])
    async def points_phoenix_remove(self, ctx, points: int):
        """
        Remove points from the Phoenix house.

        `points`: The amount of points to remove.
        """

        data = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "phoenix")
        total_points = data["points"] - points
        await self.bot.db.execute(f"UPDATE kross SET points = $1 WHERE house = $2", total_points, "phoenix")
        await ctx.send(f"Removed `{points}` points from house Phoenix. They now have `{total_points}` points.")
        return await self.refresh_points(ctx)

    @points.group(name="kodama", invoke_without_command=True)
    async def points_kodama(self, ctx):
        """
        Points commands for Kodama.
        """

        return await ctx.send("Please specify an operation, `add` or `remove`.")

    @points_kodama.command(name="add")
    async def points_kodama_add(self, ctx, points: int):
        """
        Add points to the Kodama house.

        `points`: The amount of points to add.
        """

        data = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "kodama")
        total_points = data["points"] + points
        await self.bot.db.execute(f"UPDATE kross SET points = $1 WHERE house = $2", total_points, "kodama")
        await ctx.send(f"Added `{points}` points to Kodama house. They now have `{total_points}` points.")
        return await self.refresh_points(ctx)

    @points_kodama.command(name="remove", aliases=["subtract", "minus"])
    async def points_kodama_remove(self, ctx, points: int):
        """
        Remove points from the Kodama house.

        `points`: The amount of points to remove.
        """

        data = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "kodama")
        total_points = data["points"] - points
        await self.bot.db.execute(f"UPDATE kross SET points = $1 WHERE house = $2", total_points, "kodama")
        await ctx.send(f"Removed `{points}` points from house Kodama. They now have `{total_points}` points.")
        return await self.refresh_points(ctx)

    @points.group(name="sylph", invoke_without_command=True)
    async def points_sylph(self, ctx):
        """
        Points commands for Sylph.
        """

        return await ctx.send("Please specify an operation, `add` or `remove`.")

    @points_sylph.command(name="add")
    async def points_sylph_add(self, ctx, points: int):
        """
        Add points to the Sylph house.

        `points`: The amount of points to add.
        """

        data = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "sylph")
        total_points = data["points"] + points
        await self.bot.db.execute(f"UPDATE kross SET points = $1 WHERE house = $2", total_points, "sylph")
        await ctx.send(f"Added `{points}` points to house Sylph. They now have `{total_points}` points.")
        return await self.refresh_points(ctx)

    @points_sylph.command(name="remove", aliases=["subtract", "minus"])
    async def points_sylph_remove(self, ctx, points: int):
        """
        Remove points from the Sylph house.

        `points`: The amount of points to remove.
        """

        data = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "sylph")
        total_points = data["points"] - points
        await self.bot.db.execute(f"UPDATE kross SET points = $1 WHERE house = $2", total_points, "sylph")
        await ctx.send(f"Removed `{points}` points from house Sylph. They now have `{total_points}` points.")
        return await self.refresh_points(ctx)

    async def refresh_points(self, ctx):

        channel = self.bot.get_channel(547156691985104896)

        try:
            phoenix = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "phoenix")
            kodama = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "kodama")
            leviathan = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "leviathan")
            sylph = await self.bot.db.fetchrow("SELECT * FROM kross WHERE house = $1", "sylph")

            kodama_message = await channel.fetch_message(662048639149146122)
            phoenix_message = await channel.fetch_message(662048640336134174)
            leviathan_message = await channel.fetch_message(662048641703477248)
            sylph_message = await channel.fetch_message(662048642856910848)
            await phoenix_message.edit(content=f"Phoenix has {phoenix['points']} points.")
            await kodama_message.edit(content=f"Kodama has {kodama['points']} points.")
            await leviathan_message.edit(content=f"Leviathan has {leviathan['points']} points.")
            await sylph_message.edit(content=f"Sylph has {sylph['points']} points.")

        except discord.Forbidden:
            return await ctx.send("Could not update points, you used the wrong the bot prefix.")


def setup(bot):
    bot.add_cog(Kross(bot))
