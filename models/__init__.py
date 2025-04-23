"""
Database models for the OAuth implementation.

This file contains the SQLAlchemy models for users, social media accounts, and OAuth tokens.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
import json

db = SQLAlchemy()

class User(db.Model):
    """Admin user model for managing social media accounts."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    accounts = db.relationship('SocialAccount', backref='admin', lazy='dynamic')
    
    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_admin = is_admin
    
    def set_password(self, password):
        """Set the password hash for the user."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class SocialAccount(db.Model):
    """Social media account model."""
    __tablename__ = 'social_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(20), nullable=False)  # 'tiktok' or 'instagram'
    account_id = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    display_name = db.Column(db.String(128))
    profile_picture = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    tokens = db.relationship('OAuthToken', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, platform, account_id, username, user_id, display_name=None, profile_picture=None):
        self.platform = platform
        self.account_id = account_id
        self.username = username
        self.user_id = user_id
        self.display_name = display_name
        self.profile_picture = profile_picture
    
    def update_last_used(self):
        """Update the last used timestamp."""
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert account to dictionary."""
        return {
            'id': self.id,
            'platform': self.platform,
            'account_id': self.account_id,
            'username': self.username,
            'display_name': self.display_name,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
    
    def __repr__(self):
        return f'<SocialAccount {self.platform}:{self.username}>'

class OAuthToken(db.Model):
    """OAuth token model for storing encrypted access and refresh tokens."""
    __tablename__ = 'oauth_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    access_token_encrypted = db.Column(db.Text, nullable=False)
    refresh_token_encrypted = db.Column(db.Text)
    token_type = db.Column(db.String(20), default='Bearer')
    scope = db.Column(db.String(256))
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    account_id = db.Column(db.Integer, db.ForeignKey('social_accounts.id'), nullable=False)
    
    # Class variables
    _cipher = None
    
    @classmethod
    def init_encryption(cls, key):
        """Initialize the encryption cipher with the provided key."""
        cls._cipher = Fernet(key)
    
    def __init__(self, account_id, access_token, refresh_token=None, token_type='Bearer', 
                 scope=None, expires_in=None):
        if not self._cipher:
            raise ValueError("Encryption not initialized. Call OAuthToken.init_encryption() first.")
        
        self.account_id = account_id
        self.set_access_token(access_token)
        if refresh_token:
            self.set_refresh_token(refresh_token)
        self.token_type = token_type
        self.scope = scope
        
        if expires_in:
            self.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    def set_access_token(self, access_token):
        """Encrypt and store the access token."""
        self.access_token_encrypted = self._encrypt(access_token)
    
    def get_access_token(self):
        """Decrypt and return the access token."""
        return self._decrypt(self.access_token_encrypted)
    
    def set_refresh_token(self, refresh_token):
        """Encrypt and store the refresh token."""
        self.refresh_token_encrypted = self._encrypt(refresh_token)
    
    def get_refresh_token(self):
        """Decrypt and return the refresh token."""
        if not self.refresh_token_encrypted:
            return None
        return self._decrypt(self.refresh_token_encrypted)
    
    def is_expired(self):
        """Check if the token is expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def _encrypt(self, data):
        """Encrypt data."""
        if isinstance(data, dict):
            data = json.dumps(data)
        return self._cipher.encrypt(data.encode()).decode()
    
    def _decrypt(self, encrypted_data):
        """Decrypt data."""
        decrypted = self._cipher.decrypt(encrypted_data.encode()).decode()
        try:
            return json.loads(decrypted)
        except json.JSONDecodeError:
            return decrypted
    
    def to_dict(self, include_tokens=False):
        """Convert token to dictionary."""
        result = {
            'id': self.id,
            'token_type': self.token_type,
            'scope': self.scope,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_expired': self.is_expired()
        }
        
        if include_tokens:
            result['access_token'] = self.get_access_token()
            result['refresh_token'] = self.get_refresh_token()
        
        return result
    
    def __repr__(self):
        return f'<OAuthToken {self.id} for account {self.account_id}>'
