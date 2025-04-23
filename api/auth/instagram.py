"""
Instagram OAuth authentication implementation.

This module handles the OAuth flow for Instagram authentication.
"""

import os
import requests
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, url_for, session, current_app, jsonify
from models import db, SocialAccount, OAuthToken

logger = logging.getLogger(__name__)

instagram_bp = Blueprint('instagram_auth', __name__)

@instagram_bp.route('/connect')
def connect():
    """
    Initiate the Instagram OAuth flow.
    
    This endpoint redirects the user to Instagram's authorization page.
    """
    # Get the current user ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Store the user ID in the session for the callback
    session['connecting_user_id'] = user_id
    
    # Get Instagram OAuth configuration
    config = current_app.config
    app_id = config['INSTAGRAM_APP_ID']
    redirect_uri = config['INSTAGRAM_REDIRECT_URI']
    scope = config['INSTAGRAM_SCOPE']
    
    # Generate the authorization URL
    auth_url = (
        f"https://api.instagram.com/oauth/authorize"
        f"?client_id={app_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
        f"&response_type=code"
        f"&state={user_id}"
    )
    
    return redirect(auth_url)

@instagram_bp.route('/callback')
def callback():
    """
    Handle the callback from Instagram's OAuth flow.
    
    This endpoint exchanges the authorization code for access and refresh tokens,
    then stores the tokens and account information in the database.
    """
    # Get the authorization code and state from the request
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        logger.error("No authorization code received from Instagram")
        return jsonify({'error': 'No authorization code received'}), 400
    
    # Get the user ID from the state or session
    user_id = state or session.get('connecting_user_id')
    if not user_id:
        logger.error("No user ID found in state or session")
        return jsonify({'error': 'Invalid state parameter'}), 400
    
    # Get Instagram OAuth configuration
    config = current_app.config
    app_id = config['INSTAGRAM_APP_ID']
    app_secret = config['INSTAGRAM_APP_SECRET']
    redirect_uri = config['INSTAGRAM_REDIRECT_URI']
    
    # Exchange the authorization code for tokens
    try:
        token_url = "https://api.instagram.com/oauth/access_token"
        token_data = {
            'client_id': app_id,
            'client_secret': app_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        user_id_instagram = token_info.get('user_id')
        
        if not access_token or not user_id_instagram:
            logger.error("Missing access token or user ID in Instagram response")
            return jsonify({'error': 'Invalid token response from Instagram'}), 400
        
        # Get long-lived access token
        long_lived_token = get_long_lived_token(access_token, app_id, app_secret)
        
        # Get user information from Instagram
        user_info = get_user_info(long_lived_token, user_id_instagram)
        
        # Check if this account is already connected
        existing_account = SocialAccount.query.filter_by(
            platform='instagram',
            account_id=str(user_id_instagram)
        ).first()
        
        if existing_account:
            # Update the existing account
            existing_account.username = user_info.get('username', 'Instagram User')
            existing_account.display_name = user_info.get('username')
            existing_account.profile_picture = user_info.get('profile_picture')
            existing_account.is_active = True
            existing_account.user_id = user_id  # Update to the current user
            
            # Update the token
            token = OAuthToken.query.filter_by(account_id=existing_account.id).first()
            if token:
                token.set_access_token(long_lived_token)
                token.expires_at = datetime.utcnow() + timedelta(days=60)  # Long-lived tokens last 60 days
                token.updated_at = datetime.utcnow()
            else:
                # Create a new token if none exists
                token = OAuthToken(
                    account_id=existing_account.id,
                    access_token=long_lived_token,
                    expires_in=60*24*60*60  # 60 days in seconds
                )
                db.session.add(token)
            
            db.session.commit()
            logger.info(f"Updated existing Instagram account: {existing_account.username}")
        else:
            # Create a new social account
            account = SocialAccount(
                platform='instagram',
                account_id=str(user_id_instagram),
                username=user_info.get('username', 'Instagram User'),
                user_id=user_id,
                display_name=user_info.get('username'),
                profile_picture=user_info.get('profile_picture')
            )
            db.session.add(account)
            db.session.flush()  # Get the account ID
            
            # Create a new token
            token = OAuthToken(
                account_id=account.id,
                access_token=long_lived_token,
                expires_in=60*24*60*60  # 60 days in seconds
            )
            db.session.add(token)
            db.session.commit()
            logger.info(f"Created new Instagram account: {account.username}")
        
        # Clear the connecting user ID from the session
        session.pop('connecting_user_id', None)
        
        # Redirect to the accounts page
        return redirect(url_for('accounts.index', status='success', 
                               message='Instagram account connected successfully'))
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error exchanging Instagram authorization code: {str(e)}")
        return jsonify({'error': 'Error connecting to Instagram API'}), 500
    except Exception as e:
        logger.error(f"Error processing Instagram callback: {str(e)}")
        return jsonify({'error': 'Error processing Instagram authentication'}), 500

def get_long_lived_token(short_lived_token, app_id, app_secret):
    """
    Exchange a short-lived token for a long-lived token.
    
    Args:
        short_lived_token: The short-lived access token
        app_id: The Instagram app ID
        app_secret: The Instagram app secret
        
    Returns:
        str: Long-lived access token
    """
    try:
        url = "https://graph.instagram.com/access_token"
        params = {
            'grant_type': 'ig_exchange_token',
            'client_secret': app_secret,
            'access_token': short_lived_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data.get('access_token', short_lived_token)
    except Exception as e:
        logger.error(f"Error getting long-lived token: {str(e)}")
        return short_lived_token

def get_user_info(access_token, user_id):
    """
    Get user information from Instagram API.
    
    Args:
        access_token: The access token for the Instagram API
        user_id: The user ID of the Instagram user
        
    Returns:
        dict: User information from Instagram
    """
    try:
        user_info_url = f"https://graph.instagram.com/{user_id}"
        params = {
            'fields': 'id,username,account_type,media_count',
            'access_token': access_token
        }
        
        response = requests.get(user_info_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Instagram Graph API doesn't provide profile picture directly
        # We'll use the username as display name and leave profile picture blank
        return {
            'username': data.get('username', 'Instagram User'),
            'profile_picture': None
        }
    except Exception as e:
        logger.error(f"Error getting Instagram user info: {str(e)}")
        return {}

@instagram_bp.route('/refresh/<int:account_id>')
def refresh_token(account_id):
    """
    Refresh the access token for an Instagram account.
    
    Args:
        account_id: The ID of the social account to refresh
        
    Returns:
        JSON response with the result of the refresh operation
    """
    # Get the current user ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get the account and check if it belongs to the user
    account = SocialAccount.query.filter_by(id=account_id, platform='instagram').first()
    if not account or account.user_id != user_id:
        return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    # Get the token
    token = OAuthToken.query.filter_by(account_id=account.id).first()
    if not token:
        return jsonify({'error': 'No token found for this account'}), 404
    
    # Check if the token needs refreshing
    if not token.is_expired():
        return jsonify({'message': 'Token is still valid', 'expires_at': token.expires_at})
    
    # Get the access token
    access_token = token.get_access_token()
    if not access_token:
        return jsonify({'error': 'No access token available'}), 400
    
    # Refresh the token
    try:
        url = "https://graph.instagram.com/refresh_access_token"
        params = {
            'grant_type': 'ig_refresh_token',
            'access_token': access_token
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        new_access_token = data.get('access_token')
        expires_in = data.get('expires_in', 60*24*60*60)  # Default to 60 days
        
        if not new_access_token:
            logger.error("Missing access token in Instagram refresh response")
            return jsonify({'error': 'Invalid token response from Instagram'}), 400
        
        # Update the token
        token.set_access_token(new_access_token)
        token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        token.updated_at = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Refreshed token for Instagram account: {account.username}")
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'expires_at': token.expires_at.isoformat()
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error refreshing Instagram token: {str(e)}")
        return jsonify({'error': 'Error connecting to Instagram API'}), 500
    except Exception as e:
        logger.error(f"Error processing Instagram token refresh: {str(e)}")
        return jsonify({'error': 'Error refreshing Instagram token'}), 500

@instagram_bp.route('/disconnect/<int:account_id>')
def disconnect(account_id):
    """
    Disconnect an Instagram account.
    
    Args:
        account_id: The ID of the social account to disconnect
        
    Returns:
        Redirect to the accounts page
    """
    # Get the current user ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get the account and check if it belongs to the user
    account = SocialAccount.query.filter_by(id=account_id, platform='instagram', user_id=user_id).first()
    if not account:
        return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    # Deactivate the account instead of deleting it
    account.is_active = False
    db.session.commit()
    logger.info(f"Disconnected Instagram account: {account.username}")
    
    return redirect(url_for('accounts.index', status='success', 
                           message='Instagram account disconnected successfully'))
