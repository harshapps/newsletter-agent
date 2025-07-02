from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import uvicorn
import os
from dotenv import load_dotenv
import asyncio
import schedule
import time
from datetime import datetime
import threading
import logging

from database.mongodb import MongoDB
from agents.crew_manager import CrewManager
from services.email_service import EmailService
from services.news_service import NewsService

# Load environment variables
load_dotenv()
print(f"[DEBUG] NEWS_API_KEY at startup: {os.getenv('NEWS_API_KEY')}")

app = FastAPI(
    title="Newsletter Agent MCP",
    description="AI-powered newsletter agent using multi-agent systems and MCP",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = MongoDB()
crew_manager = CrewManager()
email_service = EmailService()
news_service = NewsService()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    topics: List[str]
    news_sources: List[str] = ["yahoo_finance", "newsapi", "rss"]
    delivery_time: str = "09:00"

class NewsletterRequest(BaseModel):
    email: EmailStr
    topics: List[str]

class NewsletterGenerationRequest(BaseModel):
    topics: List[str]
    email: Optional[EmailStr] = None
    news_source: Optional[str] = "Auto"

class MCPToolTestRequest(BaseModel):
    tool_name: str
    parameters: dict = {}

class TestEmailRequest(BaseModel):
    email: EmailStr

@app.on_event("startup")
async def startup_event():
    """Initialize database and start scheduler on startup"""
    await db.connect()
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    await db.close()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Newsletter Agent MCP API",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "Multi-Agent AI System (CrewAI)",
            "Model Context Protocol (MCP) Tools",
            "Personalized News Curation",
            "Automated Email Delivery",
            "Multiple News Sources"
        ]
    }

@app.post("/register")
async def register_user(user: UserRegistration):
    """Register a new user for newsletter"""
    try:
        # Check if user already exists
        existing_user = await db.get_user(user.email)
        if existing_user:
            # Update existing user preferences
            await db.update_user(user.email, {
                "topics": user.topics,
                "news_sources": user.news_sources,
                "delivery_time": user.delivery_time,
                "updated_at": datetime.utcnow()
            })
            return {"message": "User preferences updated successfully", "email": user.email}
        
        # Create new user
        user_data = {
            "email": user.email,
            "topics": user.topics,
            "news_sources": user.news_sources,
            "delivery_time": user.delivery_time,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True
        }
        await db.create_user(user_data)
        
        return {"message": "User registered successfully", "email": user.email}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/generate-newsletter")
