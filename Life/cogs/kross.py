from discord.ext import commands
import discord


class KrossServer(commands.Cog):
    """
    Custom server commands.
    """

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

        if guild.id != 491312179476299786:
            return
        if member.bot is True:
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
            if kodama_count < phoenix_count and kodama_count < leviathan_count and kodama_count < sylph_count:
                await member.add_roles(kodama)
            elif phoenix_count < kodama_count and phoenix_count < leviathan_count and phoenix_count < sylph_count:
                await member.add_roles(phoenix)
            elif leviathan_count < phoenix_count and leviathan_count < kodama_count and leviathan_count < sylph_count:
                await member.add_roles(leviathan)
            elif sylph_count < phoenix_count and sylph_count < leviathan_count and sylph_count < kodama_count:
                await member.add_roles(sylph)
            else:
                await member.add_roles(phoenix)
        except discord.Forbidden:
            return

    @commands.command(name="houses", aliases=["h"], hidden=True)
    async def houses(self, ctx):
        """
        Get how many members are in each house.

        This only works in a specific server.
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

        # Create and send the message.
        message = f"```py\n" \
                  f"Heathens: {' ' * int((11 - 9))} {heathens}\n" \
                  f"Phoenix: {' ' * int((11 - 8))} {phoenixs}\n" \
                  f"Leviathan: {' ' * int((11 - 10))} {leviathans}\n" \
                  f"Kodama: {' ' * int((11 - 7))} {kodamas}\n" \
                  f"Sylph: {' ' * int((11 - 6))} {sylphs}\n" \
                  f"Banshees: {' ' * int((11 - 9))} {banshees}\n" \
                  f"Lost Souls: {' ' * int((11 - 11))} {lost_souls}\n" \
                  f"Bots: {' ' * int((11 - 5))} {bots}\n" \
                  f"Total: {' ' * int((11 - 6))} {total}\n" \
                  f"```"
        return await ctx.send(message)

    @commands.group(name="points", aliases=["p"], hidden=True, invoke_without_command=True)
    @commands.has_role(548604302768209920)
    async def points(self, ctx):
        """
        Displays a list of how many points each house has.
        """

        def key(house):
            return house["points"]

        data = await self.bot.db.fetch("SELECT * FROM kross")

        message = "```py\n"

        for entry in sorted(data, key=key, reverse=True):
            message += f"{entry['house'].title()}: {' ' * int((11 - len(entry['house'])))} {entry['points']}\n"

        message += "\n```"
        return await ctx.send(message)

    @points.group(name="leviathan", invoke_without_command=True)
    async def points_leviathan(self, ctx):
        """
        Points commands for leviathan.
        """
        return await ctx.send("Please specify an operation, `add` or `minus`.")

    @points_leviathan.command(name="add")
    async def points_leviathan_add(self, ctx, points: int):
        data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "leviathan")
        points_new = data["points"] + points
        await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", points_new, "leviathan")
        await ctx.send(f"Added `{points}` points to house Leviathan. They now have `{points_new}` points!")
        return await self.refresh_points(ctx)

    @points_leviathan.command(name="minus", aliases=["subtract", "remove"])
    async def points_leviathan_minus(self, ctx, points: int):
        data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "leviathan")
        points_new = data["points"] - points
        await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", points_new, "leviathan")
        await ctx.send(f"Removed `{points}` points from house Leviathan. They now have `{points_new}` points!")
        return await self.refresh_points(ctx)

    @points.group(name="phoenix", invoke_without_command=True)
    async def points_phoenix(self, ctx):
        """
        Points commands for phoenix.
        """
        return await ctx.send("Please specify an operation, `add` or `minus`.")

    @points_phoenix.command(name="add")
    async def points_phoenix_add(self, ctx, points: int):
        data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "phoenix")
        points_new = data["points"] + points
        await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", points_new, "phoenix")
        await ctx.send(f"Added `{points}` points to house Phoenix. They now have `{points_new}` points!")
        return await self.refresh_points(ctx)

    @points_phoenix.command(name="minus", aliases=["subtract", "remove"])
    async def points_phoenix_minus(self, ctx, points: int):
        data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "phoenix")
        points_new = data["points"] - points
        await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", points_new, "phoenix")
        await ctx.send(f"Removed `{points}` points from house Phoenix. They now have `{points_new}` points!")
        return await self.refresh_points(ctx)

    @points.group(name="kodama", invoke_without_command=True)
    async def points_kodama(self, ctx):
        """
        Points commands for kodama.
        """
        return await ctx.send("Please specify an operation, `add` or `minus`.")

    @points_kodama.command(name="add")
    async def points_kodama_add(self, ctx, points: int):
        data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "kodama")
        points_new = data["points"] + points
        await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", points_new, "kodama")
        await ctx.send(f"Added `{points}` points to house Kodama. They now have `{points_new}` points!")
        return await self.refresh_points(ctx)

    @points_kodama.command(name="minus", aliases=["subtract", "remove"])
    async def points_kodama_minus(self, ctx, points: int):
        data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "kodama")
        points_new = data["points"] - points
        await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", points_new, "kodama")
        await ctx.send(f"Removed `{points}` points from house Kodama. They now have `{points_new}` points!")
        return await self.refresh_points(ctx)

    @points.group(name="sylph", invoke_without_command=True)
    async def points_sylph(self, ctx):
        """
        Points commands for sylph.
        """
        return await ctx.send("Please specify an operation, `add` or `minus`.")

    @points_sylph.command(name="add")
    async def points_sylph_add(self, ctx, points: int):
        data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "sylph")
        points_new = data["points"] + points
        await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", points_new, "sylph")
        await ctx.send(f"Added `{points}` points to house Sylph. They now have `{points_new}` points!")
        return await self.refresh_points(ctx)

    @points_sylph.command(name="minus", aliases=["subtract", "remove"])
    async def points_sylph_minus(self, ctx, points: int):
        data = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "sylph")
        points_new = data["points"] - points
        await self.bot.db.execute(f"UPDATE kross_config SET points = $1 WHERE key = $2", points_new, "sylph")
        await ctx.send(f"Removed `{points}` points from house Sylph. They now have `{points_new}` points!")
        return await self.refresh_points(ctx)

    async def refresh_points(self, ctx):
        channel = self.bot.get_channel(547156691985104896)
        try:
            kodama = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "kodama")
            phoenix = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "phoenix")
            leviathan = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "leviathan")
            sylph = await self.bot.db.fetchrow("SELECT * FROM kross_config WHERE key = $1", "sylph")
            km = await channel.fetch_message(629030441420324874)
            await km.edit(content=f"Kodama has {kodama['points']} points!")
            pm = await channel.fetch_message(629030441789423616)
            await pm.edit(content=f"Phoenix has {phoenix['points']} points!")
            lm = await channel.fetch_message(629030442204659722)
            await lm.edit(content=f"Leviathan has {leviathan['points']} points!")
            sm = await channel.fetch_message(629030466569109514)
            await sm.edit(content=f"Sylph has {sylph['points']} points!")
            await ctx.send(f"Refreshed the points leaderboard in {channel.mention}")
        except discord.Forbidden:
            return await ctx.send("Wrong bot.")


def setup(bot):
    bot.add_cog(KrossServer(bot))
