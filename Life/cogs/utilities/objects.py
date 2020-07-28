import discord


class DefaultGuildConfig:

    __slots__ = ('prefixes', 'colour')

    def __init__(self):

        self.prefixes = []
        self.colour = discord.Colour.gold()

    def __repr__(self):
        return f'<DefaultGuildConfig prefixes={self.prefixes} colour={self.colour}>'


class GuildConfig:

    __slots__ = ('prefixes', 'colour')

    def __init__(self, data: dict):

        self.prefixes = data.get('prefixes')
        self.colour = int(data.get('colour'), 16)

    def __repr__(self):
        return f'<GuildConfig prefixes={self.prefixes} colour={self.colour}>'