async def generate_newsletter(request: NewsletterRequest, background_tasks: BackgroundTasks):
    """Generate a personalized newsletter for a user"""
    try:
        # Get user data
        user = await db.get_user(request.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get news from multiple sources
        news_result = await news_service.get_news_for_topics(request.topics or user.get("topics", []))
        news_data = news_result["news"]
        sources_used = news_result["sources_used"]
        date_fetched = news_result["date_fetched"]
        
        # Generate newsletter in background
        background_tasks.add_task(
            generate_and_send_newsletter,
            request.email,
            request.topics or user.get("topics", []),
            news_data,
            sources_used,
            date_fetched
        )
        
        return {"message": "Newsletter generation started", "email": request.email, "sources_used": sources_used, "date_fetched": date_fetched}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Newsletter generation failed: {str(e)}")

@app.post("/test-newsletter")
async def test_newsletter_generation(request: NewsletterRequest):
    """Test newsletter generation without background tasks"""
    try:
        print(f"Starting newsletter generation for {request.email}")
        
        # Get user data
        user = await db.get_user(request.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"User found: {user}")
        
        # Get news from multiple sources
        print("Fetching news data...")
        news_result = await news_service.get_news_for_topics(request.topics or user.get("topics", []))
        news_data = news_result["news"]
        sources_used = news_result["sources_used"]
        date_fetched = news_result["date_fetched"]
        print(f"Fetched {len(news_data)} news items from sources: {sources_used}")
        
        # Use CrewAI to generate newsletter content
        print("Generating newsletter content...")
        newsletter_content = await crew_manager.generate_newsletter(
            email=request.email,
            topics=request.topics or user.get("topics", []),
            news_data=news_data,
            sources_used=sources_used,
            date_fetched=date_fetched
        )
        
        print("Newsletter generated successfully")
        
        return {
            "message": "Newsletter generated successfully",
            "email": request.email,
            "news_count": len(news_data),
            "sources_used": sources_used,
            "date_fetched": date_fetched,
            "newsletter": newsletter_content
        }
    
    except Exception as e:
        import traceback
        print(f"Error in newsletter generation: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Newsletter generation failed: {str(e)}")

@app.post("/generate-newsletter-content")
async def generate_newsletter_content(request: NewsletterGenerationRequest):
    """Generate newsletter content without requiring email registration"""
    try:
        print(f"Starting newsletter generation for topics: {request.topics}")
        print(f"Using news source: {request.news_source}")
        
        # Get user data (optional - user doesn't need to be registered)
        if request.email:
            user = await db.get_user(str(request.email))
            # Don't require user to exist - just use None if not found
        else:
            user = None
        
        # Get news from multiple sources
        print("Fetching news data...")
        news_result = await news_service.get_news_for_topics(
            request.topics or (user.get("topics", []) if user else []),
            preferred_source=request.news_source or "Auto"
        )
        news_data = news_result["news"]
        sources_used = news_result["sources_used"]
        date_fetched = news_result["date_fetched"]
        print(f"Fetched {len(news_data)} news items from sources: {sources_used}")
        
        # Use CrewAI to generate newsletter content
        print("Generating newsletter content...")
        newsletter_content = await crew_manager.generate_newsletter(
            email=request.email or "anonymous@example.com",
            topics=request.topics,
            news_data=news_data,
            sources_used=sources_used,
            date_fetched=date_fetched
        )
        
        print("Newsletter generated successfully")
        
        return {
            "message": "Newsletter generated successfully",
            "topics": request.topics,
            "news_source": request.news_source,
            "news_count": len(news_data),
            "sources_used": sources_used,
            "date_fetched": date_fetched,
            "newsletter": newsletter_content
        }
    
    except Exception as e:
        import traceback
        print(f"Error in newsletter generation: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Newsletter generation failed: {str(e)}")

@app.get("/users")
async def get_users():
    """Get all registered users (for admin purposes)"""
    try:
        users = await db.get_all_users()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@app.delete("/users/{email}")
async def delete_user(email: str):
    """Delete a user"""
    try:
        result = await db.delete_user(email)
        if result:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")

# MCP-related endpoints
@app.get("/mcp/tools")
async def get_mcp_tools():
    """Get list of available MCP tools"""
    try:
        tools = await crew_manager.get_available_mcp_tools()
        return {
            "message": "Available MCP Tools",
            "tools": tools,
            "total_tools": len(tools)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get MCP tools: {str(e)}")

@app.post("/mcp/test-tool")
async def test_mcp_tool(request: MCPToolTestRequest):
    """Test a specific MCP tool"""
    try:
        result = await crew_manager.test_mcp_tool(request.tool_name, **request.parameters)
        return {
            "message": f"MCP Tool Test Result: {request.tool_name}",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test MCP tool: {str(e)}")

@app.get("/mcp/demo")
async def mcp_demo():
    """Demo MCP tools functionality"""
    try:
        # Demo different MCP tools
        demos = {}
        
        # Test news fetching
        news_result = await crew_manager.test_mcp_tool("fetch_news", topics=["technology"])
        demos["news_fetching"] = news_result
        
        # Test stock data
        stock_result = await crew_manager.test_mcp_tool("fetch_stock_data", symbols=["AAPL", "GOOGL"])
        demos["stock_data"] = stock_result
        
        # Test trend analysis
        if news_result.get("success") and news_result.get("data"):
            trend_result = await crew_manager.test_mcp_tool("analyze_trends", news_data=news_result["data"].get("articles", []))
            demos["trend_analysis"] = trend_result
        
        return {
            "message": "MCP Tools Demo",
            "demos": demos,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run MCP demo: {str(e)}")

@app.get("/stats")
async def get_statistics():
    """Get system statistics"""
    try:
        db_stats = await db.get_statistics()
        mcp_tools = await crew_manager.get_available_mcp_tools()
        
        return {
            "database_stats": db_stats,
            "mcp_tools_count": len(mcp_tools),
            "available_mcp_tools": [tool["name"] for tool in mcp_tools],
            "system_status": "running",
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.post("/send-newsletter")
async def send_newsletter(request: dict):
    """Send newsletter via email"""
    try:
        email = request.get("email")
        newsletter_data = request.get("newsletter_data")
        
        if not email or not newsletter_data:
            return {"error": "Email and newsletter data are required"}
        
        # Send the newsletter
        success = await email_service.send_newsletter(email, newsletter_data)
        
        if success:
            return {"message": "Newsletter sent successfully", "email": email}
        else:
            return {"error": "Failed to send newsletter"}
            
    except Exception as e:
        logging.error(f"Error sending newsletter: {str(e)}")
        return {"error": f"Internal server error: {str(e)}"}

@app.post("/test-email")
async def test_email(request: TestEmailRequest):
    """Test email configuration by sending a test email"""
    try:
        # Send a test email
        success = await email_service.send_test_email(request.email)
        
        if success:
            return {
                "message": "Test email sent successfully", 
                "email": request.email,
                "status": "success"
            }
        else:
            return {
                "error": "Failed to send test email. Check your email configuration.",
                "email": request.email,
                "status": "failed"
            }
            
    except Exception as e:
        logging.error(f"Error sending test email: {str(e)}")
        return {
            "error": f"Test email failed: {str(e)}",
            "email": request.email,
            "status": "error"
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

async def generate_and_send_newsletter(email: str, topics: List[str], news_data=None, sources_used=None, date_fetched=None):
    """Generate and send newsletter for a user"""
    try:
        # If not provided, fetch news
        if news_data is None or sources_used is None or date_fetched is None:
            news_result = await news_service.get_news_for_topics(topics)
            news_data = news_result["news"]
            sources_used = news_result["sources_used"]
            date_fetched = news_result["date_fetched"]
        
        # Use CrewAI to generate newsletter content
        newsletter_content = await crew_manager.generate_newsletter(
            email=email,
            topics=topics,
            news_data=news_data,
            sources_used=sources_used,
            date_fetched=date_fetched
        )
        
        # Send email
        await email_service.send_newsletter(email, newsletter_content)
        
        # Log the newsletter generation
        await db.log_newsletter_generation(email, topics, len(news_data))
        
    except Exception as e:
        print(f"Error generating newsletter for {email}: {str(e)}")

def start_scheduler():
    """Start the scheduler for daily newsletter delivery"""
    def run_scheduler():
        schedule.every().day.at("09:00").do(daily_newsletter_delivery)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    # Run scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

async def daily_newsletter_delivery():
    """Send newsletters to all active users"""
    try:
        users = await db.get_active_users()
        
        for user in users:
            if user.get("is_active", False):
                await generate_and_send_newsletter(
                    user["email"],
                    user.get("topics", []),
                    user.get("news_data"),
                    user.get("sources_used"),
                    user.get("date_fetched")
                )
        
        print(f"Daily newsletter delivery completed for {len(users)} users")
    
    except Exception as e:
        print(f"Error in daily newsletter delivery: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 