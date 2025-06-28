#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from agents.crew_manager import CrewManager
from services.news_service import NewsService

async def test_urls():
    """Test that article URLs are included in newsletter content"""
    print("🔍 Testing article URL inclusion in newsletter...")
    
    # Get news data
    service = NewsService()
    news_result = await service.get_news_for_topics(['technology'])
    
    print(f"📰 Found {len(news_result['news'])} news items")
    print(f"🔗 News items with URLs:")
    for i, item in enumerate(news_result['news'][:3], 1):
        url = item.get('url', 'No URL')
        print(f"  {i}. {item['title'][:50]}...")
        print(f"     URL: {url}")
    
    # Generate newsletter
    crew = CrewManager()
    result = await crew.generate_newsletter(
        'test@example.com', 
        ['technology'], 
        news_result['news'], 
        news_result['sources_used'], 
        news_result['date_fetched']
    )
    
    print(f"\n📝 Newsletter Content Preview:")
    print("=" * 50)
    content = result['content']
    print(content[:800] + "..." if len(content) > 800 else content)
    
    print(f"\n🌐 HTML Content Preview:")
    print("=" * 50)
    html_content = result['html_content']
    print(html_content[:800] + "..." if len(html_content) > 800 else html_content)
    
    # Check if URLs are present
    url_count = content.count('http')
    print(f"\n✅ Found {url_count} URLs in newsletter content")
    
    if url_count > 0:
        print("🎉 Article URLs are successfully included!")
    else:
        print("⚠️  No URLs found in newsletter content")

if __name__ == "__main__":
    asyncio.run(test_urls()) 