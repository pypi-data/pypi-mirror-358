
"""Discord Music Streamer - A Python library for streaming music in Discord voice channels."""

from .music_player import MusicPlayer
from .queue_manager import QueueManager
from .youtube_source import YouTubeSource

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "you@example.com"

__all__ = ["MusicPlayer", "QueueManager", "YouTubeSource"]
