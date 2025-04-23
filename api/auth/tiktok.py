"""
TikTok OAuth authentication implementation.

This module handles the OAuth flow for TikTok authentication.
"""

import os
import requests
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, url_for, session, current_app, jsonify
from models import db, SocialAccount, OAuthToken

logger = logging.getLogger(__name__)

tiktok_bp = Blueprint('tiktok_auth', __name__)

@tiktok_bp.route('/connect')
def connect():
    """
    Initiate the TikTok OAuth flow.
    
    This endpoint redirects the user to TikTok's authorization page.
    """
    # Get the current user ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Store the user ID in the session for the callback
    session['connecting_user_id'] = user_id
    
    # Get TikTok OAuth configuration
    config = current_app.config
    client_key = config['TIKTOK_CLIENT_KEY']
    redirect_uri = config['TIKTOK_REDIRECT_URI']
    scope = config['TIKTOK_SCOPE']
    
    # Generate the authorization URL
    auth_url = (
        f"https://www.tiktok.com/auth/authorize/"
        f"?client_key={client_key}"
        f"&scope={scope}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&state={user_id}"
    )
    
    return redirect(auth_url)

@tiktok_bp.route('/callback')
def callback():
    """
    Handle the callback from TikTok's OAuth flow.
    
    This endpoint exchanges the authorization code for access and refresh tokens,
    then stores the tokens and account information in the database.
    """
    # Get the authorization code and state from the request
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        logger.error("No authorization code received from TikTok")
        return jsonify({'error': 'No authorization code received'}), 400
    
    # Get the user ID from the state or session
    user_id = state or session.get('connecting_user_id')
    if not user_id:
        logger.error("No user ID found in state or session")
        return jsonify({'error': 'Invalid state parameter'}), 400
    
    # Get TikTok OAuth configuration
    config = current_app.config
    client_key = config['TIKTOK_CLIENT_KEY']
    client_secret = config['TIKTOK_CLIENT_SECRET']
    redirect_uri = config['TIKTOK_REDIRECT_URI']
    
    # Exchange the authorization code for tokens
    try:
        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
        token_data = {
            'client_key': client_key,
            'client_secret': client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        refresh_token = token_info.get('refresh_token')
        expires_in = token_info.get('expires_in')
        open_id = token_info.get('open_id')
        
        if not access_token or not open_id:
            logger.error("Missing access token or open ID in TikTok response")
            return jsonify({'error': 'Invalid token response from TikTok'}), 400
        
        # Get user information from TikTok
        user_info = get_user_info(access_token, open_id)
        
        # Check if this account is already connected
        existing_account = SocialAccount.query.filter_by(
            platform='tiktok',
            account_id=open_id
        ).first()
        
        if existing_account:
            # Update the existing account
            existing_account.username = user_info.get('display_name', 'TikTok User')
            existing_account.display_name = user_info.get('display_name')
            existing_account.profile_picture = user_info.get('avatar_url')
            existing_account.is_active = True
            existing_account.user_id = user_id  # Update to the current user
            
            # Update the token
            token = OAuthToken.query.filter_by(account_id=existing_account.id).first()
            if token:
                token.set_access_token(access_token)
                token.set_refresh_token(refresh_token)
                token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                token.updated_at = datetime.utcnow()
            else:
                # Create a new token if none exists
                token = OAuthToken(
                    account_id=existing_account.id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_in=expires_in
                )
                db.session.add(token)
            
            db.session.commit()
            logger.info(f"Updated existing TikTok account: {existing_account.username}")
        else:
            # Create a new social account
            account = SocialAccount(
                platform='tiktok',
                account_id=open_id,
                username=user_info.get('display_name', 'TikTok User'),
                user_id=user_id,
                display_name=user_info.get('display_name'),
                profile_picture=user_info.get('avatar_url')
            )
            db.session.add(account)
            db.session.flush()  # Get the account ID
            
            # Create a new token
            token = OAuthToken(
                account_id=account.id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in
            )
            db.session.add(token)
            db.session.commit()
            logger.info(f"Created new TikTok account: {account.username}")
        
        # Clear the connecting user ID from the session
        session.pop('connecting_user_id', None)
        
        # Redirect to the accounts page
        return redirect(url_for('accounts.index', status='success', 
                               message='TikTok account connected successfully'))
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error exchanging TikTok authorization code: {str(e)}")
        return jsonify({'error': 'Error connecting to TikTok API'}), 500
    except Exception as e:
        logger.error(f"Error processing TikTok callback: {str(e)}")
        return jsonify({'error': 'Error processing TikTok authentication'}), 500

def get_user_info(access_token, open_id):
    """
    Get user information from TikTok API.
    
    Args:
        access_token: The access token for the TikTok API
        open_id: The open ID of the TikTok user
        
    Returns:
        dict: User information from TikTok
    """
    try:
        user_info_url = "https://open.tiktokapis.com/v2/user/info/"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        params = {
            'fields': 'open_id,union_id,avatar_url,display_name,bio_description,profile_deep_link'
        }
        
        response = requests.get(user_info_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        return data.get('data', {})
    except Exception as e:
        logger.error(f"Error getting TikTok user info: {str(e)}")
        return {}

@tiktok_bp.route('/refresh/<int:account_id>')
def refresh_token(account_id):
    """
    Refresh the access token for a TikTok account.
    
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
    account = SocialAccount.query.filter_by(id=account_id, platform='tiktok').first()
    if not account or account.user_id != user_id:
        return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    # Get the token
    token = OAuthToken.query.filter_by(account_id=account.id).first()
    if not token:
        return jsonify({'error': 'No token found for this account'}), 404
    
    # Check if the token needs refreshing
    if not token.is_expired():
        return jsonify({'message': 'Token is still valid', 'expires_at': token.expires_at})
    
    # Get the refresh token
    refresh_token = token.get_refresh_token()
    if not refresh_token:
        return jsonify({'error': 'No refresh token available'}), 400
    
    # Get TikTok OAuth configuration
    config = current_app.config
    client_key = config['TIKTOK_CLIENT_KEY']
    client_secret = config['TIKTOK_CLIENT_SECRET']
    
    # Refresh the token
    try:
        token_url = "https://open.tiktokapis.com/v2/oauth/token/"
        token_data = {
            'client_key': client_key,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        access_token = token_info.get('access_token')
        new_refresh_token = token_info.get('refresh_token')
        expires_in = token_info.get('expires_in')
        
        if not access_token:
            logger.error("Missing access token in TikTok refresh response")
            return jsonify({'error': 'Invalid token response from TikTok'}), 400
        
        # Update the token
        token.set_access_token(access_token)
        if new_refresh_token:
            token.set_refresh_token(new_refresh_token)
        token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        token.updated_at = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Refreshed token for TikTok account: {account.username}")
        
        return jsonify({
            'message': 'Token refreshed successfully',
            'expires_at': token.expires_at.isoformat()
        })
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error refreshing TikTok token: {str(e)}")
        return jsonify({'error': 'Error connecting to TikTok API'}), 500
    except Exception as e:
        logger.error(f"Error processing TikTok token refresh: {str(e)}")
        return jsonify({'error': 'Error refreshing TikTok token'}), 500

@tiktok_bp.route('/disconnect/<int:account_id>')
def disconnect(account_id):
    """
    Disconnect a TikTok account.
    
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
    account = SocialAccount.query.filter_by(id=account_id, platform='tiktok', user_id=user_id).first()
    if not account:
        return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    # Deactivate the account instead of deleting it
    account.is_active = False
    db.session.commit()
    logger.info(f"Disconnected TikTok account: {account.username}")
    
    return redirect(url_for('accounts.index', status='success', 
                           message='TikTok account disconnected successfully'))
