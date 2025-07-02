#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.news_service import NewsService

async def test_newsapi():
    """Test NewsAPI integration"""
    print("🔍 Testing NewsAPI integration...")
    
    # Create news service instance
    service = NewsService()
    
    # Check if NewsAPI is available
    print(f"📡 NewsAPI Available: {service.newsapi_available}")
    
    if not service.newsapi_available:
        print("❌ NewsAPI not available. Please check your API key in .env file")
        return
    
    # Test fetching news with NewsAPI
    print("\n📰 Testing news fetching with NewsAPI...")
    try:
        result = await service.get_news_for_topics(['technology'], preferred_source='NewsAPI')
        
        print(f"✅ Successfully fetched news!")
        print(f"📊 Results:")
        print(f"   News items: {len(result['news'])}")
        print(f"   Sources used: {result['sources_used']}")
        print(f"   Date fetched: {result['date_fetched']}")
        
        # Show sample articles
        print(f"\n📰 Sample articles:")
        for i, article in enumerate(result['news'][:3], 1):
            print(f"  {i}. {article['title']}")
            print(f"     Source: {article['source']}")
            print(f"     URL: {article.get('url', 'No URL')}")
            print()
        
        # Check if NewsAPI was actually used
        if 'NewsAPI' in result['sources_used']:
            print("✅ NewsAPI is working correctly!")
        else:
            print("⚠️ NewsAPI might not be working - using fallback sources")
            
    except Exception as e:
        print(f"❌ Error testing NewsAPI: {str(e)}")
        print("Please check your API key and internet connection")

if __name__ == "__main__":
    asyncio.run(test_newsapi()) 