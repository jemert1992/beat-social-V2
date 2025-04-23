"""
TikTok API Client for Social Media Automation System

This module provides a client for interacting with the TikTok Content Posting API.
It handles authentication, video posting, and status tracking.
"""

import os
import requests
import json
import time
import logging
import random
from typing import Dict, List, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("tiktok_client")

class TikTokClient:
    """Client for interacting with the TikTok Content Posting API."""
    
    def __init__(self):
        """Initialize the TikTok API client."""
        # Using SOCIAL_MEDIA_TOKEN as required
        self.api_key = os.environ.get("TIKTOK_API_KEY", "")
        self.api_secret = os.environ.get("SOCIAL_MEDIA_TOKEN", "")
        self.base_url = "https://open.tiktokapis.com/v2/"
        self.access_token = None
        self.open_id = None
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    def set_credentials(self, access_token: str, open_id: str) -> None:
        """
        Set the access token and open ID for API requests.
        
        Args:
            access_token: The access token for the TikTok API
            open_id: The open ID of the TikTok user
        """
        self.access_token = access_token
        self.open_id = open_id
        logger.info("Credentials set successfully")
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     headers: Optional[Dict] = None, files: Optional[Dict] = None,
                     retry_count: int = 0) -> Dict:
        """
        Make a request to the TikTok API with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint to call
            data: Request data
            headers: Request headers
            files: Files to upload
            retry_count: Current retry attempt
            
        Returns:
            API response as a dictionary
        """
        if not self.access_token:
            raise ValueError("Access token not set. Call set_credentials() first.")
        
        url = f"{self.base_url}{endpoint}"
        
        # Set default headers
        if headers is None:
            headers = {}
        
        headers["Authorization"] = f"Bearer {self.access_token}"
        
        if data and not files:
            headers["Content-Type"] = "application/json; charset=UTF-8"
            
        try:
            logger.info(f"Making {method} request to {endpoint}")
            
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=data)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, headers=headers, data=data, files=files)
                else:
                    response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, data=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            
            # Implement exponential backoff for retries
            if retry_count < self.max_retries:
                wait_time = self.retry_delay * (2 ** retry_count)
                logger.info(f"Retrying in {wait_time} seconds... (Attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(wait_time)
                return self._make_request(method, endpoint, data, headers, files, retry_count + 1)
            else:
                logger.error(f"Max retries reached. Giving up.")
                raise
    
    def get_creator_info(self) -> Dict:
        """
        Query creator information, required before posting content.
        
        Returns:
            Creator information including privacy levels, restrictions, etc.
        """
        endpoint = "post/publish/creator_info/query/"
        response = self._make_request("POST", endpoint)
        
        logger.info("Retrieved creator info successfully")
        return response.get("data", {})
    
    def post_video_from_url(self, video_url: str, title: str, 
                           privacy_level: str = "PUBLIC_TO_EVERYONE",
                           disable_duet: bool = False,
                           disable_comment: bool = False, 
                           disable_stitch: bool = False,
                           video_cover_timestamp_ms: int = 0) -> Dict:
        """
        Post a video to TikTok using a URL.
        
        Args:
            video_url: URL of the video to post
            title: Caption for the video
            privacy_level: Privacy setting (PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, SELF_ONLY)
            disable_duet: Whether to disable duets
            disable_comment: Whether to disable comments
            disable_stitch: Whether to disable stitches
            video_cover_timestamp_ms: Timestamp for the video cover image
            
        Returns:
            Response containing publish_id for tracking the post
        """
        endpoint = "post/publish/video/init/"
        
        data = {
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch,
                "video_cover_timestamp_ms": video_cover_timestamp_ms
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url
            }
        }
        
        response = self._make_request("POST", endpoint, data)
        publish_id = response.get("data", {}).get("publish_id")
        
        if publish_id:
            logger.info(f"Video post initiated with publish_id: {publish_id}")
        else:
            logger.error("Failed to get publish_id from response")
            
        return response.get("data", {})
    
    def post_video_from_file(self, video_path: str, title: str,
                            privacy_level: str = "PUBLIC_TO_EVERYONE",
                            disable_duet: bool = False,
                            disable_comment: bool = False,
                            disable_stitch: bool = False,
                            video_cover_timestamp_ms: int = 0,
                            chunk_size: int = 10000000) -> Dict:
        """
        Post a video to TikTok from a local file.
        
        Args:
            video_path: Path to the video file
            title: Caption for the video
            privacy_level: Privacy setting (PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, SELF_ONLY)
            disable_duet: Whether to disable duets
            disable_comment: Whether to disable comments
            disable_stitch: Whether to disable stitches
            video_cover_timestamp_ms: Timestamp for the video cover image
            chunk_size: Size of chunks for uploading large files
            
        Returns:
            Response containing publish_id for tracking the post
        """
        # Get file size
        file_size = os.path.getsize(video_path)
        total_chunks = (file_size + chunk_size - 1) // chunk_size
        
        endpoint = "post/publish/video/init/"
        
        data = {
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch,
                "video_cover_timestamp_ms": video_cover_timestamp_ms
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunks
            }
        }
        
        # Initialize upload
        response = self._make_request("POST", endpoint, data)
        
        publish_id = response.get("data", {}).get("publish_id")
        upload_url = response.get("data", {}).get("upload_url")
        
        if not publish_id or not upload_url:
            logger.error("Failed to get publish_id or upload_url from response")
            return response.get("data", {})
        
        logger.info(f"Video upload initialized with publish_id: {publish_id}")
        
        # Upload the file
        with open(video_path, 'rb') as f:
            headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes 0-{file_size-1}/{file_size}"
            }
            
            # Use requests directly for the upload
            upload_response = requests.put(upload_url, headers=headers, data=f)
            
            if upload_response.status_code not in (200, 201):
                logger.error(f"Upload failed with status code {upload_response.status_code}")
                logger.error(f"Response: {upload_response.text}")
                return {"error": "Upload failed", "publish_id": publish_id}
        
        logger.info(f"Video uploaded successfully for publish_id: {publish_id}")
        return {"publish_id": publish_id}
    
    def get_post_status(self, publish_id: str) -> Dict:
        """
        Check the status of a post.
        
        Args:
            publish_id: The publish ID returned from post_video methods
            
        Returns:
            Status information for the post
        """
        endpoint = "post/publish/status/fetch/"
        data = {"publish_id": publish_id}
        
        response = self._make_request("POST", endpoint, data)
        status = response.get("data", {}).get("status")
        
        if status:
            logger.info(f"Post status for {publish_id}: {status}")
        else:
            logger.warning(f"Failed to get status for publish_id: {publish_id}")
            
        return response.get("data", {})
    
    def wait_for_post_completion(self, publish_id: str, max_wait_time: int = 300, 
                                check_interval: int = 10) -> Dict:
        """
        Wait for a post to complete processing.
        
        Args:
            publish_id: The publish ID returned from post_video methods
            max_wait_time: Maximum time to wait in seconds
            check_interval: Time between status checks in seconds
            
        Returns:
            Final status information for the post
        """
        start_time = time.time()
        last_status = None
        
        while time.time() - start_time < max_wait_time:
            status_data = self.get_post_status(publish_id)
            current_status = status_data.get("status")
            
            if current_status != last_status:
                logger.info(f"Status changed to: {current_status}")
                last_status = current_status
            
            if current_status in ("PUBLISH_FAILED", "PUBLISH_SUCCESS"):
                return status_data
                
            logger.info(f"Waiting for post completion. Current status: {current_status}")
            time.sleep(check_interval)
            
        logger.warning(f"Timed out waiting for post completion. Last status: {last_status}")
        return {"status": "TIMEOUT", "publish_id": publish_id}
