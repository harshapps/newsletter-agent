#!/usr/bin/env python3

import os
import asyncio
from datetime import datetime, timedelta
from newsapi import NewsApiClient

async def test_newsapi():
    """Test NewsAPI directly to see if it's working"""
    
    # Get API key
    api_key = os.getenv('NEWS_API_KEY')
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")
    
    if not api_key:
        print("❌ No NewsAPI key found")
        return
    
    try:
        # Initialize client
        newsapi = NewsApiClient(api_key=api_key)
        print("✅ NewsAPI client initialized")
        
        # Calculate 24 hours ago
        now = datetime.now()
        yesterday = now - timedelta(hours=24)
        
        print(f"📅 Searching from {yesterday.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}")
        
        # Test with a simple query
        try:
            articles = newsapi.get_everything(
                q='technology',
                language='en',
                page_size=5,
                from_param=yesterday.strftime('%Y-%m-%d'),
                to=now.strftime('%Y-%m-%d')
            )
            
            print(f"📊 API Response Status: {articles.get('status')}")
            print(f"📊 Total Results: {articles.get('totalResults', 0)}")
            print(f"📊 Articles Found: {len(articles.get('articles', []))}")
            
            if articles.get('status') == 'ok' and articles.get('articles'):
                print("\n📰 Sample Articles:")
                for i, article in enumerate(articles['articles'][:3]):
                    print(f"{i+1}. {article.get('title', 'No title')}")
                    print(f"   Source: {article.get('source', {}).get('name', 'Unknown')}")
                    print(f"   Published: {article.get('publishedAt', 'Unknown')}")
                    print(f"   URL: {article.get('url', 'No URL')}")
                    print()
            else:
                print("❌ No articles found or API error")
                if articles.get('status') != 'ok':
                    print(f"❌ API Error: {articles.get('message', 'Unknown error')}")
                    
        except Exception as e:
            print(f"❌ Error calling NewsAPI: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error initializing NewsAPI: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_newsapi()) 