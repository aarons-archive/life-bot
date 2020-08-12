"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life. If not, see <https://www.gnu.org/licenses/>.
"""

import typing

import discord


class Utils:

    def __init__(self, bot) -> None:
        self.bot = bot

    def format_time(self, seconds: int, friendly: bool = False) -> str:

        minute, second = divmod(seconds, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)

        days, hours, minutes, seconds, = round(day), round(hour), round(minute), round(second)

        if friendly is True:
            formatted = f'{minutes}m {seconds}s'
            if not hours == 0:
                formatted = f'{hours}h {formatted}'
            if not days == 0:
                formatted = f'{days}d {formatted}'
        else:
            formatted = f'{minutes:02d}:{seconds:02d}'
            if not hours == 0:
                formatted = f'{hours:02d}:{formatted}'
            if not days == 0:
                formatted = f'{days:02d}:{formatted}'

        return formatted

    def activities(self, person: discord.Member) -> str:

        if not person.activities:
            return 'N/A'

        message = '\n'
        for activity in person.activities:

            if activity.type == discord.ActivityType.custom:
                message += f'• '
                if activity.emoji:
                    message += f'{activity.emoji} '
                if activity.name:
                    message += f'{activity.name}'
                message += '\n'

            elif activity.type == discord.ActivityType.playing:

                message += f'• Playing **{activity.name}** '
                if not isinstance(activity, discord.Game):
                    if activity.details:
                        message += f'**| {activity.details}** '
                    if activity.state:
                        message += f'**| {activity.state}** '
                    message += '\n'

            elif activity.type == discord.ActivityType.streaming:
                message += f'• Streaming **[{activity.name}]({activity.url})** on **{activity.platform}**\n'

            elif activity.type == discord.ActivityType.watching:
                message += f'• Watching **{activity.name}**\n'

            elif activity.type == discord.ActivityType.listening:

                if isinstance(activity, discord.Spotify):
                    url = f'https://open.spotify.com/track/{activity.track_id}'
                    message += f'• Listening to **[{activity.title}]({url})** by **{", ".join(activity.artists)}** '
                    if activity.album and not activity.album == activity.title:
                        message += f'from the album **{activity.album}** '
                    message += '\n'
                else:
                    message += f'• Listening to **{activity.name}**\n'

        return message

    def badges(self, person: typing.Union[discord.User, discord.Member]) -> str:

        badges = [badge for name, badge in self.bot.badges.items() if dict(person.public_flags)[name] is True]
        if dict(person.public_flags)['verified_bot'] is False and person.bot:
            badges.append('<:bot:738979752244674674>')
        if self.bot.utils.has_nitro(person=person):
            badges.append('<:nitro:738961134958149662>')
        if any([guild.get_member(person.id).premium_since for guild in self.bot.guilds if person in guild.members]):
            badges.append('<:booster_level_4:738961099310760036>')

        return ' '.join(badges) if badges else 'N/A'

    def has_nitro(self, person: typing.Union[discord.User, discord.Member]) -> bool:

        if person.is_avatar_animated():
            return True

        if any([guild.get_member(person.id).premium_since for guild in self.bot.guilds if person in guild.members]):
            return True

        if member := discord.utils.get(self.bot.get_all_members(), id=person.id):
            if activity := discord.utils.get(member.activities, type=discord.ActivityType.custom):
                if activity.emoji and activity.emoji.is_custom_emoji():
                    return True

    def channel_emoji(self, channel: typing.Union[discord.TextChannel, discord.VoiceChannel]) -> str:

        if isinstance(channel, discord.VoiceChannel):
            if channel.overwrites_for(channel.guild.default_role).read_messages is False:
                emoji = self.bot.channel_emojis['voice_locked']
            else:
                emoji = self.bot.channel_emojis['voice']
        else:
            if channel.overwrites_for(channel.guild.default_role).read_messages is False:
                if channel.is_news():
                    emoji = self.bot.channel_emojis['news_locked']
                else:
                    emoji = self.bot.channel_emojis['text_locked']
            else:
                if channel.is_news():
                    emoji = self.bot.channel_emojis['news']
                else:
                    emoji = self.bot.channel_emojis['text']
            if channel.is_nsfw():
                emoji = self.bot.channel_emojis['text_nsfw']

        return emoji
