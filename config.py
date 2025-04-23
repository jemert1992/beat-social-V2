"""
Configuration file for OAuth implementation.

This file contains configuration settings for the OAuth implementation,
including database connection, API credentials, and security settings.
"""

import os
from datetime import timedelta

# Flask application settings
class Config:
    # Application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-for-development')
    DEBUG = False
    TESTING = False
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    SESSION_TYPE = 'sqlalchemy'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Security settings
    CSRF_ENABLED = True
    SSL_REQUIRED = True
    
    # TikTok OAuth settings
    TIKTOK_CLIENT_KEY = os.environ.get('TIKTOK_CLIENT_KEY', '')
    TIKTOK_CLIENT_SECRET = os.environ.get('TIKTOK_CLIENT_SECRET', '')
    TIKTOK_REDIRECT_URI = os.environ.get('TIKTOK_REDIRECT_URI', 'https://your-domain.com/api/auth/tiktok/callback')
    TIKTOK_SCOPE = 'user.info.basic,video.publish'
    
    # Instagram OAuth settings
    INSTAGRAM_APP_ID = os.environ.get('INSTAGRAM_APP_ID', '')
    INSTAGRAM_APP_SECRET = os.environ.get('INSTAGRAM_APP_SECRET', '')
    INSTAGRAM_REDIRECT_URI = os.environ.get('INSTAGRAM_REDIRECT_URI', 'https://your-domain.com/api/auth/instagram/callback')
    INSTAGRAM_SCOPE = 'user_profile,user_media'
    
    # Token encryption settings
    TOKEN_ENCRYPTION_KEY = os.environ.get('TOKEN_ENCRYPTION_KEY', 'your-encryption-key-for-development')
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    DEBUG = True
    SSL_REQUIRED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'

class TestingConfig(Config):
    TESTING = True
    SSL_REQUIRED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig(Config):
    # Production settings should be configured through environment variables
    pass

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the appropriate configuration based on environment."""
    env = os.environ.get('FLASK_ENV', 'default')
    return config.get(env, config['default'])
