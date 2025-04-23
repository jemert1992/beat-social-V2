# Social Media OAuth Implementation

This package contains all the necessary files to implement OAuth authentication for TikTok and Instagram in your Social Media Automation System. This implementation allows admin users to manage multiple social media accounts through a secure web interface rather than using environment variables.

## Features

- OAuth 2.0 authentication for TikTok and Instagram
- Admin dashboard for managing multiple social media accounts
- Secure token storage in a database
- Token refresh and management
- API integration using stored tokens
- User and account management

## Directory Structure

```
oauth_implementation/
├── api/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── tiktok.py
│   │   └── instagram.py
│   ├── accounts/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── app.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── account.py
│   └── token.py
├── services/
│   ├── __init__.py
│   ├── tiktok_service.py
│   └── instagram_service.py
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── auth.js
│       └── dashboard.js
├── templates/
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   ├── dashboard/
│   │   ├── index.html
│   │   ├── accounts.html
│   │   └── settings.html
│   └── base.html
├── config.py
├── requirements.txt
└── database_setup.sql
```

## Installation Instructions

1. Copy all files to your GitHub repository, maintaining the directory structure
2. Install required dependencies: `pip install -r requirements.txt`
3. Set up the database using the provided SQL script
4. Configure your TikTok and Instagram developer applications
5. Update the config.py file with your application credentials

## Configuration

You'll need to create applications in both TikTok and Instagram developer portals:

### TikTok Developer Setup

1. Go to [TikTok for Developers](https://developers.tiktok.com/)
2. Create a new application
3. Enable the Login Kit and Content Posting API
4. Set your redirect URI to `https://your-domain.com/api/auth/tiktok/callback`
5. Copy your Client Key and Client Secret to the config.py file

### Instagram Developer Setup

1. Go to [Facebook for Developers](https://developers.facebook.com/)
2. Create a new application
3. Add the Instagram Basic Display product
4. Set your redirect URI to `https://your-domain.com/api/auth/instagram/callback`
5. Copy your App ID and App Secret to the config.py file

## Usage

After installation, your system will have:

1. A login page for administrators
2. A dashboard for managing social media accounts
3. "Connect with TikTok" and "Connect with Instagram" buttons for adding accounts
4. Account management interface for viewing and managing connected accounts
5. Automatic token refresh and secure storage

## Security Considerations

- All tokens are encrypted in the database
- HTTPS is required for all OAuth redirects
- CSRF protection is implemented for all forms
- Session management with secure cookies
- Rate limiting on authentication endpoints

## API Integration

The existing TikTok and Instagram API integrations have been updated to use tokens from the database rather than environment variables. This allows for:

- Multiple account management
- Automatic token refresh
- Better error handling for authentication issues
- User-specific content posting

## Database Schema

The implementation uses three main tables:

1. `users` - Admin users who can manage accounts
2. `social_accounts` - Connected social media accounts
3. `oauth_tokens` - Securely stored access and refresh tokens

## Support

For questions or issues with this implementation, please refer to the documentation or contact support.
