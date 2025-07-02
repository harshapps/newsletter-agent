#!/usr/bin/env python3
"""
Test script to verify newsletter generation works properly
"""

import requests
import json

def test_newsletter_generation():
    """Test newsletter generation with NewsAPI and sports topic"""
    
    print("🧪 Testing Newsletter Generation...")
    
    # Test data
    test_data = {
        "topics": ["sports"],
        "email": "test@example.com",
        "news_source": "NewsAPI"
    }
    
    try:
        # Make request to backend
        response = requests.post(
            "http://localhost:8000/generate-newsletter-content",
            json=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            newsletter = result.get("newsletter", {})
            
            print("✅ Newsletter generated successfully!")
            print(f"📊 Topics: {result.get('topics')}")
            print(f"📰 News count: {result.get('news_count')}")
            print(f"🔍 Sources used: {result.get('sources_used')}")
            print(f"📅 Date fetched: {result.get('date_fetched')}")
            print(f"🤖 Generation method: {newsletter.get('generation_method')}")
            
            print(f"\n📧 Subject: {newsletter.get('subject', 'No subject')}")
            print(f"📝 Content length: {len(newsletter.get('content', ''))} characters")
            
            # Show first 300 characters of content
            content = newsletter.get('content', '')
            if content:
                print(f"\n📄 Content preview:")
                print("-" * 50)
                print(content[:300] + "..." if len(content) > 300 else content)
                print("-" * 50)
            else:
                print("❌ No content generated")
                
        else:
            print(f"❌ Failed to generate newsletter: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_newsletter_generation() 