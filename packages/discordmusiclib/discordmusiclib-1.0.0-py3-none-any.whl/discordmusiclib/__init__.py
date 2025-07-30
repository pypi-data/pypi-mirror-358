
"""
DiscordMusicLib - A custom YouTube audio downloader for Discord bots
"""

from .main import YouTubeAudioDownloader, DiscordMusicBot
from .simple_api import SimpleYouTubeAudio
from .youtube_search import YouTubeSearcher

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "YouTubeAudioDownloader",
    "DiscordMusicBot", 
    "SimpleYouTubeAudio",
    "YouTubeSearcher"
]
