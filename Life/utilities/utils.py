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

import datetime as dt
import typing

import discord
import humanize
import pendulum
import pendulum.exceptions


class Utils:

    def __init__(self, bot) -> None:
        self.bot = bot

        self.channel_emojis = {
            'text': '<:text:739399497200697465>',
            'text_locked': '<:text_locked:739399496953364511>',
            'text_nsfw': '<:text_nsfw:739399497251160115>',
            'news': '<:news:739399496936718337>',
            'news_locked': '<:news_locked:739399497062416435>',
            'voice': '<:voice:739399497221931058>',
            'voice_locked': '<:voice_locked:739399496924135476>',
            'category': '<:category:738960756233601097>'
        }

        self.badge_emojis = {
            'staff': '<:staff:738961032109752441>',
            'partner': '<:partner:738961058613559398>',
            'hypesquad': '<:hypesquad:738960840375664691>',
            'bug_hunter': '<:bug_hunter:738961014275571723>',
            'bug_hunter_level_2': '<:bug_hunter_level_2:739390267949580290>',
            'hypesquad_bravery': '<:hypesquad_bravery:738960831596855448>',
            'hypesquad_brilliance': '<:hypesquad_brilliance:738960824327995483>',
            'hypesquad_balance': '<:hypesquad_balance:738960813460684871>',
            'early_supporter': '<:early_supporter:738961113219203102>',
            'system': '<:system_1:738960703284576378><:system_2:738960703288770650>',
            'verified_bot': '<:verified_bot_1:738960728022581258><:verified_bot_2:738960728102273084>',
            'verified_bot_developer': '<:verified_bot_developer:738961212250914897>',
        }

        self.features = {
            'VERIFIED': 'Is verified server',
            'PARTNERED': 'Is partnered server',
            'MORE_EMOJI': 'Can have 50+ emoji',
            'DISCOVERABLE': 'Is discoverable',
            'FEATURABLE': 'Is featurable',
            'PUBLIC': 'Is public',
            'VIP_REGIONS': 'Can have VIP voice regions',
            'VANITY_URL': 'Can have vanity invite',
            'INVITE_SPLASH': 'Can have invite splash',
            'COMMERCE': 'Can have store channels',
            'NEWS': 'Can have news channels',
            'BANNER': 'Can have banner',
            'ANIMATED_ICON': 'Can have animated icon',
            'PUBLIC_DISABLED': 'Can not be public',
            'WELCOME_SCREEN_ENABLED': 'Can have welcome screen',
            'MEMBER_VERIFICATION_GATE_ENABLED': 'Has member verify gate'
        }

        self.mfa_levels = {
            0: 'Not required',
            1: 'Required'
        }

        self.colours = {
            discord.Status.online: 0x008000,
            discord.Status.idle: 0xFF8000,
            discord.Status.dnd: 0xFF0000,
            discord.Status.offline: 0x808080,
            discord.Status.invisible: 0x808080,
        }

        self.verification_levels = {
            discord.VerificationLevel.none: 'None - No criteria set.',
            discord.VerificationLevel.low: 'Low - Must have a verified email.',
            discord.VerificationLevel.medium: 'Medium - Must have a verified email and be registered on discord for more than 5 minutes.',
            discord.VerificationLevel.high: 'High - Must have a verified email, be registered on discord for more than 5 minutes and be a member of the guild for more '
                                            'then 10 minutes.',
            discord.VerificationLevel.extreme: 'Extreme - Must have a verified email, be registered on discord for more than 5 minutes, be a member of the guild for '
                                               'more then 10 minutes and a have a verified phone number.'
        }

        self.content_filter_levels = {
            discord.ContentFilter.disabled: 'None',
            discord.ContentFilter.no_role: 'No roles',
            discord.ContentFilter.all_members: 'All members',
        }

    def format_seconds(self, *, seconds: int, friendly: bool = False) -> str:

        minute, second = divmod(seconds, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)

        days, hours, minutes, seconds = round(day), round(hour), round(minute), round(second)

        if friendly is True:
            return f'{f"{days}d " if not days == 0 else ""}{f"{hours}h " if not hours == 0 or not days == 0 else ""}{minutes}m {seconds}s'

        return f'{f"{days:02d}:" if not days == 0 else ""}{f"{hours:02d}:" if not hours == 0 or not days == 0 else ""}{minutes:02d}:{seconds:02d}'

    def convert_datetime(self, *, datetime: typing.Union[pendulum.datetime, dt.datetime]) -> pendulum.datetime:

        if isinstance(datetime, dt.datetime):
            datetime = pendulum.instance(datetime)

        return datetime

    def format_datetime(self, *, datetime: typing.Union[pendulum.datetime, dt.datetime], seconds: bool = False) -> str:

        datetime = self.convert_datetime(datetime=datetime)
        return datetime.format(f'dddd Do [of] MMMM YYYY [at] HH:mm{":ss" if seconds else ""} A (zz{"ZZ" if datetime.timezone == "UTC" else ""})')

    def format_difference(self, *, datetime: typing.Union[pendulum.datetime, dt.datetime], suppress: typing.List[str] = None) -> str:

        if suppress is None:
            suppress = ['seconds']

        return humanize.precisedelta(pendulum.now(tz='UTC').diff(self.convert_datetime(datetime=datetime)), format='%0.0f', suppress=suppress)

    def badges(self, *, person: typing.Union[discord.User, discord.Member]) -> str:

        badges = [badge for name, badge in self.badge_emojis.items() if dict(person.public_flags)[name] is True]
        if dict(person.public_flags)['verified_bot'] is False and person.bot:
            badges.append('<:bot:738979752244674674>')

        if any([guild.get_member(person.id).premium_since for guild in self.bot.guilds if person in guild.members]):
            badges.append('<:booster_level_4:738961099310760036>')

        if person.is_avatar_animated() or any([guild.get_member(person.id).premium_since for guild in self.bot.guilds if person in guild.members]):
            badges.append('<:nitro:738961134958149662>')

        elif member := discord.utils.get(self.bot.get_all_members(), id=person.id):
            if activity := discord.utils.get(member.activities, type=discord.ActivityType.custom):
                if activity.emoji and activity.emoji.is_custom_emoji():
                    badges.append('<:nitro:738961134958149662>')

        return ' '.join(badges) if badges else 'N/A'

    def activities(self, *, person: discord.Member) -> str:

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
                    if activity.album and activity.album != activity.title:
                        message += f'from the album **{activity.album}** '
                    message += '\n'
                else:
                    message += f'• Listening to **{activity.name}**\n'

        return message
