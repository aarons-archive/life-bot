import random

import andesite
from discord.ext import commands

from ..utilities import formatting
from .track import Track


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.andesite = andesite.Client(self.bot)

    async def initiate_nodes(self):

        for n in self.bot.config.NODES.values():
            try:
                await self.bot.andesite.start_node(
                    n["ip"],
                    port=n["port"],
                    rest_uri=n["rest_uri"],
                    password=n["password"],
                    identifier=n["identifier"]
                )
            except andesite.InvalidCredentials:
                print(f"\n[ANDESITE] Invalid credentials for node {n['identifier']}.")
                continue
            except ConnectionRefusedError:
                print(f"Failed to connect to node {n['identifier']}")
                continue
            print(f"\n[ANDESITE] Node {n['identifier']} connected.")

    @commands.command(name="join", aliases=["connect"])
    async def join(self, ctx):
        """
        Join or move to the users voice channel.
        """

        # If the user is not in a voice channel then tell them that they have to be in one.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")
        channel = ctx.author.voice.channel

        # If the player is not already connected.
        if not ctx.player.is_connected or not ctx.guild.me.voice.channel:
            # Join the channel.
            await ctx.player.connect(channel.id)
            # Set the players channel to this one.
            ctx.player.channel = ctx.channel
            return await ctx.send(f"Joined the voice channel `{channel}`.")

        # If the player is connected but the user is in another voice channel then move to that channel.
        if ctx.guild.me.voice.channel.id != channel.id:
            await ctx.player.connect(channel.id)
            # Set the players channel to this one.
            ctx.player.channel = ctx.channel
            return await ctx.send(f"Moved to the voice channel `{channel}`.")

        # The bot must already be in this voice channel.
        return await ctx.send("I am already in this voice channel.")

    @commands.command(name="leave", aliases=["disconnect", "stop"])
    async def leave(self, ctx):
        """
        Leave the current voice channel.
        """

        # If the player is not connected then do nothing.
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not in a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # Clear the queue, destroy and disconnect the player.
        ctx.player.queue.clear()
        ctx.player.current = None
        await ctx.player.disconnect()
        await ctx.player.destroy()
        return await ctx.send(f"Left the voice channel `{ctx.guild.me.voice.channel}`.")

    @commands.command(name="search")
    async def search(self, ctx, *, search: str):
        """
        Search for all tracks with a given search query.

        `search`: The name of the track you want to search for.
        """
        # Trigger typing.
        await ctx.trigger_typing()

        # Get a list of all the tracks for the users search term.
        tracks = await ctx.player.node.get_tracks(f"{search}")
        # If no track were found.
        if not tracks:
            return await ctx.send(f"No results were found for the search term `{search}`.")

        # Create a list of results to paginate.
        results = []
        for index, track in enumerate(tracks):
            message = f"**{index + 1}.** [{track.title}]({track.uri})"
            results.append(message)

        title = f"Showing all results for the search term `{search}`\n\n"

        return await ctx.paginate_embed(entries=results, entries_per_page=10, title=title)

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):
        """
        Play a track using a link or search query.

        `search`: The name/link of the track you want to search for.
        """

        # If the user it not in a voice channel then tell them that have to be in one.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")
        channel = ctx.author.voice.channel

        # If the player is not already connected, join the users voice channel.
        if not ctx.player.is_connected:
            await ctx.player.connect(channel.id)

        ctx.player.channel = ctx.channel

        # Trigger typing.
        await ctx.trigger_typing()

        # Get a list of all the tracks for the users search term.
        tracks = await ctx.player.node.get_tracks(f"{search}")
        # If there were no tracks.
        if not tracks:
            return await ctx.send(f"No results were found for the search term `{search}`.")

        # If "tracks" was a playlist
        if isinstance(tracks, andesite.Playlist):
            # Loop through all the tracks in the playlist and add them to the queue
            for track in tracks.tracks:
                await ctx.player.queue.put(Track(track.id, track.data, ctx=ctx))
            return await ctx.send(f"Added the playlist **{tracks.name}** to the queue with a total of **{len(tracks.tracks)}** entries.")

        # Get the first entry in the list of tracks and add it to the queue.
        track = tracks[0]
        await ctx.player.queue.put(Track(track.id, track.data, ctx=ctx))
        return await ctx.send(f"Added the track **{track.title}** to the queue.")

    @commands.command(name="pause")
    async def pause(self, ctx):
        """
        Pause the current track.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If nothing is currently playing.
        if not ctx.player.current:
            return await ctx.send("No tracks currently playing.")

        # If the player is already paused.
        if ctx.player.paused is True:
            return await ctx.send("The current track is already paused.")

        await ctx.player.set_pause(True)
        return await ctx.send(f"Paused the current track.")

    @commands.command(name="resume")
    async def resume(self, ctx):
        """
        Resume the current track.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If nothing is current playing.
        if not ctx.player.current:
            return await ctx.send("No tracks currently playing.")

        # If the track is not paused
        if ctx.player.paused is False:
            return await ctx.send("The current track is not paused.")

        await ctx.player.set_pause(False)
        return await ctx.send(f"Resumed playback of the current track.")

    @commands.command(name="skip")
    async def skip(self, ctx, amount: int = 0):
        """
        Skip to the next track in the queue.

        This will auto skip if you are the requester of the current track, otherwise a vote will start to skip the track.

        `amount`: An optional number for skipping multiple tracks at once.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If there are no track currently playing.
        if not ctx.player.current:
            return await ctx.send("There is nothing currently playing.")

        # If the user is not the current tracks requester.
        if ctx.player.current.requester.id != ctx.author.id:
            return await ctx.send("Vote skipping coming soon.")

        # If the user has not specified an amount of tracks to skip.
        if not amount:
            await ctx.player.stop()
            return await ctx.send(f"The current tracks requester has skipped the current track.")

        # If the amount of tracks to skip is smaller then 1 or larger then the amount of tracks in the queue.
        if amount <= 0 or amount > ctx.player.queue.size():
            return await ctx.send(f"That is not a valid amount of tracks to skip. Please choose a value between `1` and `{ctx.player.queue.size()}`")

        # Loop through the next "amount" of tracks in the queue
        for track in ctx.player.queue.queue[:amount - 1]:
            # If the user is not the requester of the tracks then return and dont skip.
            if not ctx.author.id == track.requester.id:
                return await ctx.send(f"You are not the requester of all `{amount}` of the next tracks in the queue.")
            # Else, skip remove the track from the queue.
            await ctx.player.queue.get_pos(0)

        # Now skip the current track and return.
        await ctx.player.stop()
        return await ctx.send(f"The current tracks requester has skipped `{amount}` tracks.")

    @commands.command(name="now_playing", aliases=["np"])
    async def now_playing(self, ctx):
        """
        Display information about the current song/queue status.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If nothing is current playing.
        if not ctx.player.current:
            return await ctx.send("No tracks currently playing.")

        # Invoke the controller
        return await ctx.player.invoke_controller()

    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, volume: int = None):
        """
        Change the volume of the player.

        `volume`: The percentage to change the volume to, can be between 0 and 100.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If the user doesnt input a volume to change too.
        if not volume and not volume == 0:
            return await ctx.send(f"The current volume is `{ctx.player.volume}%`.")

        # Make sure the value is between 0 and 100.
        if volume < 0 or volume > 100:
            return await ctx.send(f"Please enter a value between `1` and and `100`.")

        ctx.player.volume = volume
        await ctx.player.set_volume(volume)
        return await ctx.send(f"Changed the players volume to `{volume}%`.")

    @commands.command(name="seek")
    async def seek(self, ctx, seconds: int = None):
        """
        Change the postion of the player.

        `position`: The position of the track to skip to in seconds.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If nothing is current playing.
        if not ctx.player.current:
            return await ctx.send("No tracks currently playing.")

        # If the current track is not seekable.
        if not ctx.player.current.is_seekable:
            return await ctx.send("This track is not seekable.")

        if not seconds and not seconds == 0:
            return await ctx.send(f"The current position is {formatting.get_time(ctx.player.position / 1000)}")

        # Check if the amount of time is between 0 and the length of the track.
        milliseconds = seconds * 1000
        if milliseconds < 0 or milliseconds > ctx.player.current.length:
            return await ctx.send(f"Please enter a value between `1` and `{round(ctx.player.current.length / 1000)}`.")

        # Seek to the position
        await ctx.player.seek(milliseconds)
        return await ctx.send(f"Changed the players position to `{formatting.get_time(milliseconds / 1000)}`.")

    @commands.command(name="queue")
    async def queue(self, ctx):
        """
        Display the queue.
        """

        # If the player is not connected then do nothing.
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the queue is empty.
        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        # Define a title with information about the current track.
        title = f"__**Current track:**__\n[{ctx.player.current.title}]({ctx.player.current.uri}) | " \
                  f"`{formatting.get_time(round(ctx.player.current.length) / 1000)}` | " \
                  f"`Requested by:` {ctx.player.current.requester.mention}\n\n" \
                  f"__**Up next:**__: Showing `10` out of `{ctx.player.queue.size()}` entries in the queue.\n"

        # Create a list of entries representing the tracks in the queue.
        entries = []
        for index, track in enumerate(ctx.player.queue.queue):
            entries.append(f"**{index + 1}.** [{str(track.title)}]({track.uri}) | " 
                           f"`{formatting.get_time(round(track.length) / 1000)}` | " 
                           f"`Requested by:` {track.requester.mention}\n")

        # Define a time and loop through all songs in the queue to get the total time.
        time = 0
        for track in ctx.player.queue.queue:
            time += track.length

        # Add extra info to the message.
        footer = f"\nThere are `{ctx.player.queue.size()}` tracks in the queue with a total time of `{formatting.get_time(round(time) / 1000)}`"

        # Paginate the list of queue entries.
        return await ctx.paginate_embed(title=title, footer=footer, entries=entries, entries_per_page=10)

    @commands.command(name="shuffle")
    async def shuffle(self, ctx):
        """
        Shuffle the queue.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If the queue is empty.
        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        # Shuffle the queue.
        random.shuffle(ctx.player.queue.queue)
        return await ctx.send(f"The queue has been shuffled.")

    @commands.command(name="clear")
    async def clear(self, ctx):
        """
        Clear the queue.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If the queue is empty.
        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        # Clear the queue.
        ctx.player.queue.queue.clear()
        return await ctx.send(f"Cleared the queue.")

    @commands.command(name="reverse")
    async def reverse(self, ctx):
        """
        Reverse the queue.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If the queue is empty.
        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        # Reverse the queue.
        ctx.player.queue.queue.reverse()
        return await ctx.send(f"Reversed the queue.")

    @commands.command(name="loop")
    async def loop(self, ctx):
        """
        Loop the queue.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If queue_loop is already True then set it to false, basic toggling.
        if ctx.player.queue_loop is True:
            ctx.player.queue_loop = False
            return await ctx.send(f"The queue will stop looping.")
        # Else set it to true.
        ctx.player.queue_loop = True
        return await ctx.send(f"The queue will now loop.")

    @commands.command(name="remove")
    async def remove(self, ctx, entry: int = 0):
        """
        Remove an entry from the queue.

        `entry`: The number of the entry you want to remove.
        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If the queue is empty.
        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        # Check if the entry is between 0 and queue size.
        if entry <= 0 or entry > ctx.player.queue.size():
            return await ctx.send(f"That was not a valid track entry number.")

        # Remove the entry from the queue.
        item = await ctx.player.queue.get_pos(entry - 1)
        return await ctx.send(f"Removed `{item}` from the queue.")

    @commands.command(name="move")
    async def move(self, ctx, entry_1: int = 0, entry_2: int = 0):
        """
        Move an entry from one position to another in the queue.

        When moving entries use the number shown in the `queue` command. For example `mb move 1 15` will move the track in 1st position to 15th.

        `entry_1`: The number of the entry you want to move from.
        `entry_2`: The number of the entry you want to move too.


        """

        # If the player is not connected then do nothing
        if not ctx.player.is_connected:
            return await ctx.send(f"MrBot is not connected to any voice channels.")

        # If the user is not a voice channel.
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send(f"You must be in a voice channel to use this command.")

        # If the user is not in the same voice channel as the bot.
        if ctx.player.channel_id != ctx.author.voice.channel.id:
            return await ctx.send(f"You must be in the same voice channel as me to use this command.")

        # If the queue is empty.
        if ctx.player.queue.empty():
            return await ctx.send("The queue is empty.")

        # Check if the entry_1 is between 0 and queue size.
        if entry_1 <= 0 or entry_1 > ctx.player.queue.size():
            return await ctx.send(f"That was not a valid track to move from.")

        # Check if the entry is between 0 and queue size.
        if entry_2 <= 0 or entry_2 > ctx.player.queue.size():
            return await ctx.send(f"That was not a valid track to move too.")

        # get the track we want to move.
        item = await ctx.player.queue.get_pos(entry_1 - 1)

        # Search for it again.
        tracks = await ctx.player.node.get_tracks(f"{item}")
        track = tracks[0]

        # Move it the chose position.
        await ctx.player.queue.put_pos(Track(track.id, track.data, ctx=ctx), entry_2 - 1)
        return await ctx.send(f"Moved `{item}` from position `{entry_1}` to position `{entry_2}`.")


def setup(bot):
    bot.add_cog(Music(bot))
    bot.loop.create_task(Music(bot).initiate_nodes())

