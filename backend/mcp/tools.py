import os
import asyncio
import aiohttp
import yfinance as yf
from newsapi import NewsApiClient
import feedparser
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass

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

@dataclass
class NewsTool(Tool):
    """Tool for fetching news from various sources"""
    name: str = "fetch_news"
    description: str = "Fetch news articles from multiple sources based on topics"
    
    async def execute(self, topics: List[str], sources: Optional[List[str]] = None) -> ToolResult:
        """Execute the news fetching tool"""
        try:
            news_service = NewsService()
            news_data = await news_service.get_news_for_topics(topics)
            
            return ToolResult(
                success=True,
                data={
                    "news_count": len(news_data),
                    "articles": news_data[:10],  # Limit to 10 articles
                    "topics": topics,
                    "sources_used": sources or ["yahoo_finance", "newsapi", "rss"]
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to fetch news: {str(e)}"
            )

@dataclass
class StockDataTool(Tool):
    """Tool for fetching stock market data"""
    name: str = "fetch_stock_data"
    description: str = "Get real-time stock data and financial information"
    
    async def execute(self, symbols: List[str]) -> ToolResult:
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
            
            return ToolResult(
                success=True,
                data={
                    "stocks": stock_data,
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to fetch stock data: {str(e)}"
            )

@dataclass
class TrendAnalysisTool(Tool):
    """Tool for analyzing trending topics"""
    name: str = "analyze_trends"
    description: str = "Analyze current trending topics and their relevance"
    
    async def execute(self, news_data: List[Dict]) -> ToolResult:
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
            
            return ToolResult(
                success=True,
                data={
                    "trending_topics": [topic for topic, count in top_topics],
                    "trending_keywords": [keyword for keyword, count in top_keywords],
                    "topic_counts": topic_counts,
                    "keyword_counts": keyword_counts,
                    "analysis_timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to analyze trends: {str(e)}"
            )

@dataclass
class ContentSummarizerTool(Tool):
    """Tool for summarizing content using AI"""
    name: str = "summarize_content"
    description: str = "Summarize news articles and content using AI"
    
    async def execute(self, content: str, max_length: int = 150) -> ToolResult:
        """Execute the content summarization tool"""
        try:
            # Simple summarization (in a real implementation, you'd use an AI model)
            words = content.split()
            if len(words) <= max_length:
                summary = content
            else:
                summary = " ".join(words[:max_length]) + "..."
            
            return ToolResult(
                success=True,
                data={
                    "original_length": len(content),
                    "summary_length": len(summary),
                    "summary": summary,
                    "compression_ratio": len(summary) / len(content) if len(content) > 0 else 1.0
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to summarize content: {str(e)}"
            )

@dataclass
class EmailTemplateTool(Tool):
    """Tool for generating email templates"""
    name: str = "generate_email_template"
    description: str = "Generate personalized email templates for newsletters"
    
    async def execute(self, user_topics: List[str], news_data: List[Dict], user_name: Optional[str] = None) -> ToolResult:
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
                    <div class="news-title">{i}. {article.get('title', 'No title')}</div>
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
            
            return ToolResult(
                success=True,
                data={
                    "template": template,
                    "user_topics": user_topics,
                    "news_count": len(news_data),
                    "generated_at": datetime.now().isoformat()
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to generate email template: {str(e)}"
            )

@dataclass
class WeatherTool(Tool):
    """Tool for fetching weather information (for newsletter personalization)"""
    name: str = "fetch_weather"
    description: str = "Get weather information for location-based newsletter personalization"
    
    async def execute(self, location: str = "New York") -> ToolResult:
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
            
            return ToolResult(
                success=True,
                data=weather_data
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to fetch weather: {str(e)}"
            )

# MCP Tool Registry
class MCPToolRegistry:
    """Registry for all MCP tools"""
    
    def __init__(self):
        self.tools = {
            "fetch_news": NewsTool(),
            "fetch_stock_data": StockDataTool(),
            "analyze_trends": TrendAnalysisTool(),
            "summarize_content": ContentSummarizerTool(),
            "generate_email_template": EmailTemplateTool(),
            "fetch_weather": WeatherTool()
        }
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> Dict[str, Tool]:
        """Get all available tools"""
        return self.tools
    
    def list_tools(self) -> List[Dict[str, str]]:
        """List all available tools with descriptions"""
        return [
            {
                "name": name,
                "description": tool.description
            }
            for name, tool in self.tools.items()
        ]

# Global tool registry instance
tool_registry = MCPToolRegistry() 