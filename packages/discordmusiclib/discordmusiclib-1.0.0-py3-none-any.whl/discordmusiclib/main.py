
import asyncio
import aiohttp
import re
import json
import urllib.parse
from typing import Dict, List, Optional, Tuple
import base64
import os

class YouTubeAudioDownloader:
    """A custom YouTube audio downloader for Discord bots"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def extract_video_info(self, url: str) -> Dict:
        """Extract video information from YouTube URL"""
        video_id = self._extract_video_id(url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")
        
        # Try different extraction methods
        for method in [self._extract_from_webpage, self._extract_from_embed]:
            try:
                return await method(video_id)
            except Exception as e:
                print(f"Method failed: {e}")
                continue
                
        raise ValueError("Could not extract video information with any method")
    
    async def _extract_from_webpage(self, video_id: str) -> Dict:
        """Extract from main YouTube webpage"""
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with self.session.get(video_url, headers=headers) as response:
            html = await response.text()
            
        # Extract player response
        player_response = self._extract_player_response(html)
        if not player_response:
            raise ValueError("Could not extract player response")
            
        video_details = player_response.get('videoDetails', {})
        streaming_data = player_response.get('streamingData', {})
        
        return {
            'id': video_id,
            'title': video_details.get('title', 'Unknown'),
            'duration': int(video_details.get('lengthSeconds', 0)),
            'uploader': video_details.get('author', 'Unknown'),
            'formats': self._extract_audio_formats(streaming_data)
        }
    
    async def _extract_from_embed(self, video_id: str) -> Dict:
        """Extract from YouTube embed page"""
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with self.session.get(embed_url, headers=headers) as response:
            html = await response.text()
            
        # Extract player response
        player_response = self._extract_player_response(html)
        if not player_response:
            raise ValueError("Could not extract player response from embed")
            
        video_details = player_response.get('videoDetails', {})
        streaming_data = player_response.get('streamingData', {})
        
        return {
            'id': video_id,
            'title': video_details.get('title', 'Unknown'),
            'duration': int(video_details.get('lengthSeconds', 0)),
            'uploader': video_details.get('author', 'Unknown'),
            'formats': self._extract_audio_formats(streaming_data)
        }
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/v/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _extract_player_response(self, html: str) -> Optional[Dict]:
        """Extract player response JSON from HTML"""
        patterns = [
            r'var ytInitialPlayerResponse\s*=\s*({.+?});',
            r'ytInitialPlayerResponse\s*=\s*({.+?});',
            r'"PLAYER_VARS":\s*({.+?})(?:,"EXPERIMENT_FLAGS"|;)',
            r'ytplayer\.config\s*=\s*({.+?});',
        ]
        
        for i, pattern in enumerate(patterns):
            matches = re.finditer(pattern, html, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match.group(1))
                    # Check if this looks like a valid player response
                    if 'videoDetails' in data or 'streamingData' in data:
                        return data
                except json.JSONDecodeError:
                    continue
        
        # Try to find any large JSON object that might contain video data
        json_pattern = r'({[^{}]*"videoDetails"[^{}]*(?:{[^{}]*}[^{}]*)*})'
        matches = re.finditer(json_pattern, html, re.DOTALL)
        for match in matches:
            try:
                data = json.loads(match.group(1))
                return data
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _extract_audio_formats(self, streaming_data: Dict) -> List[Dict]:
        """Extract audio format information"""
        formats = []
        
        # Get adaptive formats (audio only)
        adaptive_formats = streaming_data.get('adaptiveFormats', [])
        
        for fmt in adaptive_formats:
            mime_type = fmt.get('mimeType', '')
            
            # Check for audio formats more broadly
            if 'audio' in mime_type.lower() or fmt.get('audioQuality'):
                url = self._get_format_url(fmt)
                if url:
                    formats.append({
                        'format_id': fmt.get('itag'),
                        'url': url,
                        'ext': self._get_extension_from_mime(mime_type),
                        'abr': fmt.get('averageBitrate', fmt.get('bitrate', 0)),
                        'acodec': self._get_codec_from_mime(mime_type)
                    })
        
        # Also check regular formats
        regular_formats = streaming_data.get('formats', [])
        
        for fmt in regular_formats:
            mime_type = fmt.get('mimeType', '')
            # Include formats that have audio even if they also have video
            if 'audio' in mime_type.lower() or fmt.get('audioQuality'):
                url = self._get_format_url(fmt)
                if url:
                    formats.append({
                        'format_id': fmt.get('itag'),
                        'url': url,
                        'ext': self._get_extension_from_mime(mime_type),
                        'abr': fmt.get('averageBitrate', fmt.get('bitrate', 0)),
                        'acodec': self._get_codec_from_mime(mime_type)
                    })
        
        return sorted(formats, key=lambda x: x.get('abr', 0), reverse=True)
    
    def _get_format_url(self, fmt: Dict) -> Optional[str]:
        """Extract URL from format, handling ciphered URLs"""
        # Direct URL
        if fmt.get('url'):
            return fmt['url']
        
        # Ciphered URL (signatureCipher or cipher)
        cipher = fmt.get('signatureCipher') or fmt.get('cipher')
        if cipher:
            try:
                # Parse the cipher parameters
                cipher_params = urllib.parse.parse_qs(cipher)
                url = cipher_params.get('url', [None])[0]
                s = cipher_params.get('s', [None])[0]
                
                if url and s:
                    # Decode the URL
                    decoded_url = urllib.parse.unquote(url)
                    # Simple signature transformation
                    transformed_sig = self._transform_signature(s)
                    
                    # Add the signature parameter
                    separator = '&' if '?' in decoded_url else '?'
                    full_url = f"{decoded_url}{separator}sig={transformed_sig}"
                    
                    return full_url
                elif url:
                    # Return base URL without signature
                    return urllib.parse.unquote(url)
            except Exception:
                pass
        
        # Try alternative URL fields
        for url_field in ['streamingUrl', 'baseUrl']:
            if fmt.get(url_field):
                return fmt[url_field]
        
        return None
    
    def _transform_signature(self, signature: str) -> str:
        """Basic signature transformation"""
        sig = signature
        
        # Common transformations (these change frequently)
        if len(sig) >= 3:
            # Reverse
            sig = sig[::-1]
            
            # Swap first and last
            if len(sig) > 1:
                sig = sig[-1] + sig[1:-1] + sig[0]
                
            # Remove character at position 0
            if len(sig) > 1:
                sig = sig[1:]
        
        return sig
    
    def _get_extension_from_mime(self, mime_type: str) -> str:
        """Get file extension from MIME type"""
        if 'mp4' in mime_type:
            return 'm4a'
        elif 'webm' in mime_type:
            return 'webm'
        elif 'ogg' in mime_type:
            return 'ogg'
        return 'unknown'
    
    def _get_codec_from_mime(self, mime_type: str) -> str:
        """Get audio codec from MIME type"""
        if 'mp4a' in mime_type:
            return 'aac'
        elif 'opus' in mime_type:
            return 'opus'
        elif 'vorbis' in mime_type:
            return 'vorbis'
        return 'unknown'
    
    async def get_audio_stream_url(self, url: str, prefer_format: str = 'best') -> Tuple[str, Dict]:
        """Get the best audio stream URL and info"""
        info = await self.extract_video_info(url)
        formats = info['formats']
        
        if not formats:
            raise ValueError("No audio formats found")
        
        # Select best format
        if prefer_format == 'best':
            selected_format = formats[0]  # Already sorted by bitrate
        else:
            # Find format by codec preference
            selected_format = next(
                (fmt for fmt in formats if fmt.get('acodec') == prefer_format),
                formats[0]
            )
        
        if not selected_format or not selected_format.get('url'):
            raise ValueError("No valid audio stream URL found")
        
        return selected_format['url'], info

class DiscordMusicBot:
    """Example Discord bot integration"""
    
    def __init__(self):
        self.downloader = None
    
    async def play_youtube_audio(self, url: str) -> Dict:
        """Get YouTube audio stream for Discord bot playback"""
        async with YouTubeAudioDownloader() as downloader:
            try:
                stream_url, info = await downloader.get_audio_stream_url(url)
                return {
                    'success': True,
                    'stream_url': stream_url,
                    'title': info['title'],
                    'duration': info['duration'],
                    'uploader': info['uploader']
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
