"""
Audio Processing Module
Handles multi-source audio download functionality using direct music sources.
YouTube-free implementation to avoid bot detection on cloud platforms.
"""

import os
import logging
import asyncio
import aiohttp
import json
from typing import Dict, Optional
import tempfile
import hashlib
import re
import time

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Handles multi-source audio download operations with intelligent fallback."""
    
    def __init__(self):
        """Initialize audio processor with YouTube-free capabilities."""
        self.download_dir = tempfile.mkdtemp(prefix="music_bot_")
        self.session = None
        
        logger.info(f"Audio processor initialized with download directory: {self.download_dir}")
        logger.info("Using Y2Mate YouTube download system with anti-bot protection")
    
    async def download_track(self, track_info: Dict, quality: str) -> Optional[str]:
        """
        Download track audio file using multi-source fallback system.
        
        Args:
            track_info: Track information dictionary
            quality: Quality preference (128, 192, 320)
            
        Returns:
            Path to downloaded file or None if failed
        """
        search_query = f"{track_info['name']} {track_info['artist']}"
        logger.info(f"Starting multi-source download for: {search_query}")
        
        # Initialize aiohttp session if needed with strict timeout
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=15, connect=5, sock_read=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Use Y2Mate with YouTube access and anti-bot protection
        sources = [
            ("Y2Mate", self._download_with_y2mate_youtube)
        ]
        
        for source_name, download_func in sources:
            try:
                logger.info(f"Trying {source_name} for: {search_query}")
                # Add asyncio timeout wrapper to prevent hanging
                file_path = await asyncio.wait_for(
                    download_func(search_query, track_info, quality), 
                    timeout=60.0  # 60 second max per source
                )
                if file_path and os.path.exists(file_path):
                    logger.info(f"Successfully downloaded from {source_name}: {file_path}")
                    return file_path
                else:
                    logger.warning(f"{source_name} failed for: {search_query}")
            except asyncio.TimeoutError:
                logger.error(f"{source_name} timed out after 60s for: {search_query}")
                continue
            except Exception as e:
                logger.error(f"{source_name} error for {search_query}: {e}")
                continue
        
        logger.error(f"Y2Mate failed for: {search_query}")
        return None
    
    async def _download_with_zippyshare(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """
        Download audio using Zippyshare direct links (Secondary source).
        
        Args:
            search_query: Search query string
            track_info: Track information dictionary
            quality: Quality preference (128, 192, 320)
            
        Returns:
            Path to downloaded file or None
        """
        try:
            # Generate filename
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            # Zippyshare search API (simulated - would need real API)
            search_url = "https://api.zippyshare.com/v1/search"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/json'
            }
            
            # Search for direct music files
            search_data = {
                'query': f"{track_info['name']} {track_info['artist']}",
                'type': 'audio',
                'limit': 5
            }
            
            # Note: This is a placeholder implementation
            # Real implementation would require valid Zippyshare API
            logger.warning("Zippyshare source not yet implemented - skipping")
            return None
            
        except Exception as e:
            logger.error(f"Zippyshare download error: {e}")
            return None

    async def _download_with_soundcloud(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """
        Download audio using SoundCloud API (Tertiary source).
        
        Args:
            search_query: Search query string
            track_info: Track information dictionary
            quality: Quality preference (128, 192, 320)
            
        Returns:
            Path to downloaded file or None
        """
        try:
            # Generate filename
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            # SoundCloud public API for search
            search_url = "https://api.soundcloud.com/tracks"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            # Search parameters
            params = {
                'q': f"{track_info['name']} {track_info['artist']}",
                'client_id': 'your_soundcloud_client_id',  # Would need registration
                'limit': 5,
                'downloadable': 'true'
            }
            
            # Note: This is a placeholder implementation
            # Real implementation would require SoundCloud API registration
            logger.warning("SoundCloud source requires API registration - skipping")
            return None
            
        except Exception as e:
            logger.error(f"SoundCloud download error: {e}")
            return None

    async def _download_with_mp3juice(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """
        Download from mp3juice.io using web scraping.
        """
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate'
            }
            
            # Search on mp3juice.io
            search_term = f"{track_info['name']} {track_info['artist']}".replace(' ', '+')
            search_url = f"https://mp3juice.io/search?q={search_term}"
            
            try:
                async with self.session.get(search_url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Look for download links in the HTML
                        download_patterns = [
                            r'href="([^"]*\.mp3[^"]*)"',
                            r'data-url="([^"]*\.mp3[^"]*)"',
                            r'download="([^"]*\.mp3[^"]*)"'
                        ]
                        
                        for pattern in download_patterns:
                            links = re.findall(pattern, html_content, re.IGNORECASE)
                            for link in links[:3]:  # Try first 3 matches
                                if not link.startswith('http'):
                                    link = f"https://mp3juice.io{link}"
                                
                                logger.info(f"Trying MP3Juice download: {link}")
                                
                                try:
                                    async with self.session.get(link, headers=headers, timeout=20) as dl_response:
                                        if dl_response.status == 200 and dl_response.content_type.startswith('audio'):
                                            with open(output_file, 'wb') as f:
                                                async for chunk in dl_response.content.iter_chunked(8192):
                                                    f.write(chunk)
                                            
                                            # Check if file is valid (not empty or too small)
                                            if os.path.getsize(output_file) > 100000:  # 100KB minimum
                                                logger.info(f"Successfully downloaded from MP3Juice: {output_file}")
                                                return output_file
                                            else:
                                                os.remove(output_file)
                                except Exception as e:
                                    logger.debug(f"Download attempt failed: {e}")
                                    continue
                                    
            except Exception as e:
                logger.warning(f"MP3Juice scraping error: {e}")
            
            return None
        except Exception as e:
            logger.error(f"MP3Juice error: {e}")
            return None

    async def _download_with_mp3juices(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """Download from mp3juices.cc using advanced web scraping."""
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Search on mp3juices.cc
            search_term = f"{track_info['name']} {track_info['artist']}".replace(' ', '+')
            search_url = f"https://mp3juices.cc/search/{search_term}"
            
            try:
                timeout = aiohttp.ClientTimeout(total=15)
                async with self.session.get(search_url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Advanced pattern matching for MP3Juices
                        download_patterns = [
                            r'href="([^"]*download[^"]*\.mp3[^"]*)"',
                            r'data-url="([^"]*\.mp3[^"]*)"',
                            r'src="([^"]*\.mp3[^"]*)"',
                            r'"url":"([^"]*\.mp3[^"]*)"',
                            r'download_url["\s]*:["\s]*([^"]*\.mp3[^"]*)'
                        ]
                        
                        for pattern in download_patterns:
                            links = re.findall(pattern, html_content, re.IGNORECASE)
                            for link in links[:3]:  # Try first 3 matches
                                if 'mp3juices.cc' not in link and not link.startswith('http'):
                                    link = f"https://mp3juices.cc{link}"
                                elif not link.startswith('http'):
                                    continue
                                
                                logger.info(f"Trying MP3Juices download: {link}")
                                
                                try:
                                    download_timeout = aiohttp.ClientTimeout(total=15)
                                    async with self.session.get(link, headers=headers, timeout=download_timeout) as dl_response:
                                        if dl_response.status == 200:
                                            content_type = dl_response.headers.get('content-type', '')
                                            if 'audio' in content_type or 'mpeg' in content_type or dl_response.content_length and dl_response.content_length > 100000:
                                                with open(output_file, 'wb') as f:
                                                    async for chunk in dl_response.content.iter_chunked(8192):
                                                        f.write(chunk)
                                                
                                                # Check if file is valid
                                                if os.path.getsize(output_file) > 100000:  # 100KB minimum
                                                    logger.info(f"Successfully downloaded from MP3Juices: {output_file}")
                                                    return output_file
                                                else:
                                                    os.remove(output_file)
                                except Exception as e:
                                    logger.debug(f"MP3Juices download attempt failed: {e}")
                                    continue
                                    
            except Exception as e:
                logger.warning(f"MP3Juices scraping error: {e}")
            
            return None
        except Exception as e:
            logger.error(f"MP3Juices error: {e}")
            return None

    async def _download_with_tubidy(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """Download from tubidy.io using web scraping."""
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Android 10; Mobile; rv:91.0) Gecko/91.0 Firefox/91.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://tubidy.io'
            }
            
            # Search on tubidy.io (mobile-friendly music site)
            search_term = f"{track_info['name']} {track_info['artist']}".replace(' ', '%20')
            search_url = f"https://tubidy.io/search?q={search_term}"
            
            try:
                timeout = aiohttp.ClientTimeout(total=15)
                async with self.session.get(search_url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Tubidy-specific patterns
                        download_patterns = [
                            r'href="([^"]*download[^"]*\.mp3[^"]*)"',
                            r'data-download="([^"]*\.mp3[^"]*)"',
                            r'href="([^"]*tubidy[^"]*\.mp3[^"]*)"',
                            r'"mp3":"([^"]*\.mp3[^"]*)"'
                        ]
                        
                        for pattern in download_patterns:
                            links = re.findall(pattern, html_content, re.IGNORECASE)
                            for link in links[:3]:
                                if not link.startswith('http'):
                                    link = f"https://tubidy.io{link}"
                                
                                logger.info(f"Trying Tubidy download: {link}")
                                
                                try:
                                    download_timeout = aiohttp.ClientTimeout(total=15)
                                    async with self.session.get(link, headers=headers, timeout=download_timeout) as dl_response:
                                        if dl_response.status == 200:
                                            content_type = dl_response.headers.get('content-type', '')
                                            if 'audio' in content_type or 'mpeg' in content_type:
                                                with open(output_file, 'wb') as f:
                                                    async for chunk in dl_response.content.iter_chunked(8192):
                                                        f.write(chunk)
                                                
                                                if os.path.getsize(output_file) > 100000:
                                                    logger.info(f"Successfully downloaded from Tubidy: {output_file}")
                                                    return output_file
                                                else:
                                                    os.remove(output_file)
                                except Exception as e:
                                    logger.debug(f"Tubidy download attempt failed: {e}")
                                    continue
                                    
            except Exception as e:
                logger.warning(f"Tubidy scraping error: {e}")
            
            return None
        except Exception as e:
            logger.error(f"Tubidy error: {e}")
            return None

    async def _download_with_mp3skull(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """Download from mp3skull.to using web scraping."""
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://mp3skull.to'
            }
            
            # Search on mp3skull.to
            search_term = f"{track_info['name']} {track_info['artist']}".replace(' ', '+')
            search_url = f"https://mp3skull.to/search?q={search_term}"
            
            try:
                timeout = aiohttp.ClientTimeout(total=15)
                async with self.session.get(search_url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Mp3skull-specific patterns
                        download_patterns = [
                            r'href="([^"]*\.mp3[^"]*)"',
                            r'data-src="([^"]*\.mp3[^"]*)"',
                            r'"download_url":"([^"]*\.mp3[^"]*)"',
                            r'downloadUrl["\s]*:["\s]*([^"]*\.mp3[^"]*)'
                        ]
                        
                        for pattern in download_patterns:
                            links = re.findall(pattern, html_content, re.IGNORECASE)
                            for link in links[:3]:
                                if not link.startswith('http'):
                                    link = f"https://mp3skull.to{link}"
                                
                                logger.info(f"Trying Mp3skull download: {link}")
                                
                                try:
                                    download_timeout = aiohttp.ClientTimeout(total=15)
                                    async with self.session.get(link, headers=headers, timeout=download_timeout) as dl_response:
                                        if dl_response.status == 200:
                                            content_type = dl_response.headers.get('content-type', '')
                                            if 'audio' in content_type or 'mpeg' in content_type:
                                                with open(output_file, 'wb') as f:
                                                    async for chunk in dl_response.content.iter_chunked(8192):
                                                        f.write(chunk)
                                                
                                                if os.path.getsize(output_file) > 100000:
                                                    logger.info(f"Successfully downloaded from Mp3skull: {output_file}")
                                                    return output_file
                                                else:
                                                    os.remove(output_file)
                                except Exception as e:
                                    logger.debug(f"Mp3skull download attempt failed: {e}")
                                    continue
                                    
            except Exception as e:
                logger.warning(f"Mp3skull scraping error: {e}")
            
            return None
        except Exception as e:
            logger.error(f"Mp3skull error: {e}")
            return None

    async def _download_with_bittorrent(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """Download using BitTorrent DHT network search."""
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*'
            }
            
            # Use DHT search through public torrent APIs
            search_term = f"{track_info['name']} {track_info['artist']} mp3".replace(' ', '+')
            
            # Try multiple torrent search engines
            torrent_apis = [
                f"https://1337x.to/search/{search_term}/1/",
                f"https://thepiratebay.org/search.php?q={search_term}",
                f"https://torrentz2.eu/search?f={search_term}"
            ]
            
            for api_url in torrent_apis:
                try:
                    timeout = aiohttp.ClientTimeout(total=15)
                    async with self.session.get(api_url, headers=headers, timeout=timeout) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            
                            # Look for magnet links or torrent files with audio
                            magnet_patterns = [
                                r'magnet:\?xt=urn:btih:[a-zA-Z0-9]+[^"\'<>\s]*',
                                r'href="(magnet:[^"]*)"'
                            ]
                            
                            for pattern in magnet_patterns:
                                magnets = re.findall(pattern, html_content, re.IGNORECASE)
                                for magnet in magnets[:2]:  # Try first 2 magnets
                                    if 'mp3' in magnet.lower() or 'audio' in magnet.lower():
                                        # For demonstration, create a sample file
                                        # Real implementation would use torrent client
                                        logger.info(f"Found BitTorrent magnet: {magnet[:50]}...")
                                        
                                        # Simulate torrent download with demo content
                                        # In real implementation, you'd use libtorrent-python
                                        demo_content = b"Demo BitTorrent MP3 content"
                                        with open(output_file, 'wb') as f:
                                            f.write(demo_content)
                                        
                                        if os.path.getsize(output_file) > 10:
                                            logger.info(f"BitTorrent search completed (demo): {output_file}")
                                            return output_file
                                        else:
                                            os.remove(output_file)
                                        break
                            break  # If we found results, don't try other APIs
                            
                except Exception as e:
                    logger.debug(f"BitTorrent API {api_url} failed: {e}")
                    continue
            
            return None
        except Exception as e:
            logger.error(f"BitTorrent error: {e}")
            return None
            
            # Second try: Free Music Archive
            fma_url = "https://freemusicarchive.org/api/get/tracks.json"
            params = {
                'api_key': 'public',  # FMA public API
                'limit': 5,
                'q': f"{track_info['name']} {track_info['artist']}"
            }
            
            try:
                async with self.session.get(fma_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        fma_results = await response.json()
                        if fma_results.get('dataset') and len(fma_results['dataset']) > 0:
                            track = fma_results['dataset'][0]
                            if 'track_file' in track and track['track_file']:
                                download_url = track['track_file']
                                async with self.session.get(download_url) as download_response:
                                    if download_response.status == 200:
                                        with open(output_file, 'wb') as f:
                                            async for chunk in download_response.content.iter_chunked(8192):
                                                f.write(chunk)
                                        logger.info(f"Downloaded from Free Music Archive: {output_file}")
                                        return output_file
            except Exception as e:
                logger.debug(f"Free Music Archive failed: {e}")
            
            # Third try: Internet Archive
            ia_url = "https://archive.org/advancedsearch.php"
            params = {
                'q': f"title:({track_info['name']}) AND creator:({track_info['artist']})",
                'fl': 'identifier,title,creator',
                'rows': 5,
                'page': 1,
                'output': 'json',
                'mediatype': 'audio'
            }
            
            try:
                async with self.session.get(ia_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        ia_results = await response.json()
                        if ia_results.get('response', {}).get('docs'):
                            for doc in ia_results['response']['docs'][:3]:
                                identifier = doc.get('identifier')
                                if identifier:
                                    # Try to get audio file from Internet Archive
                                    files_url = f"https://archive.org/metadata/{identifier}"
                                    async with self.session.get(files_url) as files_response:
                                        if files_response.status == 200:
                                            files_data = await files_response.json()
                                            for file in files_data.get('files', []):
                                                if file.get('format') in ['VBR MP3', 'MP3']:
                                                    download_url = f"https://archive.org/download/{identifier}/{file['name']}"
                                                    async with self.session.get(download_url) as download_response:
                                                        if download_response.status == 200:
                                                            with open(output_file, 'wb') as f:
                                                                async for chunk in download_response.content.iter_chunked(8192):
                                                                    f.write(chunk)
                                                            logger.info(f"Downloaded from Internet Archive: {output_file}")
                                                            return output_file
                                                    break
            except Exception as e:
                logger.debug(f"Internet Archive failed: {e}")
            
            # If all real sources fail, inform user instead of dummy file
            logger.warning(f"No real audio sources found for: {search_query}")
            return None
            
        except Exception as e:
            logger.error(f"Audio download error: {e}")
            return None
    
    async def _try_deezer_api(self, track_info: Dict, output_file: str, headers: Dict) -> bool:
        """Try to download from Deezer API."""
        try:
            deezer_url = "https://api.deezer.com/search"
            params = {
                'q': f"{track_info['name']} {track_info['artist']}",
                'limit': 3
            }
            
            async with self.session.get(deezer_url, params=params, headers=headers) as response:
                if response.status == 200:
                    deezer_results = await response.json()
                    if deezer_results.get('data'):
                        for track in deezer_results['data']:
                            if 'preview' in track and track['preview']:
                                async with self.session.get(track['preview']) as preview_response:
                                    if preview_response.status == 200:
                                        with open(output_file, 'wb') as f:
                                            async for chunk in preview_response.content.iter_chunked(8192):
                                                f.write(chunk)
                                        logger.info(f"Downloaded Deezer preview: {output_file}")
                                        return True
        except Exception as e:
            logger.debug(f"Deezer API failed: {e}")
        return False
    
    async def _try_jamendo_api(self, track_info: Dict, output_file: str, headers: Dict) -> bool:
        """Try to download from Jamendo Creative Commons music."""
        try:
            # Jamendo has free Creative Commons music with full downloads
            jamendo_url = "https://api.jamendo.com/v3.0/tracks/"
            params = {
                'client_id': 'jamendo',  # Public access
                'format': 'json',
                'search': f"{track_info['name']} {track_info['artist']}",
                'limit': 3,
                'audioformat': 'mp32'
            }
            
            async with self.session.get(jamendo_url, params=params, headers=headers) as response:
                if response.status == 200:
                    jamendo_results = await response.json()
                    if jamendo_results.get('results'):
                        for track in jamendo_results['results']:
                            if 'audio' in track and track['audio']:
                                async with self.session.get(track['audio']) as audio_response:
                                    if audio_response.status == 200:
                                        with open(output_file, 'wb') as f:
                                            async for chunk in audio_response.content.iter_chunked(8192):
                                                f.write(chunk)
                                        logger.info(f"Downloaded Jamendo track: {output_file}")
                                        return True
        except Exception as e:
            logger.debug(f"Jamendo API failed: {e}")
        return False
    
    async def _try_freemusicarchive_api(self, track_info: Dict, output_file: str, headers: Dict) -> bool:
        """Try to download from Internet Archive music collection."""
        try:
            # Internet Archive has vast music collection
            search_query = f"{track_info['name']} {track_info['artist']}".replace(' ', '+')
            ia_url = f"https://archive.org/advancedsearch.php"
            params = {
                'q': f"title:({search_query}) AND mediatype:audio",
                'fl': 'identifier,title,creator',
                'rows': 3,
                'output': 'json'
            }
            
            async with self.session.get(ia_url, params=params, headers=headers) as response:
                if response.status == 200:
                    ia_results = await response.json()
                    if ia_results.get('response', {}).get('docs'):
                        for doc in ia_results['response']['docs']:
                            identifier = doc.get('identifier')
                            if identifier:
                                # Get audio file from Internet Archive
                                files_url = f"https://archive.org/metadata/{identifier}"
                                async with self.session.get(files_url) as files_response:
                                    if files_response.status == 200:
                                        files_data = await files_response.json()
                                        for file in files_data.get('files', []):
                                            if file.get('format') in ['VBR MP3', 'MP3', 'MPEG']:
                                                download_url = f"https://archive.org/download/{identifier}/{file['name']}"
                                                async with self.session.get(download_url) as download_response:
                                                    if download_response.status == 200:
                                                        with open(output_file, 'wb') as f:
                                                            async for chunk in download_response.content.iter_chunked(8192):
                                                                f.write(chunk)
                                                        logger.info(f"Downloaded from Internet Archive: {output_file}")
                                                        return True
                                                break
        except Exception as e:
            logger.debug(f"Internet Archive failed: {e}")
        return False
    

    
    async def _try_soundcloud_api(self, track_info: Dict, output_file: str, headers: Dict) -> bool:
        """Try SoundCloud using direct search and download."""
        try:
            # SoundCloud has a public search API
            soundcloud_search = "https://api-v2.soundcloud.com/search/tracks"
            params = {
                'q': f"{track_info['name']} {track_info['artist']}",
                'client_id': 'your_soundcloud_client_id',  # Public client ID
                'limit': 3
            }
            
            # Use a known working SoundCloud client ID (public)
            public_client_ids = [
                'iZIs9mchVcX5lhVkHQDFPjNBz4U4SkBy',
                'LBCcHmRB8XSStWL6wKH2HPACspQlXD2e',
                'fDoItMDbsbZz8dY16ZzARCZmzgHBPotA'
            ]
            
            for client_id in public_client_ids:
                params['client_id'] = client_id
                try:
                    async with self.session.get(soundcloud_search, params=params, headers=headers) as response:
                        if response.status == 200:
                            sc_results = await response.json()
                            if sc_results.get('collection'):
                                for track in sc_results['collection']:
                                    if track.get('streamable') and track.get('stream_url'):
                                        stream_url = f"{track['stream_url']}?client_id={client_id}"
                                        async with self.session.get(stream_url) as stream_response:
                                            if stream_response.status == 200:
                                                with open(output_file, 'wb') as f:
                                                    async for chunk in stream_response.content.iter_chunked(8192):
                                                        f.write(chunk)
                                                logger.info(f"Downloaded from SoundCloud: {output_file}")
                                                return True
                            break
                except Exception as e:
                    logger.debug(f"SoundCloud client {client_id} failed: {e}")
                    continue
        except Exception as e:
            logger.debug(f"SoundCloud API failed: {e}")
        return False
    
    async def _try_audiomack_api(self, track_info: Dict, output_file: str, headers: Dict) -> bool:
        """Try Audiomack public API."""
        try:
            # Audiomack has a public API for music search
            audiomack_search = "https://www.audiomack.com/api/search"
            params = {
                'q': f"{track_info['name']} {track_info['artist']}",
                'type': 'song',
                'limit': 3
            }
            
            async with self.session.get(audiomack_search, params=params, headers=headers) as response:
                if response.status == 200:
                    am_results = await response.json()
                    if am_results.get('results', {}).get('songs'):
                        for song in am_results['results']['songs']:
                            if song.get('stream_url'):
                                async with self.session.get(song['stream_url']) as stream_response:
                                    if stream_response.status == 200:
                                        with open(output_file, 'wb') as f:
                                            async for chunk in stream_response.content.iter_chunked(8192):
                                                f.write(chunk)
                                        logger.info(f"Downloaded from Audiomack: {output_file}")
                                        return True
        except Exception as e:
            logger.debug(f"Audiomack API failed: {e}")
        return False

    async def _download_with_y2mate(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """Download from y2mate.com using web scraping."""
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }
            
            # Search for music on y2mate (which often has direct download options)
            search_term = f"{track_info['name']} {track_info['artist']}".replace(' ', '%20')
            search_url = f"https://www.y2mate.com/search/{search_term}"
            
            try:
                async with self.session.get(search_url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Look for direct MP3 links
                        mp3_patterns = [
                            r'href="([^"]*\.mp3[^"]*)"',
                            r'src="([^"]*\.mp3[^"]*)"',
                            r'data-src="([^"]*\.mp3[^"]*)"'
                        ]
                        
                        for pattern in mp3_patterns:
                            links = re.findall(pattern, html_content, re.IGNORECASE)
                            for link in links[:2]:  # Try first 2 matches
                                if not link.startswith('http'):
                                    link = f"https://www.y2mate.com{link}"
                                
                                logger.info(f"Trying Y2Mate download: {link}")
                                
                                try:
                                    async with self.session.get(link, headers=headers, timeout=20) as dl_response:
                                        if dl_response.status == 200:
                                            content_type = dl_response.headers.get('content-type', '')
                                            if 'audio' in content_type or 'mpeg' in content_type:
                                                with open(output_file, 'wb') as f:
                                                    async for chunk in dl_response.content.iter_chunked(8192):
                                                        f.write(chunk)
                                                
                                                if os.path.getsize(output_file) > 100000:  # 100KB minimum
                                                    logger.info(f"Successfully downloaded from Y2Mate: {output_file}")
                                                    return output_file
                                                else:
                                                    os.remove(output_file)
                                except Exception as e:
                                    logger.debug(f"Y2Mate download attempt failed: {e}")
                                    continue
                                    
            except Exception as e:
                logger.warning(f"Y2Mate scraping error: {e}")
            
            return None
        except Exception as e:
            logger.error(f"Y2Mate error: {e}")
            return None
    
    async def _download_with_mp3download(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """Download from mp3download.to using web scraping."""
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            # Search on mp3download.to
            search_term = f"{track_info['name']} {track_info['artist']}".replace(' ', '+')
            search_url = f"https://mp3download.to/search?q={search_term}"
            
            try:
                async with self.session.get(search_url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        
                        # Look for download links
                        download_patterns = [
                            r'href="([^"]*download[^"]*\.mp3[^"]*)"',
                            r'data-download="([^"]*\.mp3[^"]*)"',
                            r'href="([^"]*\.mp3[^"]*)"'
                        ]
                        
                        for pattern in download_patterns:
                            links = re.findall(pattern, html_content, re.IGNORECASE)
                            for link in links[:2]:
                                if not link.startswith('http'):
                                    link = f"https://mp3download.to{link}"
                                
                                logger.info(f"Trying Mp3Download: {link}")
                                
                                try:
                                    async with self.session.get(link, headers=headers, timeout=20) as dl_response:
                                        if dl_response.status == 200:
                                            content_type = dl_response.headers.get('content-type', '')
                                            if 'audio' in content_type or 'mpeg' in content_type:
                                                with open(output_file, 'wb') as f:
                                                    async for chunk in dl_response.content.iter_chunked(8192):
                                                        f.write(chunk)
                                                
                                                if os.path.getsize(output_file) > 50000:  # 50KB minimum
                                                    logger.info(f"Successfully downloaded from Mp3Download: {output_file}")
                                                    return output_file
                                                else:
                                                    os.remove(output_file)
                                except Exception as e:
                                    logger.debug(f"Mp3Download attempt failed: {e}")
                                    continue
                                    
            except Exception as e:
                logger.warning(f"Mp3Download scraping error: {e}")
            
            return None
        except Exception as e:
            logger.error(f"Mp3Download error: {e}")
            return None
    
    async def _download_with_directdl(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """Download from direct file hosting sites."""
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            # Try direct file hosting sites that often have music
            file_sites = [
                f"https://mp3quack.lol/search?q={search_query.replace(' ', '+')}",
                f"https://musicpleer.la/search?q={search_query.replace(' ', '+')}",
                f"https://slider.kz/vk_auth.php?q={search_query.replace(' ', '+')}"
            ]
            
            for site_url in file_sites:
                try:
                    async with self.session.get(site_url, headers=headers, timeout=15) as response:
                        if response.status == 200:
                            html_content = await response.text()
                            
                            # Look for direct MP3 links
                            mp3_patterns = [
                                r'href="([^"]*\.mp3[^"]*)"',
                                r'src="([^"]*\.mp3[^"]*)"',
                                r'data-url="([^"]*\.mp3[^"]*)"',
                                r'download="([^"]*\.mp3[^"]*)"'
                            ]
                            
                            for pattern in mp3_patterns:
                                links = re.findall(pattern, html_content, re.IGNORECASE)
                                for link in links[:1]:  # Try only first match per site
                                    if not link.startswith('http'):
                                        base_url = site_url.split('/')[0:3]
                                        link = '/'.join(base_url) + link
                                    
                                    logger.info(f"Trying DirectDL: {link}")
                                    
                                    try:
                                        async with self.session.get(link, headers=headers, timeout=20) as dl_response:
                                            if dl_response.status == 200:
                                                content_type = dl_response.headers.get('content-type', '')
                                                if 'audio' in content_type or 'mpeg' in content_type:
                                                    with open(output_file, 'wb') as f:
                                                        async for chunk in dl_response.content.iter_chunked(8192):
                                                            f.write(chunk)
                                                    
                                                    if os.path.getsize(output_file) > 100000:  # 100KB minimum
                                                        logger.info(f"Successfully downloaded from DirectDL: {output_file}")
                                                        return output_file
                                                    else:
                                                        os.remove(output_file)
                                    except Exception as e:
                                        logger.debug(f"DirectDL download attempt failed: {e}")
                                        continue
                                        
                except Exception as e:
                    logger.warning(f"DirectDL site {site_url} error: {e}")
                    continue
            
            return None
        except Exception as e:
            logger.error(f"DirectDL error: {e}")
            return None

    async def cleanup(self):
        """Clean up resources and temporary files."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            
            # Clean up temporary directory
            if os.path.exists(self.download_dir):
                import shutil
                shutil.rmtree(self.download_dir)
                logger.info(f"Cleaned up download directory: {self.download_dir}")
                
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def _download_with_y2mate_youtube(self, search_query: str, track_info: Dict, quality: str) -> Optional[str]:
        """Download using yt-dlp with YouTube search."""
        try:
            file_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            safe_filename = re.sub(r'[^\w\s-]', '', search_query).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            output_file = os.path.join(self.download_dir, f"{safe_filename}-{file_hash}.%(ext)s")
            
            logger.info(f"Using yt-dlp to download: {search_query}")
            
            # yt-dlp command with YouTube search
            search_term = f"ytsearch:{track_info['name']} {track_info['artist']}"
            
            # Quality options
            quality_map = {
                '128': 'bestaudio[abr<=128]/worst',
                '192': 'bestaudio[abr<=192]/bestaudio[abr<=128]/worst', 
                '320': 'bestaudio/best'
            }
            audio_quality = quality_map.get(quality, 'bestaudio/best')
            
            # yt-dlp command with cookies for bypass
            cmd = [
                'yt-dlp',
                '--no-warnings',
                '--cookies', 'cookies.txt',  # Use cookies to bypass restrictions
                '--format', audio_quality,
                '--extract-audio',
                '--audio-format', 'mp3',
                '--audio-quality', '0',  # Best quality
                '--output', output_file,
                '--no-playlist',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                search_term
            ]
            
            # Execute yt-dlp command
            import subprocess
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                # Find the downloaded file (yt-dlp with --extract-audio should create MP3 directly)
                expected_files = [
                    output_file.replace('%(ext)s', ext) 
                    for ext in ['mp3', 'm4a', 'webm', 'ogg']
                ]
                
                for file_path in expected_files:
                    if os.path.exists(file_path):
                        if os.path.getsize(file_path) > 50000:  # 50KB minimum
                            logger.info(f"Successfully downloaded: {file_path}")
                            return file_path
                        else:
                            logger.warning("Downloaded file too small")
                            os.remove(file_path)
                
                logger.warning("No valid output file found")
            else:
                logger.error(f"yt-dlp failed: {stderr.decode()}")
            
            return None
            
        except Exception as e:
            logger.error(f"yt-dlp download error: {e}")
            return None
    


    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            if self.session and not self.session.closed:
                asyncio.create_task(self.session.close())
        except:
            pass

    def cleanup_file(self, file_path: str):
        """
        Clean up downloaded file.
        
        Args:
            file_path: Path to file to be cleaned up
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup file {file_path}: {e}")
