"""
Modified app.py with catch-all route for Vercel deployment.
This file includes all the TikTok API integration functionality.
"""

import os
import json
import logging
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add current directory to path to help with imports
sys.path.append('.')

# Import TikTok integration
try:
    from api.tiktok_api import TikTokAPI
    from api.tiktok_service import TikTokService
except ImportError:
    # Fallback import method
    sys.path.append('./api')
    from tiktok_api import TikTokAPI
    from tiktok_service import TikTokService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize TikTok service
tiktok_service = TikTokService()

# Default configuration
DEFAULT_CONFIG = {
    "instagram_frequency": 1,  # posts per day
    "content_preferences": {
        "video_ratio": 0.7,  # 70% videos, 30% images
        "trending_ratio": 0.8,  # 80% trending, 20% evergreen
        "reuse_ratio": 0.3  # 30% content can be reused across platforms
    },
    "api_credentials": {
        "tiktok": {
            "api_key": os.environ.get("TIKTOK_API_KEY", ""),
            "api_secret": os.environ.get("SOCIAL_MEDIA_TOKEN", "")
        },
        "instagram": {
            "username": os.environ.get("INSTAGRAM_USERNAME", ""),
            "password": os.environ.get("INSTAGRAM_PASSWORD", "")
        }
    },
    "hashtag_settings": {
        "min_count": 3,
        "max_count": 10,
        "trending_ratio": 0.6  # 60% trending, 40% niche
    },
    "scheduling_settings": {
        "tiktok_optimal_times": ["12:00", "18:00", "21:00"],
        "instagram_optimal_times": ["9:00", "13:00", "19:00"],
        "timezone": "UTC"
    }
}

# In-memory storage for demo purposes
# In a production environment, this would be a database
STORAGE = {
    "config": DEFAULT_CONFIG.copy(),
    "plans": [],
    "reports": []
}

@app.route('/')
def index():
    """Root endpoint that returns API status and available endpoints."""
    return jsonify({
        "endpoints": ["/api/status", "/api/configure", "/api/plan", "/api/execute", "/api/report", "/api/tiktok/post", "/api/tiktok/account"],
        "message": "Social Media Automation API is running",
        "status": "online"
    })

@app.route('/api/status', methods=['GET'])
def status():
    """Get the current status of the API."""
    return jsonify({
        "status": "online",
        "config": STORAGE["config"],
        "message": "Social Media Automation API is operational"
    })

@app.route('/api/configure', methods=['POST'])
def configure():
    """Configure the social media automation settings."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No configuration data provided"}), 400
        
        # Update configuration with provided data
        for key, value in data.items():
            if key in STORAGE["config"]:
                if isinstance(value, dict) and isinstance(STORAGE["config"][key], dict):
                    STORAGE["config"][key].update(value)
                else:
                    STORAGE["config"][key] = value
        
        return jsonify({
            "success": True,
            "message": "Configuration updated successfully",
            "config": STORAGE["config"]
        })
    except Exception as e:
        logger.error(f"Error in configure: {str(e)}")
        return jsonify({"success": False, "message": f"Configuration error: {str(e)}"}), 500

@app.route('/api/plan', methods=['POST'])
def create_plan():
    """Create a content posting plan based on the current configuration."""
    try:
        data = request.json or {}
        niche = data.get('niche', 'general')
        duration = data.get('duration', 7)  # Default to 7 days
        
        # In a real implementation, this would generate a detailed content plan
        # For demo purposes, we'll create a simple plan
        plan = {
            "id": len(STORAGE["plans"]) + 1,
            "niche": niche,
            "duration": duration,
            "posts": [
                {
                    "platform": "tiktok",
                    "content_type": "video",
                    "scheduled_time": "2025-04-24T12:00:00Z",
                    "status": "pending"
                },
                {
                    "platform": "instagram",
                    "content_type": "image",
                    "scheduled_time": "2025-04-24T13:00:00Z",
                    "status": "pending"
                }
            ]
        }
        
        STORAGE["plans"].append(plan)
        
        return jsonify({
            "success": True,
            "message": "Content plan created successfully",
            "plan": plan
        })
    except Exception as e:
        logger.error(f"Error in create_plan: {str(e)}")
        return jsonify({"success": False, "message": f"Planning error: {str(e)}"}), 500

@app.route('/api/execute', methods=['POST'])
def execute_plan():
    """Execute a content posting plan."""
    try:
        data = request.json or {}
        plan_id = data.get('plan_id')
        
        if not plan_id:
            return jsonify({"success": False, "message": "No plan ID provided"}), 400
        
        # Find the plan
        plan = None
        for p in STORAGE["plans"]:
            if p["id"] == plan_id:
                plan = p
                break
        
        if not plan:
            return jsonify({"success": False, "message": f"Plan with ID {plan_id} not found"}), 404
        
        # In a real implementation, this would actually post content
        # For demo purposes, we'll just update the status
        for post in plan["posts"]:
            post["status"] = "completed"
        
        return jsonify({
            "success": True,
            "message": "Plan executed successfully",
            "plan": plan
        })
    except Exception as e:
        logger.error(f"Error in execute_plan: {str(e)}")
        return jsonify({"success": False, "message": f"Execution error: {str(e)}"}), 500

@app.route('/api/report', methods=['GET'])
def get_report():
    """Get a performance report."""
    try:
        # In a real implementation, this would generate a detailed performance report
        # For demo purposes, we'll create a simple report
        report = {
            "id": len(STORAGE["reports"]) + 1,
            "period": "last_7_days",
            "platforms": {
                "tiktok": {
                    "posts": 5,
                    "views": 10000,
                    "likes": 500,
                    "comments": 50,
                    "shares": 20
                },
                "instagram": {
                    "posts": 3,
                    "impressions": 5000,
                    "likes": 300,
                    "comments": 30,
                    "saves": 10
                }
            },
            "top_performing_content": [
                {
                    "platform": "tiktok",
                    "content_id": "123456",
                    "views": 5000,
                    "engagement_rate": 0.05
                }
            ]
        }
        
        STORAGE["reports"].append(report)
        
        return jsonify({
            "success": True,
            "message": "Report generated successfully",
            "report": report
        })
    except Exception as e:
        logger.error(f"Error in get_report: {str(e)}")
        return jsonify({"success": False, "message": f"Reporting error: {str(e)}"}), 500

# TikTok API Integration Endpoints

@app.route('/api/tiktok/post', methods=['POST'])
def post_to_tiktok():
    """Post content to TikTok using the TikTok API integration."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data provided"}), 400
        
        video_url = data.get('video_url')
        if not video_url:
            return jsonify({"success": False, "message": "No video URL provided"}), 400
        
        caption = data.get('caption', '')
        hashtags = data.get('hashtags', [])
        
        # Use the TikTok service to post the video
        response = tiktok_service.post_video(video_url, caption, hashtags)
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in post_to_tiktok: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to post to TikTok: {str(e)}",
            "error": str(e)
        }), 500

@app.route('/api/tiktok/account', methods=['GET'])
def get_tiktok_account():
    """Get information about the authenticated TikTok account."""
    try:
        # Use the TikTok service to get account information
        response = tiktok_service.get_account_info()
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in get_tiktok_account: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"Failed to get TikTok account information: {str(e)}",
            "error": str(e)
        }), 500

# Critical for Vercel: Catch-all route to handle all other routes
@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route to handle any undefined routes."""
    return jsonify({"error": "Route not found", "path": path}), 404

# For local development
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
