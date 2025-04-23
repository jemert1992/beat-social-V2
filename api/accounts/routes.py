"""
Account management routes for the OAuth implementation.

This module defines the routes for managing social media accounts.
"""

import logging
from flask import Blueprint, request, redirect, url_for, render_template, session, flash, jsonify
from models import db, SocialAccount, OAuthToken
from services.tiktok_service import TikTokService
from services.instagram_service import InstagramService

logger = logging.getLogger(__name__)

accounts_bp = Blueprint('accounts', __name__)

@accounts_bp.route('/')
def index():
    """Display all connected social media accounts."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access your accounts', 'error')
        return redirect(url_for('auth.login'))
    
    # Get all active accounts for the user
    accounts = SocialAccount.query.filter_by(user_id=user_id, is_active=True).all()
    
    # Get status message from query parameters
    status = request.args.get('status')
    message = request.args.get('message')
    
    if status and message:
        flash(message, status)
    
    return render_template('dashboard/accounts.html', accounts=accounts)

@accounts_bp.route('/view/<int:account_id>')
def view(account_id):
    """View details of a specific social media account."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access your accounts', 'error')
        return redirect(url_for('auth.login'))
    
    # Get the account and check if it belongs to the user
    account = SocialAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        flash('Account not found or unauthorized', 'error')
        return redirect(url_for('accounts.index'))
    
    # Get the token for the account
    token = OAuthToken.query.filter_by(account_id=account.id).first()
    
    # Get account information from the API
    if account.platform == 'tiktok':
        service = TikTokService()
        account_info = service.get_account_info(account.id)
    elif account.platform == 'instagram':
        service = InstagramService()
        account_info = service.get_account_info(account.id)
    else:
        account_info = {'success': False, 'error': 'Unsupported platform'}
    
    return render_template('dashboard/account_details.html', 
                          account=account, 
                          token=token,
                          account_info=account_info)

@accounts_bp.route('/refresh/<int:account_id>')
def refresh(account_id):
    """Refresh the token for a social media account."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access your accounts', 'error')
        return redirect(url_for('auth.login'))
    
    # Get the account and check if it belongs to the user
    account = SocialAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        flash('Account not found or unauthorized', 'error')
        return redirect(url_for('accounts.index'))
    
    # Refresh the token based on the platform
    if account.platform == 'tiktok':
        service = TikTokService()
        result = service.refresh_account_token(account.id)
    elif account.platform == 'instagram':
        service = InstagramService()
        result = service.refresh_account_token(account.id)
    else:
        result = {'success': False, 'error': 'Unsupported platform'}
    
    if result['success']:
        flash('Token refreshed successfully', 'success')
    else:
        flash(f"Error refreshing token: {result.get('error', 'Unknown error')}", 'error')
    
    return redirect(url_for('accounts.view', account_id=account.id))

@accounts_bp.route('/disconnect/<int:account_id>')
def disconnect(account_id):
    """Disconnect a social media account."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access your accounts', 'error')
        return redirect(url_for('auth.login'))
    
    # Get the account and check if it belongs to the user
    account = SocialAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        flash('Account not found or unauthorized', 'error')
        return redirect(url_for('accounts.index'))
    
    # Deactivate the account instead of deleting it
    account.is_active = False
    db.session.commit()
    
    flash(f"{account.platform.capitalize()} account {account.username} disconnected successfully", 'success')
    return redirect(url_for('accounts.index'))

@accounts_bp.route('/api/list')
def api_list():
    """API endpoint to list all connected social media accounts."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get all active accounts for the user
    accounts = SocialAccount.query.filter_by(user_id=user_id, is_active=True).all()
    
    # Convert accounts to dictionary
    accounts_list = [account.to_dict() for account in accounts]
    
    return jsonify({'accounts': accounts_list})

@accounts_bp.route('/api/info/<int:account_id>')
def api_info(account_id):
    """API endpoint to get information about a specific social media account."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get the account and check if it belongs to the user
    account = SocialAccount.query.filter_by(id=account_id, user_id=user_id).first()
    if not account:
        return jsonify({'error': 'Account not found or unauthorized'}), 404
    
    # Get account information from the API
    if account.platform == 'tiktok':
        service = TikTokService()
        account_info = service.get_account_info(account.id)
    elif account.platform == 'instagram':
        service = InstagramService()
        account_info = service.get_account_info(account.id)
    else:
        account_info = {'success': False, 'error': 'Unsupported platform'}
    
    return jsonify(account_info)
