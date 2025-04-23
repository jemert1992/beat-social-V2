"""
Main application file for the OAuth implementation.

This module initializes the Flask application and registers all blueprints.
"""

import os
import logging
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import get_config
from models import db, OAuthToken
from services.token_service import TokenStorageService
from api.auth.routes import auth_routes
from api.auth.tiktok import tiktok_bp
from api.auth.instagram import instagram_bp
from api.accounts.routes import accounts_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """
    Create and configure the Flask application.
    
    Args:
        config_name: The configuration to use (default, development, testing, production)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(get_config())
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    Session(app)
    
    # Initialize rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["100 per hour"],
        storage_uri="memory://"
    )
    
    # Initialize token encryption
    with app.app_context():
        token_service = TokenStorageService(app.config.get('TOKEN_ENCRYPTION_KEY'))
    
    # Register blueprints
    app.register_blueprint(auth_routes, url_prefix='/auth')
    app.register_blueprint(tiktok_bp, url_prefix='/auth/tiktok')
    app.register_blueprint(instagram_bp, url_prefix='/auth/instagram')
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    
    # Create database tables
    @app.before_first_request
    def create_tables():
        db.create_all()
    
    # Home route
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {str(e)}")
        return render_template('errors/500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
