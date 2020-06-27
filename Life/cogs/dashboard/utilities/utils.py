from cogs.voice.utilities import objects
from typing import Union


def generate_track_html(handler, track: Union[objects.SpotifyTrack, objects.SpotifyTrack]):
    html = f"""
    <div class='text-light'>
        <p class="m-0 bg-lgray">Author: {track.author}</p>
        <p class="m-0 bg-lgray">Length: {handler.bot.utils.format_time(round(track.length) / 1000)}</p>
        <p class="m-0 bg-lgray">Requester: {track.requester}</p>
        <img class="img-fluid rounded mt-1" src="{track.thumbnail}" alt="Track thumbnail">
    </div>
    """
    return html

