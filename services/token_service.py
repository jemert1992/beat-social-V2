"""
Secure token storage service for OAuth tokens.

This module provides utilities for securely storing and retrieving OAuth tokens.
"""

import logging
import base64
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from models import db, OAuthToken, SocialAccount

logger = logging.getLogger(__name__)

class TokenStorageService:
    """Service for securely storing and retrieving OAuth tokens."""
    
    def __init__(self, encryption_key=None):
        """
        Initialize the token storage service.
        
        Args:
            encryption_key: The encryption key to use for token encryption.
                If not provided, it will be generated from the environment.
        """
        self.encryption_key = encryption_key or self._get_encryption_key()
        self._initialize_encryption()
    
    def _get_encryption_key(self):
        """
        Get the encryption key from the environment or generate a new one.
        
        Returns:
            bytes: The encryption key
        """
        key = os.environ.get('TOKEN_ENCRYPTION_KEY')
        if key:
            # If the key is provided as a string, derive a key from it
            salt = b'social_media_automation'  # Fixed salt for consistency
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            return base64.urlsafe_b64encode(kdf.derive(key.encode()))
        else:
            # Generate a new key
            logger.warning("No encryption key provided, generating a new one")
            return Fernet.generate_key()
    
    def _initialize_encryption(self):
        """Initialize the encryption for OAuth tokens."""
        OAuthToken.init_encryption(self.encryption_key)
    
    def store_token(self, platform, account_id, user_id, access_token, refresh_token=None, 
                   token_type='Bearer', scope=None, expires_in=None, account_info=None):
        """
        Store an OAuth token for a social media account.
        
        Args:
            platform: The social media platform ('tiktok' or 'instagram')
            account_id: The ID of the account on the platform
            user_id: The ID of the user who owns the account
            access_token: The OAuth access token
            refresh_token: The OAuth refresh token (optional)
            token_type: The token type (default: 'Bearer')
            scope: The token scope (optional)
            expires_in: The token expiration time in seconds (optional)
            account_info: Additional account information (optional)
            
        Returns:
            tuple: (success, message, account_id)
        """
        try:
            # Check if the account already exists
            account = SocialAccount.query.filter_by(
                platform=platform,
                account_id=account_id
            ).first()
            
            if account:
                # Update the existing account
                account.user_id = user_id
                account.is_active = True
                
                if account_info:
                    account.username = account_info.get('username', account.username)
                    account.display_name = account_info.get('display_name', account.display_name)
                    account.profile_picture = account_info.get('profile_picture', account.profile_picture)
                
                # Update the token
                token = OAuthToken.query.filter_by(account_id=account.id).first()
                if token:
                    token.set_access_token(access_token)
                    if refresh_token:
                        token.set_refresh_token(refresh_token)
                    token.token_type = token_type
                    token.scope = scope
                    
                    if expires_in:
                        token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    token.updated_at = datetime.utcnow()
                else:
                    # Create a new token if none exists
                    token = OAuthToken(
                        account_id=account.id,
                        access_token=access_token,
                        refresh_token=refresh_token,
                        token_type=token_type,
                        scope=scope,
                        expires_in=expires_in
                    )
                    db.session.add(token)
                
                db.session.commit()
                logger.info(f"Updated token for {platform} account: {account.username}")
                return True, f"Updated token for {platform} account", account.id
            else:
                # Create a new account
                username = account_info.get('username', f"{platform} User")
                display_name = account_info.get('display_name', username)
                profile_picture = account_info.get('profile_picture')
                
                account = SocialAccount(
                    platform=platform,
                    account_id=account_id,
                    username=username,
                    user_id=user_id,
                    display_name=display_name,
                    profile_picture=profile_picture
                )
                db.session.add(account)
                db.session.flush()  # Get the account ID
                
                # Create a new token
                token = OAuthToken(
                    account_id=account.id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_type=token_type,
                    scope=scope,
                    expires_in=expires_in
                )
                db.session.add(token)
                db.session.commit()
                
                logger.info(f"Created new {platform} account: {account.username}")
                return True, f"Created new {platform} account", account.id
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error storing token: {str(e)}")
            return False, f"Error storing token: {str(e)}", None
    
    def get_token(self, account_id):
        """
        Get the OAuth token for a social media account.
        
        Args:
            account_id: The ID of the social account
            
        Returns:
            dict: The token information or None if not found
        """
        try:
            token = OAuthToken.query.filter_by(account_id=account_id).first()
            if not token:
                return None
            
            # Check if the token is expired
            if token.is_expired():
                logger.warning(f"Token for account {account_id} is expired")
            
            return {
                'access_token': token.get_access_token(),
                'refresh_token': token.get_refresh_token(),
                'token_type': token.token_type,
                'scope': token.scope,
                'expires_at': token.expires_at,
                'is_expired': token.is_expired()
            }
        
        except Exception as e:
            logger.error(f"Error getting token: {str(e)}")
            return None
    
    def refresh_token(self, account_id, new_access_token, new_refresh_token=None, expires_in=None):
        """
        Update a token with new values after refreshing.
        
        Args:
            account_id: The ID of the social account
            new_access_token: The new access token
            new_refresh_token: The new refresh token (optional)
            expires_in: The new expiration time in seconds (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            token = OAuthToken.query.filter_by(account_id=account_id).first()
            if not token:
                logger.error(f"No token found for account {account_id}")
                return False
            
            token.set_access_token(new_access_token)
            if new_refresh_token:
                token.set_refresh_token(new_refresh_token)
            
            if expires_in:
                token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            token.updated_at = datetime.utcnow()
            db.session.commit()
            
            account = SocialAccount.query.get(account_id)
            logger.info(f"Refreshed token for account: {account.platform}:{account.username}")
            return True
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error refreshing token: {str(e)}")
            return False
    
    def delete_token(self, account_id):
        """
        Delete the OAuth token for a social media account.
        
        Args:
            account_id: The ID of the social account
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            token = OAuthToken.query.filter_by(account_id=account_id).first()
            if token:
                db.session.delete(token)
                db.session.commit()
                logger.info(f"Deleted token for account {account_id}")
                return True
            else:
                logger.warning(f"No token found for account {account_id}")
                return False
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting token: {str(e)}")
            return False
    
    def get_active_accounts(self, user_id, platform=None):
        """
        Get all active social media accounts for a user.
        
        Args:
            user_id: The ID of the user
            platform: Filter by platform (optional)
            
        Returns:
            list: List of active social accounts
        """
        try:
            query = SocialAccount.query.filter_by(user_id=user_id, is_active=True)
            
            if platform:
                query = query.filter_by(platform=platform)
            
            accounts = query.all()
            return accounts
        
        except Exception as e:
            logger.error(f"Error getting active accounts: {str(e)}")
            return []
