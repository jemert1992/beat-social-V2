"""
Authentication routes for the OAuth implementation.

This module defines the routes for user authentication and account management.
"""

import logging
from flask import Blueprint, request, redirect, url_for, render_template, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

logger = logging.getLogger(__name__)

auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html')
        
        # Update last login timestamp
        user.update_last_login()
        
        # Store user ID in session
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        
        logger.info(f"User {username} logged in successfully")
        return redirect(url_for('dashboard.index'))
    
    return render_template('auth/login.html')

@auth_routes.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))

@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        # First user is automatically an admin
        is_admin = User.query.count() == 0
        
        user = User(
            username=username,
            email=email,
            password=password,
            is_admin=is_admin
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {username} (admin: {is_admin})")
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_routes.route('/profile', methods=['GET', 'POST'])
def profile():
    """Handle user profile management."""
    # Check if user is logged in
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in to access your profile', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Update email
        if email and email != user.email:
            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already exists', 'error')
            else:
                user.email = email
                flash('Email updated successfully', 'success')
        
        # Update password
        if current_password and new_password:
            if not user.check_password(current_password):
                flash('Current password is incorrect', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'error')
            else:
                user.set_password(new_password)
                flash('Password updated successfully', 'success')
        
        db.session.commit()
        logger.info(f"User {user.username} updated profile")
    
    return render_template('auth/profile.html', user=user)

@auth_routes.route('/check-auth')
def check_auth():
    """Check if user is authenticated."""
    user_id = session.get('user_id')
    if user_id:
        return jsonify({'authenticated': True, 'user_id': user_id})
    else:
        return jsonify({'authenticated': False}), 401
