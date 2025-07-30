
from discord.ext import commands
from .music_player import MusicPlayer


class MusicCommands(commands.Cog):
    """Pre-built Discord commands for music functionality."""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_player = MusicPlayer(bot)
    
    @commands.command(name='play', aliases=['p'])
    async def play_command(self, ctx, *, query):
        """Play a song from YouTube."""
        try:
            result = await self.music_player.play(ctx, query)
            await ctx.send(result)
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")
    
    @commands.command(name='pause')
    async def pause_command(self, ctx):
        """Pause the current song."""
        result = self.music_player.pause(ctx)
        await ctx.send(result)
    
    @commands.command(name='resume')
    async def resume_command(self, ctx):
        """Resume the current song."""
        result = self.music_player.resume(ctx)
        await ctx.send(result)
    
    @commands.command(name='stop')
    async def stop_command(self, ctx):
        """Stop playback and clear queue."""
        result = self.music_player.stop(ctx)
        await ctx.send(result)
    
    @commands.command(name='skip', aliases=['next'])
    async def skip_command(self, ctx):
        """Skip the current song."""
        result = await self.music_player.skip(ctx)
        await ctx.send(result)
    
    @commands.command(name='queue', aliases=['q'])
    async def queue_command(self, ctx):
        """Show the current queue."""
        queue = self.music_player.get_queue(ctx)
        if queue:
            queue_text = "\n".join([f"{i+1}. {title}" for i, title in enumerate(queue)])
            await ctx.send(f"Current queue:\n```{queue_text}```")
        else:
            await ctx.send("Queue is empty")
    
    @commands.command(name='nowplaying', aliases=['np'])
    async def now_playing_command(self, ctx):
        """Show currently playing song."""
        result = self.music_player.now_playing(ctx)
        await ctx.send(result)
    
    @commands.command(name='disconnect', aliases=['leave'])
    async def disconnect_command(self, ctx):
        """Disconnect from voice channel."""
        result = await self.music_player.disconnect(ctx)
        await ctx.send(result)


def setup(bot):
    """Function to add the cog to a bot."""
    bot.add_cog(MusicCommands(bot))
