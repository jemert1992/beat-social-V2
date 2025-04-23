"""
Example usage of the TikTok API integration.

This script demonstrates how to use the TikTok API integration to post content to TikTok.
"""

import os
import sys
import logging
from tiktok_service import TikTokService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Example usage of the TikTok API integration.
    """
    # Create TikTok service
    tiktok_service = TikTokService()
    
    # Example 1: Post a video using a URL
    video_url = "https://example.com/video.mp4"  # Replace with actual video URL
    caption = "Check out this awesome video! #trending"
    hashtags = ["fyp", "viral", "trending"]
    
    response = tiktok_service.post_video(video_url, caption, hashtags)
    logger.info(f"Post video response: {response}")
    
    # Example 2: Post a video file
    # video_path = "/path/to/video.mp4"  # Replace with actual video path
    # caption = "Another great video! #content"
    # hashtags = ["fyp", "viral", "content"]
    
    # response = tiktok_service.post_video_file(video_path, caption, hashtags)
    # logger.info(f"Post video file response: {response}")
    
    # Example 3: Get account information
    account_info = tiktok_service.get_account_info()
    logger.info(f"Account info: {account_info}")

if __name__ == "__main__":
    main()
