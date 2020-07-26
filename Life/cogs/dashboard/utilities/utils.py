"""
Life
Copyright (C) 2020 MrRandom#9258

Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later version.

Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with Life.  If not, see <https://www.gnu.org/licenses/>.
"""


from cogs.voice.utilities import objects


def generate_track_html(handler, track: objects.LifeTrack):
    length = handler.bot.utils.format_time(round(track.length) / 1000)
    html = f"""
    <div class='text-light'>
        <p class="m-0">Author: {track.author}<br>Length: {length}<br>Requester: {track.requester}</p>
        <img class="img-fluid rounded mt-2" src="{track.thumbnail}" alt="Track thumbnail">
    </div>
    """
    return html
