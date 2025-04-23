"""
TikTok API Integration Module

This module provides direct API access to TikTok without requiring OAuth.
It uses API keys stored in environment variables for authentication.
"""

import os
import requests
import time
import json
import logging
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TikTokAPI:
    """
    TikTok API client for direct API access using API keys.
    """
    
    BASE_URL = "https://open.tiktokapis.com/v2"
    
    def __init__(self):
        """
        Initialize the TikTok API client with credentials from environment variables.
        """
        self.api_key = os.environ.get("TIKTOK_API_KEY", "")
        self.api_secret = os.environ.get("SOCIAL_MEDIA_TOKEN", "")
        
        if not self.api_key or not self.api_secret:
            logger.warning("TikTok API credentials not found in environment variables")
        
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Generate headers for API requests.
        
        Returns:
            Dict[str, str]: Headers for API requests
        """
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, 
                     params: Optional[Dict[str, Any]] = None, retries: int = 3) -> Dict[str, Any]:
        """
        Make a request to the TikTok API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            retries: Number of retry attempts
            
        Returns:
            Dict[str, Any]: API response
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        # Add API secret to the request data
        if data is None:
            data = {}
        data["api_secret"] = self.api_secret
        
        attempt = 0
        while attempt < retries:
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if method.upper() in ["POST", "PUT", "PATCH"] else None,
                    params=params if method.upper() == "GET" else None,
                    timeout=30
                )
                
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt >= retries:
                    logger.error(f"Failed to make request after {retries} attempts: {str(e)}")
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"Request failed, retrying in {wait_time} seconds... ({attempt}/{retries})")
                time.sleep(wait_time)
    
    def post_video(self, video_url: str, caption: str = "", hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Post a video to TikTok using a video URL.
        
        Args:
            video_url: URL of the video to post
            caption: Caption for the video
            hashtags: List of hashtags to include
            
        Returns:
            Dict[str, Any]: API response
        """
        if hashtags is None:
            hashtags = []
        
        # Format hashtags
        hashtag_str = " ".join([f"#{tag}" for tag in hashtags])
        full_caption = f"{caption} {hashtag_str}".strip()
        
        data = {
            "video_url": video_url,
            "caption": full_caption,
            "post_info": {
                "title": full_caption[:80],  # TikTok typically limits titles
                "disable_comment": False,
                "disable_duet": False,
                "disable_stitch": False,
            }
        }
        
        logger.info(f"Posting video to TikTok: {video_url}")
        return self._make_request("POST", "/post/publish/video/url", data=data)
    
    def post_video_file(self, video_path: str, caption: str = "", hashtags: List[str] = None) -> Dict[str, Any]:
        """
        Upload and post a video file to TikTok.
        
        Args:
            video_path: Path to the video file
            caption: Caption for the video
            hashtags: List of hashtags to include
            
        Returns:
            Dict[str, Any]: API response
        """
        if hashtags is None:
            hashtags = []
        
        # First, upload the video file to get a URL
        upload_url = self._upload_video(video_path)
        
        # Then post using the URL
        return self.post_video(upload_url, caption, hashtags)
    
    def _upload_video(self, video_path: str) -> str:
        """
        Upload a video file to TikTok's servers.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            str: URL of the uploaded video
        """
        # Prepare upload request
        upload_data = {
            "source": "FILE_UPLOAD",
            "content_type": "video/mp4",
            "filename": os.path.basename(video_path)
        }
        
        # Get upload URL
        upload_info = self._make_request("POST", "/post/publish/video/init", data=upload_data)
        
        # Upload the file
        with open(video_path, "rb") as video_file:
            files = {"file": (os.path.basename(video_path), video_file, "video/mp4")}
            upload_url = upload_info.get("upload_url")
            
            response = requests.post(upload_url, files=files)
            response.raise_for_status()
        
        return upload_info.get("video_url")
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated TikTok account.
        
        Returns:
            Dict[str, Any]: Account information
        """
        return self._make_request("GET", "/user/info")
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get the status of a posted video.
        
        Args:
            video_id: ID of the video
            
        Returns:
            Dict[str, Any]: Video status information
        """
        params = {"video_id": video_id}
        return self._make_request("GET", "/post/publish/status", params=params)
