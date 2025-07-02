#!/usr/bin/env python3
"""
Test script to verify MCP integration with CrewAI agents
"""

import asyncio
import os
import sys

# Add the backend directory to the path
sys.path.append('backend')

try:
    from backend.agents.crew_manager import CrewManager
    from backend.mcp.tools import MCPToolRegistry
except ImportError:
    # Fallback for different directory structure
    from agents.crew_manager import CrewManager
    from mcp.tools import MCPToolRegistry

async def test_mcp_tools():
    """Test individual MCP tools"""
    print("🧪 Testing MCP Tools...")
    
    # Initialize tool registry
    registry = MCPToolRegistry()
    
    # Test each tool
    tools_to_test = [
        ("fetch_news", {"topics": ["technology", "AI"]}),
        ("fetch_stock_data", {"symbols": ["AAPL", "GOOGL"]}),
        ("analyze_trends", {"news_data": [{"title": "AI breakthrough in technology"}, {"title": "New startup funding"}]}),
        ("summarize_content", {"content": "This is a test article about artificial intelligence and its impact on modern technology.", "max_length": 50}),
        ("generate_email_template", {"user_topics": ["technology"], "news_data": [{"title": "Test news", "summary": "Test summary", "source": "Test source"}], "user_name": "Test User"}),
        ("fetch_weather", {"location": "San Francisco"})
    ]
    
    for tool_name, params in tools_to_test:
        print(f"\n🔧 Testing {tool_name}...")
        try:
            result = await registry.execute_tool(tool_name, **params)
            if result["success"]:
                print(f"✅ {tool_name} succeeded")
                print(f"   Result: {result['data'][:200]}...")
            else:
                print(f"❌ {tool_name} failed: {result['error']}")
        except Exception as e:
            print(f"❌ {tool_name} error: {str(e)}")

async def test_crew_manager():
    """Test CrewManager with MCP tools"""
    print("\n🤖 Testing CrewManager with MCP Tools...")
    
    try:
        # Initialize CrewManager
        crew_manager = CrewManager()
        
        # Test available tools
        tools = await crew_manager.get_available_mcp_tools()
        print(f"📦 Available tools: {len(tools)}")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # Test individual tool
        print("\n🔧 Testing fetch_news tool...")
        result = await crew_manager.test_mcp_tool("fetch_news", topics=["technology"])
        if result["success"]:
            print("✅ fetch_news tool works")
        else:
            print(f"❌ fetch_news tool failed: {result['error']}")
        
        # Test newsletter generation (this will use the full MCP workflow)
        print("\n📧 Testing newsletter generation with MCP tools...")
        test_news_data = [
            {
                "title": "AI Breakthrough in Technology",
                "summary": "Scientists discover new AI algorithm that improves efficiency by 50%",
                "source": "Tech News",
                "url": "https://example.com/ai-breakthrough"
            },
            {
                "title": "Startup Funding Reaches New High",
                "summary": "Venture capital investment in tech startups reaches record levels",
                "source": "Business Daily",
                "url": "https://example.com/startup-funding"
            }
        ]
        
        newsletter = await crew_manager.generate_newsletter(
            email="test@example.com",
            topics=["technology", "business"],
            news_data=test_news_data,
            sources_used=["NewsAPI", "Yahoo Finance"],
            date_fetched="2025-01-27 10:30:00"
        )
        
        print("✅ Newsletter generation completed")
        print(f"   Subject: {newsletter.get('subject', 'No subject')}")
        print(f"   Content length: {len(newsletter.get('content', ''))} characters")
        print(f"   Generation method: {newsletter.get('generation_method', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ CrewManager test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main test function"""
    print("🚀 Starting MCP Integration Tests...")
    
    # Test 1: Individual MCP tools
    await test_mcp_tools()
    
    # Test 2: CrewManager integration
    await test_crew_manager()
    
    print("\n✅ MCP Integration Tests Completed!")

if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    
    # Run tests
    asyncio.run(main()) 