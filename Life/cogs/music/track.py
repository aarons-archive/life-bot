import andesite

class Track(andesite.Track):

    def __init__(self, id_, info, *, ctx=None):
        super(Track, self).__init__(id_, info)

        # Store the author and channel the track was requested in when playing it.
        self.channel = ctx.channel
        self.requester = ctx.author
