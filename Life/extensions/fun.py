import asyncio
import collections
import random
from typing import Optional

import discord
from discord.ext import commands, tasks

from core import colours, emojis
from core.bot import Life
from utilities import context, exceptions, utils


MAGIC_8_BALL_RESPONSES = [
    "Yeah!",
    "Hell yeah!!",
    "I think so?",
    "Maybe, not sure",
    "Totally",
    "Of course",
    "Yes",
    "Perhaps...",
    "If you believe in yourself, you can surely do it.",
    "Nah",
    "Nope",
    "Definitely not",
    "WHAT, are you insane???",
    "Sorry I had you muted, can you ask me again?",
    "I didn’t quite catch that, can you repeat?"
]

RATES = [
    "-100, i don't ever want to hear their name again :nauseated_face: :nauseated_face:",
    "-10 :nauseated_face:",
    "0, who even is that?? never heard of them...",
    "1",
    "2",
    "3",
    "4, they're ok, i guess :rolling_eyes:",
    "5, im on the fence about this one.",
    "6",
    "7 :cold_face:",
    "8 :star_struck:",
    "9 :hot_face:",
    "10 :fire:",
    "100 :star_struck: :heart_eyes:",
    "1000 :fire: :heart_eyes: :heart_on_fire: :heart_on_fire:"
]


def setup(bot: Life) -> None:
    bot.add_cog(Fun(bot=bot))


