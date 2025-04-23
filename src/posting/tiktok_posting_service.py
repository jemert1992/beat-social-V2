"""
TikTok Posting Service for Social Media Automation System

This module provides a service for posting content to TikTok using the TikTok API client.
"""

import os
import logging
import json
from datetime import datetime
from api.tiktok_integration import TikTokIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("posting.tiktok_posting_service")

class TikTokPostingService:
    """Service for posting content to TikTok."""
    
    def __init__(self, data_dir, config=None):
        """
        Initialize the TikTok posting service.
        
        Args:
            data_dir (str): Directory for storing data
            config (dict, optional): Configuration dictionary
        """
        self.data_dir = data_dir
        self.config = config
        self.tiktok_integration = TikTokIntegration()
        self.initialized = False
        self.posts_dir = os.path.join(data_dir, 'posts', 'tiktok')
        
        # Create posts directory if it doesn't exist
        os.makedirs(self.posts_dir, exist_ok=True)
        
        logger.info("TikTok Posting Service initialized")
    
    def initialize(self):
        """
        Initialize the TikTok API client with credentials from config.
        
        Returns:
            bool: Whether initialization was successful
        """
        if self.config is None:
            logger.error("Configuration not provided")
            return False
        
        try:
            # Check if API credentials are available
            tiktok_credentials = self.config.get("api_credentials", {}).get("tiktok", {})
            
            # Get access token and open ID (these would typically come from a user authentication flow)
            # For demo purposes, we're using placeholder values that would be replaced in production
            access_token = os.environ.get("TIKTOK_ACCESS_TOKEN", "demo_access_token")
            open_id = os.environ.get("TIKTOK_OPEN_ID", "demo_open_id")
            
            # Initialize the TikTok integration
            success = self.tiktok_integration.initialize(access_token, open_id)
            
            if success:
                self.initialized = True
                logger.info("TikTok Posting Service successfully initialized")
                return True
            else:
                logger.error("Failed to initialize TikTok integration")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing TikTok Posting Service: {str(e)}")
            return False
    
    def update_config(self, config):
        """
        Update the service configuration.
        
        Args:
            config (dict): New configuration dictionary
            
        Returns:
            bool: Whether update was successful
        """
        try:
            self.config = config
            
            # Re-initialize with new config if already initialized
            if self.initialized:
                return self.initialize()
            
            return True
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            return False
    
    def post_content(self, content_path, caption, hashtags=None, privacy_level="PUBLIC_TO_EVERYONE"):
        """
        Post content to TikTok.
        
        Args:
            content_path (str): Path to the content file
            caption (str): Caption for the post
            hashtags (list, optional): List of hashtags
            privacy_level (str): Privacy level for the post
            
        Returns:
            dict: Result of the posting operation
        """
        if not self.initialized:
            success = self.initialize()
            if not success:
                return {"success": False, "error": "Service not initialized"}
        
        try:
            # Format caption with hashtags
            full_caption = caption
            if hashtags:
                hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
                full_caption = f"{caption} {hashtag_text}"
            
            # Check if content exists
            if not os.path.exists(content_path):
                return {"success": False, "error": f"Content file not found: {content_path}"}
            
            # Determine if content is video or image based on file extension
            is_video = content_path.lower().endswith(('.mp4', '.mov', '.avi'))
            
            if not is_video:
                return {"success": False, "error": "Only video content is supported for TikTok posting"}
            
            # Post the video
            result = self.tiktok_integration.post_video(
                video_source=content_path,
                caption=full_caption,
                privacy_level=privacy_level,
                wait_for_completion=True
            )
            
            # Save posting record
            post_record = {
                "timestamp": datetime.now().isoformat(),
                "content_path": content_path,
                "caption": caption,
                "hashtags": hashtags,
                "privacy_level": privacy_level,
                "result": result
            }
            
            record_path = os.path.join(
                self.posts_dir, 
                f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(record_path, 'w') as f:
                json.dump(post_record, f, indent=4)
            
            logger.info(f"TikTok post record saved to {record_path}")
            
            if result.get("success"):
                logger.info(f"Successfully posted to TikTok: {result.get('share_url', '')}")
                return {
                    "success": True,
                    "post_id": result.get("publish_id"),
                    "share_url": result.get("share_url", ""),
                    "status": result.get("status"),
                    "record_path": record_path
                }
            else:
                logger.error(f"Failed to post to TikTok: {result.get('error', '')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "error_message": result.get("error_message", ""),
                    "record_path": record_path
                }
                
        except Exception as e:
            logger.error(f"Error posting content to TikTok: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_post_status(self, post_id):
        """
        Get the status of a TikTok post.
        
        Args:
            post_id (str): ID of the post
            
        Returns:
            dict: Status information
        """
        if not self.initialized:
            success = self.initialize()
            if not success:
                return {"success": False, "error": "Service not initialized"}
        
        try:
            status = self.tiktok_integration.get_post_status(post_id)
            
            return {
                "success": True,
                "post_id": post_id,
                "status": status.get("status"),
                "share_url": status.get("share_url", ""),
                "timestamp": status.get("timestamp")
            }
        except Exception as e:
            logger.error(f"Error getting post status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_account_info(self):
        """
        Get information about the TikTok account.
        
        Returns:
            dict: Account information
        """
        if not self.initialized:
            success = self.initialize()
            if not success:
                return {"success": False, "error": "Service not initialized"}
        
        try:
            account_info = self.tiktok_integration.get_account_info()
            
            if "error" in account_info:
                return {"success": False, "error": account_info["error"]}
            
            return {
                "success": True,
                "username": account_info.get("username", ""),
                "nickname": account_info.get("nickname", ""),
                "avatar_url": account_info.get("avatar_url", ""),
                "privacy_options": account_info.get("privacy_options", []),
                "max_video_duration": account_info.get("max_video_duration", 0)
            }
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return {"success": False, "error": str(e)}
