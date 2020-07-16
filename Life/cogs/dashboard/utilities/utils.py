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
