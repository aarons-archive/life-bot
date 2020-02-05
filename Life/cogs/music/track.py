from granitepy import objects


class Track(objects.Track):

    def __init__(self, track_id: str, info: dict, ctx):
        super(Track, self).__init__(track_id, info)

        self.requester = ctx.author
