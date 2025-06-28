#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('backend')

async def test_news():
    from backend.services.news_service import NewsService
    
    print("🧪 Testing news service...")
    service = NewsService()
    
    print(f"NewsAPI available: {service.newsapi_available}")
    
    # Test news fetching
    news, sources = await service.get_news_for_topics(['sports', 'technology'])
    
    print(f"Sources used: {sources}")
    print(f"Found {len(news)} articles")
    
    # Show first 5 articles
    for i, article in enumerate(news[:5], 1):
        print(f"{i}. {article.get('title', 'No title')} - {article.get('source', 'Unknown')}")
    
    if len(news) > 0:
        print("\n✅ SUCCESS: News service is working!")
    else:
        print("\n❌ FAIL: No news found")

if __name__ == "__main__":
    asyncio.run(test_news()) 