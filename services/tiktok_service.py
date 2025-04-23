"""
TikTok service for API integration using stored tokens.

This module provides services for interacting with the TikTok API using stored OAuth tokens.
"""

import os
import requests
import json
import logging
import time
from datetime import datetime
from services.token_service import TokenStorageService

logger = logging.getLogger(__name__)

class TikTokService:
    """Service for interacting with the TikTok API using stored OAuth tokens."""
    
    def __init__(self, token_service=None):
        """
        Initialize the TikTok service.
        
        Args:
            token_service: The token storage service to use.
                If not provided, a new one will be created.
        """
        self.token_service = token_service or TokenStorageService()
        self.base_url = "https://open.tiktokapis.com/v2"
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def get_account_info(self, account_id):
        """
        Get information about a TikTok account.
        
        Args:
            account_id: The ID of the social account
            
        Returns:
            dict: Account information or error details
        """
        # Get the token for the account
        token_info = self.token_service.get_token(account_id)
        if not token_info:
            return {'success': False, 'error': 'No token found for this account'}
        
        # Check if the token is expired
        if token_info['is_expired']:
            return {'success': False, 'error': 'Token is expired, please refresh'}
        
        access_token = token_info['access_token']
        
        # Make the API request
        try:
            url = f"{self.base_url}/user/info/"
            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }
            params = {
                'fields': 'open_id,union_id,avatar_url,display_name,bio_description,profile_deep_link'
            }
            
            response = self._make_request('GET', url, headers=headers, params=params)
            
            # Update the last used timestamp for the account
            from models import SocialAccount, db
            account = SocialAccount.query.get(account_id)
            if account:
                account.update_last_used()
            
            return {'success': True, 'data': response.get('data', {})}
        
        except Exception as e:
            logger.error(f"Error getting TikTok account info: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def post_video(self, account_id, video_url=None, video_path=None, caption=None, hashtags=None, privacy_level='PUBLIC_TO_EVERYONE'):
        """
        Post a video to TikTok.
        
        Args:
            account_id: The ID of the social account
            video_url: URL of the video to post (either video_url or video_path must be provided)
            video_path: Path to the video file to post
            caption: Caption for the video
            hashtags: List of hashtags for the video
            privacy_level: Privacy level for the video (default: PUBLIC_TO_EVERYONE)
            
        Returns:
            dict: Response from the TikTok API or error details
        """
        # Get the token for the account
        token_info = self.token_service.get_token(account_id)
        if not token_info:
            return {'success': False, 'error': 'No token found for this account'}
        
        # Check if the token is expired
        if token_info['is_expired']:
            return {'success': False, 'error': 'Token is expired, please refresh'}
        
        access_token = token_info['access_token']
        
        # Validate input
        if not video_url and not video_path:
            return {'success': False, 'error': 'Either video_url or video_path must be provided'}
        
        # Prepare the caption with hashtags
        full_caption = caption or ""
        if hashtags:
            hashtag_text = " ".join([f"#{tag}" for tag in hashtags])
            full_caption = f"{full_caption} {hashtag_text}"
        
        # Make the API request
        try:
            # Step 1: Initialize the video upload
            init_url = f"{self.base_url}/video/init/"
            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }
            
            init_data = {
                'post_info': {
                    'title': full_caption,
                    'privacy_level': privacy_level,
                    'disable_duet': False,
                    'disable_comment': False,
                    'disable_stitch': False
                }
            }
            
            init_response = self._make_request('POST', init_url, headers=headers, json=init_data)
            
            if not init_response.get('data', {}).get('upload_url'):
                return {'success': False, 'error': 'Failed to initialize video upload'}
            
            upload_url = init_response['data']['upload_url']
            
            # Step 2: Upload the video
            if video_url:
                # Download the video from the URL
                video_response = requests.get(video_url, stream=True)
                video_response.raise_for_status()
                video_content = video_response.content
            else:
                # Read the video file
                with open(video_path, 'rb') as f:
                    video_content = f.read()
            
            upload_headers = {
                'Content-Type': 'video/mp4'
            }
            
            upload_response = requests.put(upload_url, headers=upload_headers, data=video_content)
            upload_response.raise_for_status()
            
            # Step 3: Finalize the video upload
            publish_url = f"{self.base_url}/video/publish/"
            publish_data = {
                'publish_id': init_response['data']['publish_id']
            }
            
            publish_response = self._make_request('POST', publish_url, headers=headers, json=publish_data)
            
            # Update the last used timestamp for the account
            from models import SocialAccount, db
            account = SocialAccount.query.get(account_id)
            if account:
                account.update_last_used()
            
            return {'success': True, 'data': publish_response.get('data', {})}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error posting video to TikTok: {str(e)}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Error posting video to TikTok: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_video_status(self, account_id, publish_id):
        """
        Get the status of a video upload.
        
        Args:
            account_id: The ID of the social account
            publish_id: The publish ID of the video
            
        Returns:
            dict: Video status or error details
        """
        # Get the token for the account
        token_info = self.token_service.get_token(account_id)
        if not token_info:
            return {'success': False, 'error': 'No token found for this account'}
        
        # Check if the token is expired
        if token_info['is_expired']:
            return {'success': False, 'error': 'Token is expired, please refresh'}
        
        access_token = token_info['access_token']
        
        # Make the API request
        try:
            url = f"{self.base_url}/video/query/"
            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }
            
            data = {
                'publish_id': publish_id
            }
            
            response = self._make_request('POST', url, headers=headers, json=data)
            
            return {'success': True, 'data': response.get('data', {})}
        
        except Exception as e:
            logger.error(f"Error getting video status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def refresh_account_token(self, account_id):
        """
        Refresh the access token for a TikTok account.
        
        Args:
            account_id: The ID of the social account
            
        Returns:
            dict: Result of the refresh operation
        """
        # Get the token for the account
        token_info = self.token_service.get_token(account_id)
        if not token_info:
            return {'success': False, 'error': 'No token found for this account'}
        
        refresh_token = token_info['refresh_token']
        if not refresh_token:
            return {'success': False, 'error': 'No refresh token available'}
        
        # Get TikTok OAuth configuration
        client_key = os.environ.get('TIKTOK_CLIENT_KEY')
        client_secret = os.environ.get('TIKTOK_CLIENT_SECRET')
        
        if not client_key or not client_secret:
            return {'success': False, 'error': 'TikTok API credentials not configured'}
        
        # Make the refresh request
        try:
            url = "https://open.tiktokapis.com/v2/oauth/token/"
            data = {
                'client_key': client_key,
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            token_info = response.json()
            
            access_token = token_info.get('access_token')
            new_refresh_token = token_info.get('refresh_token')
            expires_in = token_info.get('expires_in')
            
            if not access_token:
                return {'success': False, 'error': 'Invalid token response from TikTok'}
            
            # Update the token in the database
            success = self.token_service.refresh_token(
                account_id=account_id,
                new_access_token=access_token,
                new_refresh_token=new_refresh_token,
                expires_in=expires_in
            )
            
            if success:
                return {
                    'success': True,
                    'message': 'Token refreshed successfully',
                    'expires_in': expires_in
                }
            else:
                return {'success': False, 'error': 'Failed to update token in database'}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing TikTok token: {str(e)}")
            return {'success': False, 'error': f"Error connecting to TikTok API: {str(e)}"}
        except Exception as e:
            logger.error(f"Error refreshing TikTok token: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _make_request(self, method, url, headers=None, params=None, json=None, data=None):
        """
        Make an API request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            headers: Request headers
            params: Query parameters
            json: JSON body
            data: Form data
            
        Returns:
            dict: Response JSON
            
        Raises:
            requests.exceptions.RequestException: If the request fails after retries
        """
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json,
                    data=data
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.RequestException as e:
                last_error = e
                retries += 1
                
                if retries < self.max_retries:
                    # Exponential backoff
                    sleep_time = self.retry_delay * (2 ** (retries - 1))
                    logger.warning(f"Request failed, retrying in {sleep_time} seconds... ({retries}/{self.max_retries})")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Request failed after {self.max_retries} retries: {str(e)}")
                    raise
        
        # This should not be reached, but just in case
        raise last_error or Exception("Request failed")
