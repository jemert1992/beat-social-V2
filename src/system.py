import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import json
import datetime
import random
from src.content_analysis.analysis_manager import AnalysisManager
from src.content_creation.tiktok_creator import TikTokContentCreator
from src.content_creation.instagram_creator import InstagramContentCreator
from src.caption_hashtag.generator import CaptionHashtagGenerator
from src.scheduling.scheduler import Scheduler
from src.performance_tracking.tracker import PerformanceTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("system")

class SocialMediaAutomationSystem:
    """Main system class that coordinates all components"""
    
    def __init__(self, base_dir):
        """Initialize the system with base directory"""
        self.base_dir = base_dir
        self.data_dir = os.environ.get('DATA_DIR', os.path.join(base_dir, 'data'))
        
        # Create data directories if they don't exist
        self._create_data_directories()
        
        # Load or create default configuration
        self.config_path = os.path.join(self.data_dir, 'config', 'system_config.json')
        self.config = self._load_or_create_config()
        
        # Initialize components
        self.content_analyzer = AnalysisManager(self.data_dir, self.config)
        self.tiktok_creator = TikTokContentCreator(self.data_dir, self.config)
        self.instagram_creator = InstagramContentCreator(self.data_dir, self.config)
        self.caption_generator = CaptionHashtagGenerator(self.data_dir, self.config)
        self.scheduler = Scheduler(self.data_dir, self.config)
        self.performance_tracker = PerformanceTracker(self.data_dir, self.config)
        
        logger.info("Social Media Automation System initialized")
    
    def _create_data_directories(self):
        """Create necessary data directories"""
        directories = [
            os.path.join(self.data_dir, 'content'),
            os.path.join(self.data_dir, 'metrics'),
            os.path.join(self.data_dir, 'reports'),
            os.path.join(self.data_dir, 'config'),
            os.path.join(self.data_dir, 'logs')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        logger.info(f"Data directories created at {self.data_dir}")
    
    def _load_or_create_config(self):
        """Load existing configuration or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info("Configuration loaded from file")
                return config
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        # Create default configuration
        default_config = {
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
                    "api_secret": os.environ.get("TIKTOK_API_SECRET", "")
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
        
        # Save default configuration
        try:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=4)
            logger.info("Default configuration created")
        except Exception as e:
            logger.error(f"Error creating default configuration: {str(e)}")
        
        return default_config
    
    def configure(self, niche="general", tiktok_frequency=1, instagram_frequency=1, content_preferences=None):
        """Configure the system with user preferences"""
        self.config["niche"] = niche
        self.config["tiktok_frequency"] = tiktok_frequency
        self.config["instagram_frequency"] = instagram_frequency
        
        if content_preferences:
            self.config["content_preferences"].update(content_preferences)
        
        # Save updated configuration
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration updated")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
        
        # Update components with new configuration
        self.content_analyzer.update_config(self.config)
        self.tiktok_creator.update_config(self.config)
        self.instagram_creator.update_config(self.config)
        self.caption_generator.update_config(self.config)
        self.scheduler.update_config(self.config)
        self.performance_tracker.update_config(self.config)
        
        return self.config
    
    def generate_content_plan(self, days=7):
        """Generate a content plan for the specified number of days"""
        logger.info(f"Generating content plan for {days} days")
        
        # Analyze trends for the selected niche
        trend_analysis = self.content_analyzer.analyze_all_platforms()
        
        # Calculate number of posts needed
        tiktok_posts = days * self.config["tiktok_frequency"]
        instagram_posts = days * self.config["instagram_frequency"]
        
        # Generate content plan
        start_date = datetime.datetime.now()
        content_plan = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": (start_date + datetime.timedelta(days=days)).strftime("%Y-%m-%d"),
            "niche": self.config["niche"],
            "tiktok_posts": [],
            "instagram_posts": []
        }
        
        # Generate TikTok posts
        for i in range(tiktok_posts):
            post_date = start_date + datetime.timedelta(days=i // self.config["tiktok_frequency"])
            
            # Select a random optimal time
            optimal_times = self.config["scheduling_settings"]["tiktok_optimal_times"]
            post_time = random.choice(optimal_times)
            
            # Create post entry
            post = {
                "id": f"tt_{i+1}",
                "platform": "tiktok",
                "scheduled_date": post_date.strftime("%Y-%m-%d"),
                "scheduled_time": post_time,
                "content_type": "video" if random.random() < self.config["content_preferences"]["video_ratio"] else "image",
                "trending_topic": random.choice(trend_analysis["tiktok"]["trending_topics"]) if trend_analysis["tiktok"]["trending_topics"] else "general",
                "status": "planned"
            }
            
            content_plan["tiktok_posts"].append(post)
        
        # Generate Instagram posts
        for i in range(instagram_posts):
            post_date = start_date + datetime.timedelta(days=i // self.config["instagram_frequency"])
            
            # Select a random optimal time
            optimal_times = self.config["scheduling_settings"]["instagram_optimal_times"]
            post_time = random.choice(optimal_times)
            
            # Create post entry
            post = {
                "id": f"ig_{i+1}",
                "platform": "instagram",
                "scheduled_date": post_date.strftime("%Y-%m-%d"),
                "scheduled_time": post_time,
                "content_type": "video" if random.random() < self.config["content_preferences"]["video_ratio"] else "image",
                "trending_topic": random.choice(trend_analysis["instagram"]["trending_topics"]) if trend_analysis["instagram"]["trending_topics"] else "general",
                "status": "planned"
            }
            
            content_plan["instagram_posts"].append(post)
        
        # Save content plan
        plan_path = os.path.join(self.data_dir, 'content', f"plan_{start_date.strftime('%Y%m%d')}.json")
        try:
            with open(plan_path, 'w') as f:
                json.dump(content_plan, f, indent=4)
            logger.info(f"Content plan saved to {plan_path}")
        except Exception as e:
            logger.error(f"Error saving content plan: {str(e)}")
        
        return content_plan
    
    def execute_content_plan(self, content_plan=None):
        """Execute a content plan by creating and scheduling posts"""
        logger.info("Executing content plan")
        
        if content_plan is None:
            # Load the most recent content plan
            content_dir = os.path.join(self.data_dir, 'content')
            plan_files = [f for f in os.listdir(content_dir) if f.startswith('plan_') and f.endswith('.json')]
            
            if not plan_files:
                logger.error("No content plan found")
                return {"status": "error", "message": "No content plan found"}
            
            # Sort by date (newest first)
            plan_files.sort(reverse=True)
            
            # Load the most recent plan
            plan_path = os.path.join(content_dir, plan_files[0])
            try:
                with open(plan_path, 'r') as f:
                    content_plan = json.load(f)
                logger.info(f"Loaded content plan from {plan_path}")
            except Exception as e:
                logger.error(f"Error loading content plan: {str(e)}")
                return {"status": "error", "message": f"Error loading content plan: {str(e)}"}
        
        execution_results = {
            "tiktok_posts": [],
            "instagram_posts": []
        }
        
        # Process TikTok posts
        for post in content_plan["tiktok_posts"]:
            if post["status"] != "planned":
                continue
            
            try:
                # Generate content
                content_result = self.tiktok_creator.create_content(
                    content_type=post["content_type"],
                    topic=post["trending_topic"]
                )
                
                # Generate caption and hashtags
                caption_result = self.caption_generator.generate_for_tiktok(
                    topic=post["trending_topic"],
                    content_type=post["content_type"]
                )
                
                # Schedule post
                scheduled_result = self.scheduler.schedule_tiktok_post(
                    content_path=content_result["content_path"],
                    caption=caption_result["caption"],
                    hashtags=caption_result["hashtags"],
                    scheduled_date=post["scheduled_date"],
                    scheduled_time=post["scheduled_time"]
                )
                
                # Update post status
                post["status"] = "scheduled"
                post["content_path"] = content_result["content_path"]
                post["caption"] = caption_result["caption"]
                post["hashtags"] = caption_result["hashtags"]
                post["schedule_id"] = scheduled_result["schedule_id"]
                
                execution_results["tiktok_posts"].append({
                    "id": post["id"],
                    "status": "scheduled",
                    "scheduled_date": post["scheduled_date"],
                    "scheduled_time": post["scheduled_time"]
                })
                
                logger.info(f"TikTok post {post['id']} scheduled successfully")
            except Exception as e:
                logger.error(f"Error scheduling TikTok post {post['id']}: {str(e)}")
                post["status"] = "error"
                post["error_message"] = str(e)
                
                execution_results["tiktok_posts"].append({
                    "id": post["id"],
                    "status": "error",
                    "error_message": str(e)
                })
        
        # Process Instagram posts
        for post in content_plan["instagram_posts"]:
            if post["status"] != "planned":
                continue
            
            try:
                # Generate content
                content_result = self.instagram_creator.create_content(
                    content_type=post["content_type"],
                    topic=post["trending_topic"]
                )
                
                # Generate caption and hashtags
                caption_result = self.caption_generator.generate_for_instagram(
                    topic=post["trending_topic"],
                    content_type=post["content_type"]
                )
                
                # Schedule post
                scheduled_result = self.scheduler.schedule_instagram_post(
                    content_path=content_result["content_path"],
                    caption=caption_result["caption"],
                    hashtags=caption_result["hashtags"],
                    scheduled_date=post["scheduled_date"],
                    scheduled_time=post["scheduled_time"]
                )
                
                # Update post status
                post["status"] = "scheduled"
                post["content_path"] = content_result["content_path"]
                post["caption"] = caption_result["caption"]
                post["hashtags"] = caption_result["hashtags"]
                post["schedule_id"] = scheduled_result["schedule_id"]
                
                execution_results["instagram_posts"].append({
                    "id": post["id"],
                    "status": "scheduled",
                    "scheduled_date": post["scheduled_date"],
                    "scheduled_time": post["scheduled_time"]
                })
                
                logger.info(f"Instagram post {post['id']} scheduled successfully")
            except Exception as e:
                logger.error(f"Error scheduling Instagram post {post['id']}: {str(e)}")
                post["status"] = "error"
                post["error_message"] = str(e)
                
                execution_results["instagram_posts"].append({
                    "id": post["id"],
                    "status": "error",
                    "error_message": str(e)
                })
        
        # Save updated content plan
        plan_path = os.path.join(self.data_dir, 'content', f"plan_{content_plan['start_date'].replace('-', '')}_updated.json")
        try:
            with open(plan_path, 'w') as f:
                json.dump(content_plan, f, indent=4)
            logger.info(f"Updated content plan saved to {plan_path}")
        except Exception as e:
            logger.error(f"Error saving updated content plan: {str(e)}")
        
        return execution_results
    
    def generate_weekly_report(self):
        """Generate a weekly performance report"""
        logger.info("Generating weekly performance report")
        
        # Get performance metrics
        metrics = self.performance_tracker.get_weekly_metrics()
        
        # Generate report
        report = {
            "generated_date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "period_start": metrics["period_start"],
            "period_end": metrics["period_end"],
            "tiktok_metrics": metrics["tiktok"],
            "instagram_metrics": metrics["instagram"],
            "overall_performance": metrics["overall"],
            "recommendations": self._generate_recommendations(metrics)
        }
        
        # Save report
        report_path = os.path.join(self.data_dir, 'reports', f"weekly_report_{report['period_end'].replace('-', '')}.json")
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=4)
            logger.info(f"Weekly report saved to {report_path}")
        except Exception as e:
            logger.error(f"Error saving weekly report: {str(e)}")
        
        return report_path
    
    def _generate_recommendations(self, metrics):
        """Generate recommendations based on performance metrics"""
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
        
        return recommendations
    
    def get_system_status(self):
        """Get the current system status"""
        return {
            "status": "online",
            "version": "1.0.0",
            "config": self.config,
            "data_dir": self.data_dir,
            "components": {
                "content_analyzer": "active",
                "tiktok_creator": "active",
                "instagram_creator": "active",
                "caption_generator": "active",
                "scheduler": "active",
                "performance_tracker": "active"
            }
        }
