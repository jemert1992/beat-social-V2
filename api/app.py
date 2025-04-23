from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os
import json
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api")

# Initialize Flask app
app = Flask(__name__)

# Configuration
DEFAULT_CONFIG = {
    "niche": "general",
    "tiktok_frequency": 1,  # posts per day
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
    "content_plans": [],
    "scheduled_posts": [],
    "metrics": {
        "tiktok": {
            "views": random.randint(1000, 10000),
            "likes": random.randint(100, 1000),
            "comments": random.randint(10, 100),
            "shares": random.randint(5, 50),
            "followers": random.randint(100, 5000),
            "follower_growth": random.randint(-10, 100),
            "engagement_rate": round(random.uniform(0.01, 0.1), 4),
            "video_performance": round(random.uniform(0.5, 1.0), 2),
            "image_performance": round(random.uniform(0.3, 0.9), 2)
        },
        "instagram": {
            "views": random.randint(1000, 10000),
            "likes": random.randint(100, 1000),
            "comments": random.randint(10, 100),
            "shares": random.randint(5, 50),
            "followers": random.randint(100, 5000),
            "follower_growth": random.randint(-10, 100),
            "engagement_rate": round(random.uniform(0.01, 0.1), 4),
            "video_performance": round(random.uniform(0.3, 0.9), 2),
            "image_performance": round(random.uniform(0.5, 1.0), 2)
        },
        "overall": {
            "total_posts": random.randint(10, 100),
            "average_engagement": round(random.uniform(0.01, 0.1), 4),
            "best_performing_platform": random.choice(["tiktok", "instagram"]),
            "best_performing_content_type": random.choice(["video", "image"]),
            "best_performing_topic": random.choice(["fashion", "fitness", "food", "travel", "technology"])
        }
    }
}

# Sample trending topics for demo
TRENDING_TOPICS = {
    "tiktok": {
        "trending_topics": [
            "dance_challenge", "life_hack", "cooking_tutorial", 
            "fitness_routine", "comedy_skit", "day_in_life",
            "product_review", "transformation", "prank"
        ],
        "trending_hashtags": [
            "#fyp", "#viral", "#trending", "#tiktok", 
            "#challenge", "#duet", "#foryou", "#foryoupage"
        ]
    },
    "instagram": {
        "trending_topics": [
            "outfit_of_day", "food_photography", "travel_destination", 
            "fitness_motivation", "home_decor", "beauty_tutorial",
            "lifestyle_tips", "pet_feature", "inspirational_quote"
        ],
        "trending_hashtags": [
            "#instagood", "#photooftheday", "#love", "#fashion", 
            "#beautiful", "#happy", "#cute", "#follow"
        ]
    }
}

# API Routes
@app.route('/')
def home():
    """Home page route"""
    return jsonify({
        "status": "online",
        "message": "Social Media Automation API is running",
        "endpoints": [
            "/api/status",
            "/api/configure",
            "/api/plan",
            "/api/execute",
            "/api/report"
        ]
    })

@app.route('/api/status')
def status():
    """Check system status"""
    return jsonify({
        "status": "online",
        "version": "1.0.0",
        "config": STORAGE["config"],
        "metrics": {
            "tiktok_posts": len([p for p in STORAGE["scheduled_posts"] if p["platform"] == "tiktok"]),
            "instagram_posts": len([p for p in STORAGE["scheduled_posts"] if p["platform"] == "instagram"]),
            "total_posts": len(STORAGE["scheduled_posts"])
        }
    })

