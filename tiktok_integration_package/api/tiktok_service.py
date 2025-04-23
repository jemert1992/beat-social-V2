"""
TikTok Service Module

This module provides a high-level service for posting content to TikTok.
It uses the TikTokAPI client for direct API access.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from .tiktok_api import TikTokAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TikTokService:
    """
    Service for posting content to TikTok.
    """
    
    def __init__(self):
        """
        Initialize the TikTok service.
        """
        self.api = TikTokAPI()
    
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
        try:
            logger.info(f"Posting video to TikTok: {video_url}")
            response = self.api.post_video(video_url, caption, hashtags)
            logger.info(f"Successfully posted video to TikTok: {response}")
            return {
                "success": True,
                "message": "Video posted successfully",
                "data": response
            }
        except Exception as e:
            logger.error(f"Failed to post video to TikTok: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to post video: {str(e)}",
                "error": str(e)
            }
    
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
        try:
            logger.info(f"Uploading and posting video file to TikTok: {video_path}")
            response = self.api.post_video_file(video_path, caption, hashtags)
            logger.info(f"Successfully posted video file to TikTok: {response}")
            return {
                "success": True,
                "message": "Video posted successfully",
                "data": response
            }
        except Exception as e:
            logger.error(f"Failed to post video file to TikTok: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to post video: {str(e)}",
                "error": str(e)
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the authenticated TikTok account.
        
        Returns:
            Dict[str, Any]: Account information
        """
        try:
            logger.info("Getting TikTok account information")
            response = self.api.get_account_info()
            logger.info(f"Successfully retrieved TikTok account information: {response}")
            return {
                "success": True,
                "message": "Account information retrieved successfully",
                "data": response
            }
        except Exception as e:
            logger.error(f"Failed to get TikTok account information: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to get account information: {str(e)}",
                "error": str(e)
            }
