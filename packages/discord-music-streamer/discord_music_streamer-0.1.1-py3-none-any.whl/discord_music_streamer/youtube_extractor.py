
import re
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs

class YouTubeExtractor:
    """Custom YouTube audio URL extractor without external dependencies."""
    
    BASE_URL = "https://www.youtube.com"
    SEARCH_URL = "https://www.youtube.com/results"
    
    @staticmethod
    async def extract_video_info(video_id: str) -> Dict:
        """Extract video information and audio URL from YouTube video ID."""
        try:
            async with aiohttp.ClientSession() as session:
                # Get video page
                video_url = f"{YouTubeExtractor.BASE_URL}/watch?v={video_id}"
                async with session.get(video_url) as response:
                    html = await response.text()
                
                # Extract player response JSON
                player_response = YouTubeExtractor._extract_player_response(html)
                if not player_response:
                    raise Exception("Could not extract player response")
                
                # Extract video details
                video_details = player_response.get('videoDetails', {})
                streaming_data = player_response.get('streamingData', {})
                
                # Find audio stream
                audio_url = YouTubeExtractor._extract_audio_url(streaming_data)
                if not audio_url:
                    raise Exception("No audio stream found")
                
                return {
                    'title': video_details.get('title', 'Unknown'),
                    'url': audio_url,
                    'duration': int(video_details.get('lengthSeconds', 0)),
                    'uploader': video_details.get('author', 'Unknown'),
                    'video_id': video_id
                }
                
        except Exception as e:
            raise Exception(f"Failed to extract video info: {str(e)}")
    
    @staticmethod
    async def search_videos(query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube for videos and return results."""
        try:
            async with aiohttp.ClientSession() as session:
                params = {'search_query': query}
                async with session.get(YouTubeExtractor.SEARCH_URL, params=params) as response:
                    html = await response.text()
                
                # Extract video data from search results
                video_ids = YouTubeExtractor._extract_search_results(html)
                
                results = []
                for video_id in video_ids[:max_results]:
                    try:
                        video_info = await YouTubeExtractor.extract_video_info(video_id)
                        results.append(video_info)
                    except:
                        continue  # Skip failed extractions
                
                return results
                
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")
    
    @staticmethod
    def _extract_player_response(html: str) -> Optional[Dict]:
        """Extract player response JSON from YouTube page HTML."""
        patterns = [
            r'var ytInitialPlayerResponse = ({.+?});',
            r'"playerResponse":"({.+?})"',
            r'ytInitialPlayerResponse":\s*({.+?})(?:,|\s*})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                try:
                    json_str = match.group(1)
                    # Handle escaped JSON
                    if json_str.startswith('"'):
                        json_str = json_str[1:-1].replace('\\"', '"').replace('\\\\', '\\')
                    return json.loads(json_str)
                except:
                    continue
        
        return None
    
    @staticmethod
    def _extract_audio_url(streaming_data: Dict) -> Optional[str]:
        """Extract the best audio stream URL from streaming data."""
        formats = streaming_data.get('adaptiveFormats', [])
        
        # Look for audio-only formats
        audio_formats = [f for f in formats if f.get('mimeType', '').startswith('audio/')]
        
        if not audio_formats:
            # Fallback to regular formats
            formats = streaming_data.get('formats', [])
            audio_formats = [f for f in formats if f.get('mimeType', '').startswith('audio/')]
        
        if not audio_formats:
            return None
        
        # Sort by audio quality (bitrate)
        audio_formats.sort(key=lambda x: x.get('bitrate', 0), reverse=True)
        
        return audio_formats[0].get('url')
    
    @staticmethod
    def _extract_search_results(html: str) -> List[str]:
        """Extract video IDs from search results page."""
        pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
        matches = re.findall(pattern, html)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for match in matches:
            if match not in seen:
                seen.add(match)
                unique_matches.append(match)
        
        return unique_matches
    
    @staticmethod
    def extract_video_id(url_or_query: str) -> Optional[str]:
        """Extract video ID from YouTube URL or return None if it's a search query."""
        youtube_patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in youtube_patterns:
            match = re.search(pattern, url_or_query)
            if match:
                return match.group(1)
        
        return None
