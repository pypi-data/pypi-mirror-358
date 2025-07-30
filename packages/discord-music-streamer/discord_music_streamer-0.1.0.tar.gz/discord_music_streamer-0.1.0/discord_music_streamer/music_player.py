import asyncio
import discord
from discord.ext import commands
from typing import Dict, Optional
from .queue_manager import QueueManager
from .youtube_source import YouTubeSource


class MusicPlayer:
    """Main music player class for Discord voice channels."""

    def __init__(self, bot):
        self.bot = bot
        self.queue_manager = QueueManager()
        self.voice_clients = {}
        self.current_players = {}

    async def join_voice_channel(self, ctx, channel=None):
        """Join a voice channel."""
        if channel is None:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
            else:
                raise ValueError("No voice channel specified and user not in voice channel")

        if ctx.guild.id in self.voice_clients:
            await self.voice_clients[ctx.guild.id].move_to(channel)
        else:
            voice_client = await channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client

        return self.voice_clients[ctx.guild.id]

    async def play(self, ctx, query: str):
        """Play a song from YouTube."""
        # Connect to voice channel if not already connected
        if ctx.guild.id not in self.voice_clients:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                voice_client = await channel.connect()
                self.voice_clients[ctx.guild.id] = voice_client
            else:
                return "You need to be in a voice channel to play music"

        voice_client = self.voice_clients[ctx.guild.id]

        try:
            # Create YouTube source
            source = await YouTubeSource.create_source(query)

            if voice_client.is_playing():
                # Add to queue
                self.queue_manager.add_to_queue(ctx.guild.id, source)
                return f"Added to queue: {source.title}"
            else:
                # Play immediately
                voice_client.play(source, after=lambda e: self._play_next(ctx))
                self.current_players[ctx.guild.id] = source
                return f"Now playing: {source.title}"
        except Exception as e:
            return f"Error loading song: {str(e)}"

    def pause(self, ctx):
        """Pause the current song."""
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            if voice_client.is_playing():
                voice_client.pause()
                return "Playback paused"
        return "Nothing is currently playing"

    def resume(self, ctx):
        """Resume the current song."""
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            if voice_client.is_paused():
                voice_client.resume()
                return "Playback resumed"
        return "Nothing is currently paused"

    def stop(self, ctx):
        """Stop the current song and clear queue."""
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            voice_client.stop()
            self.queue_manager.clear_queue(ctx.guild.id)
            return "Playback stopped and queue cleared"
        return "Nothing is currently playing"

    async def skip(self, ctx):
        """Skip the current song."""
        if ctx.guild.id in self.voice_clients:
            voice_client = self.voice_clients[ctx.guild.id]
            voice_client.stop()  # This will trigger _play_next
            return "Skipped current song"
        return "Nothing is currently playing"

    def get_queue(self, ctx):
        """Get the current queue."""
        return self.queue_manager.get_queue(ctx.guild.id)

    async def disconnect(self, ctx):
        """Disconnect from voice channel."""
        if ctx.guild.id in self.voice_clients:
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]
            self.queue_manager.clear_queue(ctx.guild.id)
            if ctx.guild.id in self.current_players:
                del self.current_players[ctx.guild.id]
            return "Disconnected from voice channel"
        return "Not connected to any voice channel"

    def _play_next(self, ctx):
        """Play the next song in queue."""
        guild_id = ctx.guild.id
        next_source = self.queue_manager.get_next(guild_id)

        if next_source and guild_id in self.voice_clients:
            voice_client = self.voice_clients[guild_id]
            voice_client.play(next_source, after=lambda e: self._play_next(ctx))
            self.current_players[guild_id] = next_source

    def now_playing(self, ctx):
        """Get currently playing song info."""
        if ctx.guild.id in self.current_players:
            current = self.current_players[ctx.guild.id]
            return f"Now playing: {current.title}"
        return "Nothing is currently playing"