import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List, Dict, Optional
import logging

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None
        self.newsletters_collection = None
        self.logs_collection = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            self.client = AsyncIOMotorClient(mongodb_uri)
            self.db = self.client.newsletter_agent
            
            # Initialize collections
            self.users_collection = self.db.users
            self.newsletters_collection = self.db.newsletters
            self.logs_collection = self.db.logs
            
            # Create indexes
            await self.users_collection.create_index("email", unique=True)
            await self.newsletters_collection.create_index([("email", 1), ("created_at", -1)])
            await self.logs_collection.create_index("created_at", expireAfterSeconds=2592000)  # 30 days
            
            logging.info("Connected to MongoDB successfully")
            
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logging.info("MongoDB connection closed")
    
    async def create_user(self, user_data: Dict) -> bool:
        """Create a new user"""
        try:
            result = await self.users_collection.insert_one(user_data)
            return result.inserted_id is not None
        except Exception as e:
            logging.error(f"Error creating user: {str(e)}")
            return False
    
    async def get_user(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            user = await self.users_collection.find_one({"email": email})
            return user
        except Exception as e:
            logging.error(f"Error getting user: {str(e)}")
            return None
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users"""
        try:
            cursor = self.users_collection.find({})
            users = await cursor.to_list(length=None)
            return users
        except Exception as e:
            logging.error(f"Error getting all users: {str(e)}")
            return []
    
    async def get_active_users(self) -> List[Dict]:
        """Get all active users"""
        try:
            cursor = self.users_collection.find({"is_active": True})
            users = await cursor.to_list(length=None)
            return users
        except Exception as e:
            logging.error(f"Error getting active users: {str(e)}")
            return []
    
    async def update_user(self, email: str, update_data: Dict) -> bool:
        """Update user data"""
        try:
            result = await self.users_collection.update_one(
                {"email": email},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logging.error(f"Error updating user: {str(e)}")
            return False
    
    async def delete_user(self, email: str) -> bool:
        """Delete a user"""
        try:
            result = await self.users_collection.delete_one({"email": email})
            return result.deleted_count > 0
        except Exception as e:
            logging.error(f"Error deleting user: {str(e)}")
            return False
    
    async def save_newsletter(self, newsletter_data: Dict) -> bool:
        """Save a generated newsletter"""
        try:
            result = await self.newsletters_collection.insert_one(newsletter_data)
            return result.inserted_id is not None
        except Exception as e:
            logging.error(f"Error saving newsletter: {str(e)}")
            return False
    
    async def get_user_newsletters(self, email: str, limit: int = 10) -> List[Dict]:
        """Get newsletters for a specific user"""
        try:
            cursor = self.newsletters_collection.find(
                {"email": email}
            ).sort("created_at", -1).limit(limit)
            newsletters = await cursor.to_list(length=None)
            return newsletters
        except Exception as e:
            logging.error(f"Error getting user newsletters: {str(e)}")
            return []
    
    async def log_newsletter_generation(self, email: str, topics: List[str], news_count: int) -> bool:
        """Log newsletter generation"""
        try:
            log_data = {
                "email": email,
                "topics": topics,
                "news_count": news_count,
                "created_at": datetime.utcnow(),
                "type": "newsletter_generation"
            }
            result = await self.logs_collection.insert_one(log_data)
            return result.inserted_id is not None
        except Exception as e:
            logging.error(f"Error logging newsletter generation: {str(e)}")
            return False
    
    async def get_statistics(self) -> Dict:
        """Get system statistics"""
        try:
            total_users = await self.users_collection.count_documents({})
            active_users = await self.users_collection.count_documents({"is_active": True})
            total_newsletters = await self.newsletters_collection.count_documents({})
            
            # Get today's newsletters
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_newsletters = await self.newsletters_collection.count_documents({
                "created_at": {"$gte": today}
            })
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "total_newsletters": total_newsletters,
                "today_newsletters": today_newsletters
            }
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            return {} 