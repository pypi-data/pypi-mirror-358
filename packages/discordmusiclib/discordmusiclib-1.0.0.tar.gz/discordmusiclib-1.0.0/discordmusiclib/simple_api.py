
import asyncio
from .main import YouTubeAudioDownloader

class SimpleYouTubeAudio:
    """Simplified sync wrapper for the YouTube audio downloader"""
    
    @staticmethod
    def get_audio_info(url: str) -> dict:
        """Get audio information synchronously"""
        return asyncio.run(SimpleYouTubeAudio._get_info_async(url))
    
    @staticmethod
    def get_stream_url(url: str) -> str:
        """Get audio stream URL synchronously"""
        return asyncio.run(SimpleYouTubeAudio._get_stream_async(url))
    
    @staticmethod
    async def _get_info_async(url: str) -> dict:
        async with YouTubeAudioDownloader() as downloader:
            return await downloader.extract_video_info(url)
    
    @staticmethod
    async def _get_stream_async(url: str) -> str:
        async with YouTubeAudioDownloader() as downloader:
            stream_url, _ = await downloader.get_audio_stream_url(url)
            return stream_url
