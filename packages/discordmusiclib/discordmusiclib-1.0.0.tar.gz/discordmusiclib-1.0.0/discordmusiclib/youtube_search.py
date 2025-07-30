
import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional

class YouTubeSearcher:
    """Alternative YouTube search and stream finder"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_youtube(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube for videos"""
        # Using YouTube's internal search API
        search_url = "https://www.youtube.com/youtubei/v1/search"
        
        params = {
            'key': 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8',  # Public key
        }
        
        data = {
            'context': {
                'client': {
                    'clientName': 'WEB',
                    'clientVersion': '2.20240101.00.00'
                }
            },
            'query': query
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            async with self.session.post(search_url, params=params, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_search_results(result, max_results)
        except Exception as e:
            print(f"Search error: {e}")
        
        return []
    
    def _parse_search_results(self, data: Dict, max_results: int) -> List[Dict]:
        """Parse search results from YouTube API response"""
        results = []
        
        try:
            contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
            
            for section in contents:
                items = section.get('itemSectionRenderer', {}).get('contents', [])
                
                for item in items:
                    if 'videoRenderer' in item:
                        video = item['videoRenderer']
                        video_id = video.get('videoId')
                        title = video.get('title', {}).get('runs', [{}])[0].get('text', 'Unknown')
                        
                        # Get duration
                        duration_text = video.get('lengthText', {}).get('simpleText', '0:00')
                        duration_seconds = self._parse_duration(duration_text)
                        
                        # Get channel name
                        channel = video.get('ownerText', {}).get('runs', [{}])[0].get('text', 'Unknown')
                        
                        if video_id:
                            results.append({
                                'id': video_id,
                                'title': title,
                                'duration': duration_seconds,
                                'uploader': channel,
                                'url': f'https://www.youtube.com/watch?v={video_id}'
                            })
                            
                        if len(results) >= max_results:
                            break
                
                if len(results) >= max_results:
                    break
                    
        except Exception as e:
            print(f"Parse error: {e}")
        
        return results
    
    def _parse_duration(self, duration_text: str) -> int:
        """Convert duration text like '3:45' to seconds"""
        try:
            parts = duration_text.split(':')
            if len(parts) == 2:
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except:
            pass
        return 0