class Fun(commands.Cog):

    def __init__(self, bot: Life) -> None:
        self.bot = bot

        self.MAGIC_8_BALL_PREDICTIONS = {}
        self.RATES = {}
        self.IQ_RATES = {}
        self.GAY_RATES = {}

        self.clear_states.start()

    # Clear states task

    @tasks.loop(minutes=5)
    async def clear_states(self) -> None:

        self.MAGIC_8_BALL_PREDICTIONS.clear()
        self.RATES.clear()
        self.IQ_RATES.clear()
        self.GAY_RATES.clear()

    @clear_states.before_loop
    async def before_clear_states(self) -> None:
        await self.bot.wait_until_ready()

    def cog_unload(self) -> None:
        self.clear_states.cancel()

    # Commands

    @commands.command(name='rps')
    async def rps(self, ctx: context.Context) -> None:
        """
        Play rock, paper, scissors with the bot.
        """

        CHOICES = ['\U0001faa8', '\U0001f4f0', '\U00002702']
        MY_CHOICE = random.choice(CHOICES)

        ROCK = "\U0001faa8"
        PAPER = "\U0001f4f0"
        SCISSORS = "\U00002702"

        LOSE = "You won! GG"
        WIN = "I won! GG"
        DRAW = "We both picked the same, It's a draw!"

        message = await ctx.reply("Let's see who wins!")
        for choice in CHOICES:
            await message.add_reaction(choice)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", check=lambda r, u: r.message.id == message.id and u.id == ctx.author.id and r.emoji in CHOICES, timeout=45.0, )
        except asyncio.TimeoutError:
            raise exceptions.EmbedError(emoji=emojis.CROSS, colour=colours.RED, description="You took too long to respond!")

        if (player_choice := reaction.emoji) == ROCK:
            if player_choice == MY_CHOICE:
                await message.edit(content=DRAW)
            elif MY_CHOICE == PAPER:
                await message.edit(content=WIN)
            elif MY_CHOICE == SCISSORS:
                await message.edit(content=LOSE)

        elif (player_choice := reaction.emoji) == PAPER:
            if player_choice == MY_CHOICE:
                await message.edit(content=DRAW)
            elif MY_CHOICE == SCISSORS:
                await message.edit(content=WIN)
            elif MY_CHOICE == ROCK:
                await message.edit(content=LOSE)

        elif (player_choice := reaction.emoji) == SCISSORS:
            if player_choice == MY_CHOICE:
                await message.edit(content=DRAW)
            elif MY_CHOICE == ROCK:
                await message.edit(content=WIN)
            elif MY_CHOICE == PAPER:
                await message.edit(content=LOSE)

    @commands.command(name="8ball")
    async def magic_8_ball(self, ctx: context.Context, *, question: str = utils.MISSING) -> None:
        """
        Ask the magic 8 ball a question.

        **question**: The question to ask the 8 ball.
        """

        if not question:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.UNKNOWN, description="c'mon kid, you have to ask me something, how can I predict something from nothing?")

        question = "".join(str(question).split("\n"))

        if self.MAGIC_8_BALL_PREDICTIONS.get(question) is None:
            self.MAGIC_8_BALL_PREDICTIONS[question] = random.choice(MAGIC_8_BALL_RESPONSES)

        await ctx.reply(self.MAGIC_8_BALL_PREDICTIONS[question])

    @commands.command(name="rate")
    async def rate(self, ctx: context.Context, *, person: discord.User = utils.MISSING) -> None:
        """
        Let the bot rate you, or someone else...

        **person**: The person to rate, can be their ID, Username, @Mention or Nickname.
        """

        user = person or ctx.author

        if self.RATES.get(user.id) is None:
            self.RATES[user.id] = random.choice(RATES)

        await ctx.reply(f"hmm...i rate {user.mention} a {self.RATES[user.id]}", allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="gayrate", aliases=["gay-rate", "gay_rate"])
    async def gay_rate(self, ctx: context.Context, *, person: discord.User = utils.MISSING) -> None:
        """
        The bot will judge how gay you are...
        """

        user = person or ctx.author

        if self.GAY_RATES.get(user.id) is None:
            self.GAY_RATES[user.id] = random.randint(1, 100)

        await ctx.reply(f"{user.mention} is **{self.GAY_RATES[user.id]}%** gay :rainbow:", allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="iqrate", aliases=["iq-rate", "iq_rate"])
    async def iq_rate(self, ctx: context.Context, *, person: discord.User = utils.MISSING) -> None:
        """
        Let the bot shame your IQ in front of everyone.
        """

        user = person or ctx.author

        if self.IQ_RATES.get(user.id) is None:
            self.IQ_RATES[user.id] = random.randint(20, 200)

        await ctx.reply(f"{user.mention}'s IQ is **{self.IQ_RATES[user.id]}** :nerd:", allowed_mentions=discord.AllowedMentions.none())

    @commands.command(name="choose", aliases=["choice"])
    async def choose(self, ctx: context.Context, *choices: commands.clean_content) -> None:
        """
        Chooses something from a list of choices.

        **choices**: A list of choices to choose from. These should be separated using just quotes. For example **l-choose "Do coding" "Do gaming"**
        """

        if len(choices) <= 1:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="Not enough choices to choose from.")

        await ctx.reply(random.choice(list(map(str, choices))))

    @commands.command(name="choosebestof", aliases=["cbo", "bestof"])
    async def choosebestof(self, ctx: context.Context, times: Optional[int], *choices: commands.clean_content) -> None:
        """
        Chooses the best option from a list of choices.

        **times**: An amount of times to calculate choices with, more times will equal more "accurate" results.
        **choices**: A list of choices to choose from. These should be separated using just quotes. For example **l-bestof 99999 "Do coding" "Do gaming"**.
        """

        if len(choices) <= 1:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="Not enough choices to choose from.")
        if times and times > 999999999:
            raise exceptions.EmbedError(colour=colours.RED, emoji=emojis.CROSS, description="That a bit too many times...")

        times = min(10001, max(1, (len(choices) ** 3) + 1 if not times else times))
        counter = collections.Counter(random.choice(list(map(str, choices))) for _ in range(times))

        await ctx.paginate(
                entries=[f"║ {item[:28] + (item[28:] and '..'):30} ║ {f'{count / times:.2%}':<10} ║" for item, count in counter.most_common()],
                per_page=10,
                header="╔════════════════════════════════╦════════════╗\n"
                       "║ Choice                         ║ Percentage ║\n"
                       "╠════════════════════════════════╬════════════╣\n",
                footer="\n"
                       "╚════════════════════════════════╩════════════╝",
                codeblock=True,
        )
