#!/usr/bin/env python3
"""
Test script to verify news service functionality without NewsAPI key
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.append('backend')

# Load environment variables
load_dotenv()

async def test_news_service_without_newsapi():
    """Test the news service when NewsAPI key is not available"""
    print("🧪 Testing news service without NewsAPI key...")
    
    try:
        from backend.services.news_service import NewsService
        
        # Create news service instance
        news_service = NewsService()
        
        # Test topics
        test_topics = ["sports", "technology"]
        
        print(f"📰 Fetching news for topics: {test_topics}")
        print(f"🔑 NewsAPI available: {news_service.newsapi_available}")
        
        # Get news
        news_data, sources_used = await news_service.get_news_for_topics(test_topics, preferred_source="Auto")
        
        print(f"✅ Sources used: {sources_used}")
        print(f"📊 Found {len(news_data)} news items")
        
        # Display the news
        for i, article in enumerate(news_data[:5], 1):  # Show first 5 articles
            print(f"\n--- Article {i} ---")
            print(f"Title: {article.get('title', 'No title')}")
            print(f"Summary: {article.get('summary', 'No summary')[:200]}...")
            print(f"Source: {article.get('source', 'Unknown')}")
            print(f"URL: {article.get('url', 'No URL')}")
            print(f"News Source: {article.get('news_source', 'Unknown')}")
        
        # Check if we got helpful messages instead of fake news
        has_helpful_message = any(
            "News Service Temporarily Unavailable" in article.get('title', '') or
            "Setup NewsAPI" in article.get('title', '')
            for article in news_data
        )
        
        if has_helpful_message:
            print("\n✅ SUCCESS: System provided helpful messages instead of fake news")
            return True
        else:
            print("\n❌ FAIL: System should provide helpful messages when NewsAPI is unavailable")
            return False
        
    except Exception as e:
        print(f"❌ Error testing news service: {str(e)}")
        return False

async def test_rss_feeds():
    """Test RSS feeds functionality"""
    print("\n🧪 Testing RSS feeds functionality...")
    
    try:
        from backend.services.news_service import NewsService
        
        news_service = NewsService()
        
        # Test RSS feeds directly
        rss_news = await news_service._get_rss_news(["sports", "technology"])
        
        print(f"📊 Found {len(rss_news)} RSS articles")
        
        if rss_news:
            print("✅ SUCCESS: RSS feeds are working")
            for i, article in enumerate(rss_news[:3], 1):
                print(f"  {i}. {article.get('title', 'No title')} - {article.get('source', 'Unknown')}")
            return True
        else:
            print("❌ FAIL: No RSS articles found")
            return False
        
    except Exception as e:
        print(f"❌ Error testing RSS feeds: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting news service tests without NewsAPI key...")
    
    # Check if NEWS_API_KEY is set
    if os.getenv('NEWS_API_KEY'):
        print("⚠️  NEWS_API_KEY is set. For this test, please temporarily remove it from .env file")
        print("   This test is designed to verify behavior when the key is missing")
        return
    
    # Run tests
    news_service_success = await test_news_service_without_newsapi()
    rss_success = await test_rss_feeds()
    
    print("\n📋 Test Results:")
    print(f"News Service (no NewsAPI): {'✅ PASS' if news_service_success else '❌ FAIL'}")
    print(f"RSS Feeds: {'✅ PASS' if rss_success else '❌ FAIL'}")
    
    if news_service_success and rss_success:
        print("\n🎉 All tests passed! News service handles missing NewsAPI key gracefully.")
        print("\n💡 To get NewsAPI functionality:")
        print("   1. Get a free API key from https://newsapi.org/")
        print("   2. Add NEWS_API_KEY=your_key_here to your .env file")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main()) 