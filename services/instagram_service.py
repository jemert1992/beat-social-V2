"""
Instagram service for API integration using stored tokens.

This module provides services for interacting with the Instagram API using stored OAuth tokens.
"""

import os
import requests
import json
import logging
import time
from datetime import datetime
from services.token_service import TokenStorageService

logger = logging.getLogger(__name__)

class InstagramService:
    """Service for interacting with the Instagram API using stored OAuth tokens."""
    
    def __init__(self, token_service=None):
        """
        Initialize the Instagram service.
        
        Args:
            token_service: The token storage service to use.
                If not provided, a new one will be created.
        """
        self.token_service = token_service or TokenStorageService()
        self.base_url = "https://graph.instagram.com"
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def get_account_info(self, account_id):
        """
        Get information about an Instagram account.
        
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
            # Get the Instagram user ID
            from models import SocialAccount
            account = SocialAccount.query.get(account_id)
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            instagram_user_id = account.account_id
            
            url = f"{self.base_url}/{instagram_user_id}"
            params = {
                'fields': 'id,username,account_type,media_count',
                'access_token': access_token
            }
            
            response = self._make_request('GET', url, params=params)
            
            # Update the last used timestamp for the account
            account.update_last_used()
            
            return {'success': True, 'data': response}
        
        except Exception as e:
            logger.error(f"Error getting Instagram account info: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_media(self, account_id, limit=25):
        """
        Get recent media from an Instagram account.
        
        Args:
            account_id: The ID of the social account
            limit: Maximum number of media items to return
            
        Returns:
            dict: Media items or error details
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
            # Get the Instagram user ID
            from models import SocialAccount
            account = SocialAccount.query.get(account_id)
            if not account:
                return {'success': False, 'error': 'Account not found'}
            
            instagram_user_id = account.account_id
            
            url = f"{self.base_url}/{instagram_user_id}/media"
            params = {
                'fields': 'id,caption,media_type,media_url,permalink,thumbnail_url,timestamp,username',
                'access_token': access_token,
                'limit': limit
            }
            
            response = self._make_request('GET', url, params=params)
            
            # Update the last used timestamp for the account
            account.update_last_used()
            
            return {'success': True, 'data': response.get('data', [])}
        
        except Exception as e:
            logger.error(f"Error getting Instagram media: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def refresh_account_token(self, account_id):
        """
        Refresh the access token for an Instagram account.
        
        Args:
            account_id: The ID of the social account
            
        Returns:
            dict: Result of the refresh operation
        """
        # Get the token for the account
        token_info = self.token_service.get_token(account_id)
        if not token_info:
            return {'success': False, 'error': 'No token found for this account'}
        
        access_token = token_info['access_token']
        if not access_token:
            return {'success': False, 'error': 'No access token available'}
        
        # Make the refresh request
        try:
            url = f"{self.base_url}/refresh_access_token"
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': access_token
            }
            
            response = self._make_request('GET', url, params=params)
            
            new_access_token = response.get('access_token')
            expires_in = response.get('expires_in', 60*24*60*60)  # Default to 60 days
            
            if not new_access_token:
                return {'success': False, 'error': 'Invalid token response from Instagram'}
            
            # Update the token in the database
            success = self.token_service.refresh_token(
                account_id=account_id,
                new_access_token=new_access_token,
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
            logger.error(f"Error refreshing Instagram token: {str(e)}")
            return {'success': False, 'error': f"Error connecting to Instagram API: {str(e)}"}
        except Exception as e:
            logger.error(f"Error refreshing Instagram token: {str(e)}")
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
