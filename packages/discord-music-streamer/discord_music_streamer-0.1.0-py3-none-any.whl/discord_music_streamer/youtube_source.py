
import asyncio
import discord
import yt_dlp
from typing import Optional, Dict, Any

class YouTubeSource(discord.PCMVolumeTransformer):
    """YouTube audio source for Discord voice channels."""
    
    YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'extract_flat': False,
    }

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
        
        ytdl = yt_dlp.YoutubeDL(cls.YTDL_OPTIONS)
        
        # Run the blocking yt-dlp operation in a thread pool
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(search, download=False))
        
        if 'entries' in data:
            # Take the first result if it's a playlist
            data = data['entries'][0]
        
        if not data:
            raise Exception(f"Could not find any results for: {search}")
        
        # Create the audio source
        source = discord.FFmpegPCMAudio(data['url'], **cls.FFMPEG_OPTIONS)
        
        return cls(source, data=data)

    @classmethod
    async def search_youtube(cls, query: str, max_results: int = 5) -> list:
        """Search YouTube and return a list of results."""
        ytdl = yt_dlp.YoutubeDL({
            **cls.YTDL_OPTIONS,
            'quiet': True,
            'extract_flat': True,
        })
        
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch{max_results}:{query}", download=False))
        
        if not data or 'entries' not in data:
            return []
        
        results = []
        for entry in data['entries']:
            if entry:
                results.append({
                    'title': entry.get('title', 'Unknown'),
                    'url': entry.get('url', ''),
                    'duration': entry.get('duration', 0),
                    'uploader': entry.get('uploader', 'Unknown'),
                })
        
        return results

    def __str__(self):
        return f"**{self.title}** by **{self.uploader}**"