@app.route('/api/configure', methods=['POST'])
def configure():
    """Configure the system"""
    data = request.json
    
    try:
        STORAGE["config"]["niche"] = data.get('niche', STORAGE["config"]["niche"])
        STORAGE["config"]["tiktok_frequency"] = int(data.get('tiktok_frequency', STORAGE["config"]["tiktok_frequency"]))
        STORAGE["config"]["instagram_frequency"] = int(data.get('instagram_frequency', STORAGE["config"]["instagram_frequency"]))
        
        if 'content_preferences' in data:
            STORAGE["config"]["content_preferences"].update(data['content_preferences'])
        
        logger.info("System configured successfully")
        return jsonify({"status": "success", "message": "System configured successfully", "config": STORAGE["config"]})
    except Exception as e:
        logger.error(f"Configuration error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/plan', methods=['POST'])
def generate_plan():
    """Generate a content plan"""
    data = request.json
    
    try:
        days = int(data.get('days', 7))
        
        # Analyze trends (simulated)
        trend_analysis = TRENDING_TOPICS
        
        # Calculate number of posts needed
        tiktok_posts = days * STORAGE["config"]["tiktok_frequency"]
        instagram_posts = days * STORAGE["config"]["instagram_frequency"]
        
        # Generate content plan
        start_date = datetime.now()
        content_plan = {
            "id": f"plan_{start_date.strftime('%Y%m%d%H%M%S')}",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": (start_date + timedelta(days=days)).strftime("%Y-%m-%d"),
            "niche": STORAGE["config"]["niche"],
            "tiktok_posts": [],
            "instagram_posts": []
        }
        
        # Generate TikTok posts
        for i in range(tiktok_posts):
            post_date = start_date + timedelta(days=i // STORAGE["config"]["tiktok_frequency"])
            
            # Select a random optimal time
            optimal_times = STORAGE["config"]["scheduling_settings"]["tiktok_optimal_times"]
            post_time = random.choice(optimal_times)
            
            # Create post entry
            post = {
                "id": f"tt_{start_date.strftime('%Y%m%d')}_{i+1}",
                "platform": "tiktok",
                "scheduled_date": post_date.strftime("%Y-%m-%d"),
                "scheduled_time": post_time,
                "content_type": "video" if random.random() < STORAGE["config"]["content_preferences"]["video_ratio"] else "image",
                "trending_topic": random.choice(trend_analysis["tiktok"]["trending_topics"]),
                "status": "planned"
            }
            
            content_plan["tiktok_posts"].append(post)
        
        # Generate Instagram posts
        for i in range(instagram_posts):
            post_date = start_date + timedelta(days=i // STORAGE["config"]["instagram_frequency"])
            
            # Select a random optimal time
            optimal_times = STORAGE["config"]["scheduling_settings"]["instagram_optimal_times"]
            post_time = random.choice(optimal_times)
            
            # Create post entry
            post = {
                "id": f"ig_{start_date.strftime('%Y%m%d')}_{i+1}",
                "platform": "instagram",
                "scheduled_date": post_date.strftime("%Y-%m-%d"),
                "scheduled_time": post_time,
                "content_type": "video" if random.random() < STORAGE["config"]["content_preferences"]["video_ratio"] else "image",
                "trending_topic": random.choice(trend_analysis["instagram"]["trending_topics"]),
                "status": "planned"
            }
            
            content_plan["instagram_posts"].append(post)
        
        # Save content plan
        STORAGE["content_plans"].append(content_plan)
        
        logger.info(f"Content plan generated with {tiktok_posts} TikTok posts and {instagram_posts} Instagram posts")
        return jsonify({"status": "success", "plan": content_plan})
    except Exception as e:
        logger.error(f"Plan generation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/execute', methods=['POST'])
def execute_plan():
    """Execute a content plan"""
    data = request.json
    
    try:
        plan_id = data.get('plan_id')
        
        # Find the content plan
        content_plan = None
        if plan_id:
            for plan in STORAGE["content_plans"]:
                if plan["id"] == plan_id:
                    content_plan = plan
                    break
        else:
            # Use the most recent plan
            if STORAGE["content_plans"]:
                content_plan = STORAGE["content_plans"][-1]
        
        if not content_plan:
            return jsonify({"status": "error", "message": "No content plan found"}), 404
        
        execution_results = {
            "tiktok_posts": [],
            "instagram_posts": []
        }
        
        # Process TikTok posts
        for post in content_plan["tiktok_posts"]:
            if post["status"] != "planned":
                continue
            
            # Simulate content creation
            content_path = f"/simulated/content/tiktok/{post['id']}.mp4" if post["content_type"] == "video" else f"/simulated/content/tiktok/{post['id']}.jpg"
            
            # Generate caption and hashtags
            caption = f"Check out this {post['trending_topic']} content! #trending #{post['trending_topic'].replace('_', '')}"
            hashtags = random.sample(TRENDING_TOPICS["tiktok"]["trending_hashtags"], random.randint(3, 6))
            
            # Schedule post (simulated)
            schedule_id = f"sched_{post['id']}"
            
            # Update post status
            post["status"] = "scheduled"
            post["content_path"] = content_path
            post["caption"] = caption
            post["hashtags"] = hashtags
            post["schedule_id"] = schedule_id
            
            # Add to scheduled posts
            STORAGE["scheduled_posts"].append({
                "id": post["id"],
                "platform": "tiktok",
                "scheduled_date": post["scheduled_date"],
                "scheduled_time": post["scheduled_time"],
                "content_path": content_path,
                "caption": caption,
                "hashtags": hashtags,
                "schedule_id": schedule_id,
                "status": "scheduled"
            })
            
            execution_results["tiktok_posts"].append({
                "id": post["id"],
                "status": "scheduled",
                "scheduled_date": post["scheduled_date"],
                "scheduled_time": post["scheduled_time"]
            })
        
        # Process Instagram posts
        for post in content_plan["instagram_posts"]:
            if post["status"] != "planned":
                continue
            
            # Simulate content creation
            content_path = f"/simulated/content/instagram/{post['id']}.mp4" if post["content_type"] == "video" else f"/simulated/content/instagram/{post['id']}.jpg"
            
            # Generate caption and hashtags
            caption = f"Enjoying this {post['trending_topic']} moment! #instagram #{post['trending_topic'].replace('_', '')}"
            hashtags = random.sample(TRENDING_TOPICS["instagram"]["trending_hashtags"], random.randint(3, 6))
            
            # Schedule post (simulated)
            schedule_id = f"sched_{post['id']}"
            
            # Update post status
            post["status"] = "scheduled"
            post["content_path"] = content_path
            post["caption"] = caption
            post["hashtags"] = hashtags
            post["schedule_id"] = schedule_id
            
            # Add to scheduled posts
            STORAGE["scheduled_posts"].append({
                "id": post["id"],
                "platform": "instagram",
                "scheduled_date": post["scheduled_date"],
                "scheduled_time": post["scheduled_time"],
                "content_path": content_path,
                "caption": caption,
                "hashtags": hashtags,
                "schedule_id": schedule_id,
                "status": "scheduled"
            })
            
            execution_results["instagram_posts"].append({
                "id": post["id"],
                "status": "scheduled",
                "scheduled_date": post["scheduled_date"],
                "scheduled_time": post["scheduled_time"]
            })
        
        logger.info(f"Content plan executed with {len(execution_results['tiktok_posts'])} TikTok posts and {len(execution_results['instagram_posts'])} Instagram posts")
        return jsonify({"status": "success", "results": execution_results})
    except Exception as e:
        logger.error(f"Plan execution error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/report', methods=['GET'])
def generate_report():
    """Generate a performance report"""
    try:
        # Get performance metrics (simulated)
        metrics = STORAGE["metrics"]
        
        # Generate recommendations
        recommendations = []
        
        # TikTok recommendations
        if metrics["tiktok"]["engagement_rate"] < 0.02:
            recommendations.append("TikTok engagement is low. Consider creating more trending content.")
        
        if metrics["tiktok"]["follower_growth"] < 0:
            recommendations.append("TikTok followers are decreasing. Review content strategy and posting frequency.")
        
        # Instagram recommendations
        if metrics["instagram"]["engagement_rate"] < 0.03:
            recommendations.append("Instagram engagement is low. Try using more relevant hashtags.")
        
        if metrics["instagram"]["follower_growth"] < 0:
            recommendations.append("Instagram followers are decreasing. Consider posting more consistently.")
        
        # Content type recommendations
        if metrics["tiktok"]["video_performance"] > metrics["tiktok"]["image_performance"]:
            recommendations.append("Videos are performing better than images on TikTok. Increase video ratio.")
        
        if metrics["instagram"]["image_performance"] > metrics["instagram"]["video_performance"]:
            recommendations.append("Images are performing better than videos on Instagram. Increase image ratio.")
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("All metrics look good. Continue with the current strategy.")
        
        # Generate report
        report = {
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "period_start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "period_end": datetime.now().strftime("%Y-%m-%d"),
            "tiktok_metrics": metrics["tiktok"],
            "instagram_metrics": metrics["instagram"],
            "overall_performance": metrics["overall"],
            "recommendations": recommendations
        }
        
        logger.info("Performance report generated")
        return jsonify({"status": "success", "report": report})
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 400

# For local testing
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
