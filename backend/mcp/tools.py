import os
import asyncio
import aiohttp
import yfinance as yf
from newsapi import NewsApiClient
import feedparser
from typing import List, Dict, Any, Optional, Type
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

# Simple MCP-like classes
@dataclass
class Tool:
    """Base tool class"""
    name: str
    description: str

@dataclass
class ToolResult:
    """Result from tool execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class ToolCall:
    """Tool call request"""
    tool_name: str
    parameters: Dict[str, Any]

# Import the news service
from services.news_service import NewsService

# Pydantic models for tool parameters
class FetchNewsInput(BaseModel):
    topics: List[str] = Field(description="List of topics to fetch news for")
    sources: Optional[List[str]] = Field(default=None, description="Optional list of news sources to use")

class FetchStockDataInput(BaseModel):
    symbols: List[str] = Field(description="List of stock symbols to fetch data for")

class AnalyzeTrendsInput(BaseModel):
    news_data: List[Dict] = Field(description="List of news articles to analyze for trends")

class SummarizeContentInput(BaseModel):
    content: str = Field(description="Content to summarize")
    max_length: int = Field(default=150, description="Maximum length of summary")

class GenerateEmailTemplateInput(BaseModel):
    user_topics: List[str] = Field(description="User's topics of interest")
    news_data: List[Dict] = Field(description="News data to include in template")
    user_name: Optional[str] = Field(default=None, description="User's name for personalization")

class FetchWeatherInput(BaseModel):
    location: str = Field(default="New York", description="Location to get weather for")

# CrewAI-compatible tool classes
class NewsTool(BaseTool):
    name: str = "fetch_news"
    description: str = "Fetch news articles from multiple sources based on topics"
    args_schema: Optional[Type[BaseModel]] = FetchNewsInput
    
    async def _arun(self, topics: List[str], sources: Optional[List[str]] = None) -> str:
        """Execute the news fetching tool"""
        try:
            news_service = NewsService()
            result = await news_service.get_news_for_topics(topics)
            
            news_data = result.get("news", [])
            sources_used = result.get("sources_used", [])
            
            # Format the result for the agent
            response = f"Found {len(news_data)} news articles from {', '.join(sources_used)} sources.\n\n"
            
            for i, article in enumerate(news_data[:5], 1):  # Show first 5 articles
                response += f"{i}. {article.get('title', 'No title')}\n"
                response += f"   Summary: {article.get('summary', 'No summary')[:100]}...\n"
                response += f"   Source: {article.get('source', 'Unknown')}\n\n"
            
            return response
            
        except Exception as e:
            return f"Failed to fetch news: {str(e)}"
    
    def _run(self, topics: List[str], sources: Optional[List[str]] = None) -> str:
        """Synchronous version for compatibility"""
        return asyncio.run(self._arun(topics, sources))

class StockDataTool(BaseTool):
    name: str = "fetch_stock_data"
    description: str = "Get real-time stock data and financial information"
    args_schema: Optional[Type[BaseModel]] = FetchStockDataInput
    
    async def _arun(self, symbols: List[str]) -> str:
        """Execute the stock data fetching tool"""
        try:
            stock_data = {}
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    stock_data[symbol] = {
                        "current_price": info.get("currentPrice", "N/A"),
                        "market_cap": info.get("marketCap", "N/A"),
                        "pe_ratio": info.get("trailingPE", "N/A"),
                        "volume": info.get("volume", "N/A"),
                        "change_percent": info.get("regularMarketChangePercent", "N/A"),
                        "company_name": info.get("longName", symbol)
                    }
                except Exception as e:
                    stock_data[symbol] = {"error": str(e)}
            
            # Format the result for the agent
            response = f"Stock data for {len(symbols)} symbols:\n\n"
            
            for symbol, data in stock_data.items():
                if "error" not in data:
                    response += f"{symbol} ({data['company_name']}):\n"
                    response += f"  Price: ${data['current_price']}\n"
                    response += f"  Change: {data['change_percent']}%\n"
                    response += f"  Volume: {data['volume']}\n\n"
                else:
                    response += f"{symbol}: Error - {data['error']}\n\n"
            
            return response
            
        except Exception as e:
            return f"Failed to fetch stock data: {str(e)}"
    
    def _run(self, symbols: List[str]) -> str:
        """Synchronous version for compatibility"""
        return asyncio.run(self._arun(symbols))

class TrendAnalysisTool(BaseTool):
    name: str = "analyze_trends"
    description: str = "Analyze current trending topics and their relevance"
    args_schema: Optional[Type[BaseModel]] = AnalyzeTrendsInput
    
    async def _arun(self, news_data: List[Dict]) -> str:
        """Execute the trend analysis tool"""
        try:
            # Analyze trends from news data
            topic_counts = {}
            keyword_counts = {}
            
            for article in news_data:
                title = article.get("title", "").lower()
                
                # Count topics
                for topic in ["technology", "business", "finance", "politics", "science", "health"]:
                    if topic in title:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
                
                # Count keywords
                keywords = ["AI", "artificial intelligence", "startup", "market", "economy", "innovation"]
                for keyword in keywords:
                    if keyword.lower() in title:
                        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
            
            # Get top trends
            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Format the result for the agent
            response = f"Trend analysis of {len(news_data)} articles:\n\n"
            
            response += "Top trending topics:\n"
            for topic, count in top_topics:
                response += f"  {topic}: {count} articles\n"
            
            response += "\nTop trending keywords:\n"
            for keyword, count in top_keywords:
                response += f"  {keyword}: {count} mentions\n"
            
            return response
            
        except Exception as e:
            return f"Failed to analyze trends: {str(e)}"
    
    def _run(self, news_data: List[Dict]) -> str:
        """Synchronous version for compatibility"""
        return asyncio.run(self._arun(news_data))

class ContentSummarizerTool(BaseTool):
    name: str = "summarize_content"
    description: str = "Summarize news articles and content using AI"
    args_schema: Optional[Type[BaseModel]] = SummarizeContentInput
    
    async def _arun(self, content: str, max_length: int = 150) -> str:
        """Execute the content summarization tool"""
        try:
            # Simple summarization (in a real implementation, you'd use an AI model)
            words = content.split()
            if len(words) <= max_length:
                summary = content
            else:
                summary = " ".join(words[:max_length]) + "..."
            
            # Format the result for the agent
            response = f"Content summary ({len(summary)} characters):\n\n"
            response += summary
            
            return response
            
        except Exception as e:
            return f"Failed to summarize content: {str(e)}"
    
    def _run(self, content: str, max_length: int = 150) -> str:
        """Synchronous version for compatibility"""
        return asyncio.run(self._arun(content, max_length))

class EmailTemplateTool(BaseTool):
    name: str = "generate_email_template"
    description: str = "Generate personalized email templates for newsletters"
    args_schema: Optional[Type[BaseModel]] = GenerateEmailTemplateInput
    
    async def _arun(self, user_topics: List[str], news_data: List[Dict], user_name: Optional[str] = None) -> str:
        """Execute the email template generation tool"""
        try:
            # Generate personalized email template
            greeting = f"Good morning{f', {user_name}' if user_name else ''}! 🌅"
            
            topics_text = ", ".join(user_topics)
            
            # Create news items HTML
            news_items_html = ""
            for i, article in enumerate(news_data[:8], 1):  # Limit to 8 articles
                news_items_html += f"""
                <div class="news-item">
                    <h3>{article.get('title', 'No title')}</h3>
                    <div class="news-summary">{article.get('summary', 'No summary')[:200]}...</div>
                    <div class="news-source">Source: {article.get('source', 'Unknown')}</div>
                </div>
                """
            
            template = f"""
            <div class="greeting">{greeting}</div>
            <div class="stats">
                <p><strong>📊 Today's Summary</strong></p>
                <p>Topics: {topics_text}</p>
                <p>News items: {len(news_data)}</p>
                <p>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            <div class="news-section">
                <h2>📰 Top Stories</h2>
                {news_items_html}
            </div>
            """
            
            # Format the result for the agent
            response = f"Email template generated for {user_name or 'user'}:\n\n"
            response += f"Topics: {topics_text}\n"
            response += f"News items: {len(news_data)}\n"
            response += f"Template length: {len(template)} characters\n\n"
            response += "Template preview:\n"
            response += template[:500] + "..." if len(template) > 500 else template
            
            return response
            
        except Exception as e:
            return f"Failed to generate email template: {str(e)}"
    
    def _run(self, user_topics: List[str], news_data: List[Dict], user_name: Optional[str] = None) -> str:
        """Synchronous version for compatibility"""
        return asyncio.run(self._arun(user_topics, news_data, user_name))

class WeatherTool(BaseTool):
    name: str = "fetch_weather"
    description: str = "Get weather information for location-based newsletter personalization"
    args_schema: Optional[Type[BaseModel]] = FetchWeatherInput
    
    async def _arun(self, location: str = "New York") -> str:
        """Execute the weather fetching tool"""
        try:
            # Mock weather data (in real implementation, use a weather API)
            weather_data = {
                "location": location,
                "temperature": "72°F",
                "condition": "Partly Cloudy",
                "humidity": "65%",
                "forecast": "Sunny with scattered clouds",
                "timestamp": datetime.now().isoformat()
            }
            
            # Format the result for the agent
            response = f"Weather for {location}:\n"
            response += f"Temperature: {weather_data['temperature']}\n"
            response += f"Condition: {weather_data['condition']}\n"
            response += f"Humidity: {weather_data['humidity']}\n"
            response += f"Forecast: {weather_data['forecast']}\n"
            
            return response
            
        except Exception as e:
            return f"Failed to fetch weather: {str(e)}"
    
    def _run(self, location: str = "New York") -> str:
        """Synchronous version for compatibility"""
        return asyncio.run(self._arun(location))

# MCP Tool Registry
class MCPToolRegistry:
    """Registry for managing MCP tools"""
    
    def __init__(self):
        self.tools = {
            "fetch_news": NewsTool(),
            "fetch_stock_data": StockDataTool(),
            "analyze_trends": TrendAnalysisTool(),
            "summarize_content": ContentSummarizerTool(),
            "generate_email_template": EmailTemplateTool(),
            "fetch_weather": WeatherTool()
        }
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a specific tool by name"""
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, BaseTool]:
        """Get all available tools"""
        return self.tools
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools with their descriptions"""
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools.values()
        ]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool by name with given parameters"""
        tool = self.get_tool(tool_name)
        if tool:
            try:
                result = await tool._arun(**kwargs)
                return {
                    "success": True,
                    "data": result,
                    "error": None
                }
            except Exception as e:
                return {
                    "success": False,
                    "data": None,
                    "error": str(e)
                }
        else:
            return {
                "success": False,
                "data": None,
                "error": f"Tool {tool_name} not found"
            }

# Global tool registry instance
tool_registry = MCPToolRegistry() 

llm = ChatOpenAI(
    model="gpt-4",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

def llm_topic_news_fetcher(topic: str):
    """Legacy function for fetching news by topic"""
    async def fetch_news():
        news_service = NewsService()
        result = await news_service.get_news_for_topics([topic])
        return result.get("news", [])
    
    return asyncio.run(fetch_news()) 