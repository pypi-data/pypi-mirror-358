import asyncio
import discord
from typing import Optional, Dict, Any
from .youtube_extractor import YouTubeExtractor

class YouTubeSource(discord.PCMVolumeTransformer):
    """YouTube audio source for Discord voice channels."""

    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    def __init__(self, source: discord.AudioSource, *, data: Dict[str, Any], volume: float = 0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title', 'Unknown')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.uploader = data.get('uploader', 'Unknown')

    @classmethod
    async def create_source(cls, search: str, *, loop: Optional[asyncio.AbstractEventLoop] = None) -> 'YouTubeSource':
        """Create a YouTube source from a search query or URL."""
        loop = loop or asyncio.get_event_loop()

        try:
            # Check if it's a YouTube URL or search query
            video_id = YouTubeExtractor.extract_video_id(search)

            if video_id:
                # Direct video URL
                data = await YouTubeExtractor.extract_video_info(video_id)
            else:
                # Search query
                search_results = await YouTubeExtractor.search_videos(search, max_results=1)
                if not search_results:
                    raise Exception(f"No results found for: {search}")
                data = search_results[0]

            if not data.get('url'):
                raise Exception(f"No audio URL found for: {search}")

            # Create the audio source
            try:
                source = discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS)
            except Exception as ffmpeg_error:
                raise Exception(f"FFmpeg error: {str(ffmpeg_error)}. Make sure FFmpeg is installed.")

            return cls(source, data=data)

        except Exception as e:
            if "FFmpeg" in str(e):
                raise e  # Re-raise FFmpeg errors as-is
            raise Exception(f"Failed to create audio source: {str(e)}")

    @classmethod
    async def search_youtube(cls, query: str, max_results: int = 5) -> list:
        """Search YouTube and return a list of results."""
        try:
            results = await YouTubeExtractor.search_videos(query, max_results)
            return [{
                'title': result.get('title', 'Unknown'),
                'url': result.get('url', ''),
                'duration': result.get('duration', 0),
                'uploader': result.get('uploader', 'Unknown'),
            } for result in results]
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")

    def __str__(self):
        return f"**{self.title}** by **{self.uploader}**"