"""
Integration module for TikTok API Client

This module integrates the TikTok API client with the main application.
"""

import os
import logging
from api.tiktok_client import TikTokClient
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tiktok_integration")

class TikTokIntegration:
    """Integration class for TikTok API client."""
    
    def __init__(self):
        """Initialize the TikTok integration."""
        self.client = TikTokClient()
        self.is_initialized = False
        
    def initialize(self, access_token=None, open_id=None):
        """
        Initialize the TikTok client with credentials.
        
        Args:
            access_token: Optional access token (if not provided, must be set later)
            open_id: Optional open ID (if not provided, must be set later)
        
        Returns:
            bool: Whether initialization was successful
        """
        try:
            # Check if API key and secret are available
            api_key = os.environ.get("TIKTOK_API_KEY", "")
            api_secret = os.environ.get("SOCIAL_MEDIA_TOKEN", "")
            
            if not api_key or not api_secret:
                logger.error("Missing API credentials. Ensure TIKTOK_API_KEY and SOCIAL_MEDIA_TOKEN are set.")
                return False
            
            # Set credentials if provided
            if access_token and open_id:
                self.client.set_credentials(access_token, open_id)
                self.is_initialized = True
                logger.info("TikTok integration initialized successfully")
                return True
            else:
                logger.warning("Access token and open ID not provided. Call set_user_credentials() before posting.")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize TikTok integration: {str(e)}")
            return False
    
    def set_user_credentials(self, access_token, open_id):
        """
        Set user credentials for the TikTok client.
        
        Args:
            access_token: The access token for the TikTok API
            open_id: The open ID of the TikTok user
            
        Returns:
            bool: Whether setting credentials was successful
        """
        try:
            self.client.set_credentials(access_token, open_id)
            self.is_initialized = True
            logger.info("User credentials set successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set user credentials: {str(e)}")
            return False
    
    def get_account_info(self):
        """
        Get information about the TikTok account.
        
        Returns:
            dict: Account information or error message
        """
        if not self.is_initialized:
            return {"error": "Client not initialized. Call initialize() or set_user_credentials() first."}
        
        try:
            creator_info = self.client.get_creator_info()
            return {
                "username": creator_info.get("creator_username", ""),
                "nickname": creator_info.get("creator_nickname", ""),
                "avatar_url": creator_info.get("creator_avatar_url", ""),
                "privacy_options": creator_info.get("privacy_level_options", []),
                "max_video_duration": creator_info.get("max_video_post_duration_sec", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            return {"error": str(e)}
    
    def post_video(self, video_source, caption, privacy_level="PUBLIC_TO_EVERYONE", 
                  disable_comments=False, disable_duet=False, disable_stitch=False,
                  wait_for_completion=True):
        """
        Post a video to TikTok.
        
        Args:
            video_source: Path to local video file or URL
            caption: Caption for the video
            privacy_level: Privacy setting
            disable_comments: Whether to disable comments
            disable_duet: Whether to disable duets
            disable_stitch: Whether to disable stitches
            wait_for_completion: Whether to wait for the post to complete
            
        Returns:
            dict: Post result information
        """
        if not self.is_initialized:
            return {"error": "Client not initialized. Call initialize() or set_user_credentials() first."}
        
        try:
            # Determine if source is URL or file path
            is_url = video_source.startswith(('http://', 'https://'))
            
            # Post the video
            if is_url:
                result = self.client.post_video_from_url(
                    video_url=video_source,
                    title=caption,
                    privacy_level=privacy_level,
                    disable_comment=disable_comments,
                    disable_duet=disable_duet,
                    disable_stitch=disable_stitch
                )
            else:
                result = self.client.post_video_from_file(
                    video_path=video_source,
                    title=caption,
                    privacy_level=privacy_level,
                    disable_comment=disable_comments,
                    disable_duet=disable_duet,
                    disable_stitch=disable_stitch
                )
            
            publish_id = result.get("publish_id")
            
            if not publish_id:
                return {"error": "Failed to get publish_id from response", "details": result}
            
            # Wait for completion if requested
            if wait_for_completion:
                final_status = self.client.wait_for_post_completion(publish_id)
                
                if final_status.get("status") == "PUBLISH_SUCCESS":
                    return {
                        "success": True,
                        "publish_id": publish_id,
                        "share_url": final_status.get("share_url", ""),
                        "status": "completed",
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {
                        "success": False,
                        "publish_id": publish_id,
                        "status": final_status.get("status", "unknown"),
                        "error": final_status.get("error_code", ""),
                        "error_message": final_status.get("error_message", ""),
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                return {
                    "success": True,
                    "publish_id": publish_id,
                    "status": "processing",
                    "message": "Video post initiated. Check status later with get_post_status().",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to post video: {str(e)}")
            return {"error": str(e)}
    
    def get_post_status(self, publish_id):
        """
        Get the status of a post.
        
        Args:
            publish_id: The publish ID returned from post_video
            
        Returns:
            dict: Status information
        """
        if not self.is_initialized:
            return {"error": "Client not initialized. Call initialize() or set_user_credentials() first."}
        
        try:
            status_data = self.client.get_post_status(publish_id)
            
            return {
                "publish_id": publish_id,
                "status": status_data.get("status", "unknown"),
                "share_url": status_data.get("share_url", ""),
                "create_time": status_data.get("create_time", ""),
                "error_code": status_data.get("error_code", ""),
                "error_message": status_data.get("error_message", ""),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get post status: {str(e)}")
            return {"error": str(e)}
