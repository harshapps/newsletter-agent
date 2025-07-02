# Agent and MCP Tools Usage Demonstration

## Overview
This document demonstrates how AI agents use Model Context Protocol (MCP) tools in the newsletter system to fetch news, analyze data, and generate personalized content.

## 1. MCP Tool Architecture

### Tool Registry System
```python
# backend/mcp/tools.py
class MCPToolRegistry:
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
        return self.tools.get(tool_name)
    
    def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        tool = self.get_tool(tool_name)
        if tool:
            return await tool.execute(**kwargs)
        return ToolResult(success=False, error=f"Tool {tool_name} not found")
```

### Tool Base Classes
```python
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
```

## 2. Available MCP Tools

### 1. News Fetching Tool
```python
@dataclass
class NewsTool(Tool):
    name: str = "fetch_news"
    description: str = "Fetch news articles from multiple sources based on topics"
    
    async def execute(self, topics: List[str], sources: Optional[List[str]] = None) -> ToolResult:
        try:
            news_service = NewsService()
            news_data, sources_used = await news_service.get_news_for_topics(topics)
            
            return ToolResult(
                success=True,
                data={
                    "news_count": len(news_data),
                    "articles": news_data[:10],
                    "topics": topics,
                    "sources_used": sources or ["yahoo_finance", "newsapi", "rss"]
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to fetch news: {str(e)}")
```

### 2. Stock Data Tool
```python
@dataclass
class StockDataTool(Tool):
    name: str = "fetch_stock_data"
    description: str = "Get real-time stock data and financial information"
    
    async def execute(self, symbols: List[str]) -> ToolResult:
        try:
            stock_data = {}
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                stock_data[symbol] = {
                    "current_price": info.get("currentPrice", "N/A"),
                    "market_cap": info.get("marketCap", "N/A"),
                    "pe_ratio": info.get("trailingPE", "N/A"),
                    "volume": info.get("volume", "N/A"),
                    "change_percent": info.get("regularMarketChangePercent", "N/A")
                }
            return ToolResult(success=True, data={"stocks": stock_data})
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to fetch stock data: {str(e)}")
```

### 3. Trend Analysis Tool
```python
@dataclass
class TrendAnalysisTool(Tool):
    name: str = "analyze_trends"
    description: str = "Analyze current trending topics and their relevance"
    
    async def execute(self, news_data: List[Dict]) -> ToolResult:
        try:
            topic_counts = {}
            keyword_counts = {}
            
            for article in news_data:
                title = article.get("title", "").lower()
                for topic in ["technology", "business", "finance", "politics", "science", "health"]:
                    if topic in title:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            top_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return ToolResult(
                success=True,
                data={
                    "trending_topics": [topic for topic, count in top_topics],
                    "topic_counts": topic_counts
                }
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to analyze trends: {str(e)}")
```

## 3. How Agents Use MCP Tools

### Agent Creation with Tool Access
```python
# backend/agents/crew_manager.py
def _create_researcher_agent(self) -> Agent:
    return Agent(
        role="News Researcher",
        goal="Gather comprehensive news data from multiple sources",
        backstory="Expert at finding and validating news from various sources",
        verbose=True,
        allow_delegation=False,
        tools=[
            "fetch_news",           # MCP Tool
            "fetch_stock_data",     # MCP Tool
            "analyze_trends"        # MCP Tool
        ]
    )

def _create_analyst_agent(self) -> Agent:
    return Agent(
        role="News Analyst",
        goal="Analyze news relevance and extract key insights",
        backstory="Specialist in analyzing news patterns and trends",
        verbose=True,
        allow_delegation=False,
        tools=[
            "analyze_trends",       # MCP Tool
            "summarize_content"     # MCP Tool
        ]
    )

def _create_writer_agent(self) -> Agent:
    return Agent(
        role="Newsletter Writer",
        goal="Create engaging and personalized newsletter content",
        backstory="Expert writer specializing in news summarization",
        verbose=True,
        allow_delegation=False,
        tools=[
            "generate_email_template",  # MCP Tool
            "summarize_content"         # MCP Tool
        ]
    )
```

### Tool Execution Flow
```python
# Example of how agents execute MCP tools
async def generate_newsletter(self, email: str, topics: List[str], news_data: List[Dict]) -> Dict[str, Any]:
    # 1. Researcher Agent uses fetch_news tool
    researcher_result = await self.researcher_agent.execute_task(
        f"Fetch latest news for topics: {', '.join(topics)}",
        tools=["fetch_news"]
    )
    
    # 2. Analyst Agent uses analyze_trends tool
    analyst_result = await self.analyst_agent.execute_task(
        f"Analyze trends in the news data",
        tools=["analyze_trends"],
        context={"news_data": news_data}
    )
    
    # 3. Writer Agent uses generate_email_template tool
    writer_result = await self.writer_agent.execute_task(
        f"Create newsletter content for {email}",
        tools=["generate_email_template"],
        context={
            "user_topics": topics,
            "news_data": news_data,
            "trends": analyst_result
        }
    )
    
    return writer_result
```

## 4. MCP Tool Integration Points

### Backend API Endpoints
```python
# backend/main.py
@app.get("/mcp/tools")
async def get_mcp_tools():
    """Get list of available MCP tools"""
    tools = await crew_manager.get_available_mcp_tools()
    return {
        "message": "Available MCP Tools",
        "tools": tools,
        "total_tools": len(tools)
    }

@app.post("/mcp/test-tool")
async def test_mcp_tool(request: MCPToolTestRequest):
    """Test a specific MCP tool"""
    result = await crew_manager.test_mcp_tool(request.tool_name, **request.parameters)
    return {
        "message": f"MCP Tool Test Result: {request.tool_name}",
        "result": result
    }
```

### News Service Integration
```python
# backend/services/news_service.py
async def get_news_for_topics(self, topics: List[str]) -> Dict[str, Any]:
    """Get news from multiple sources for given topics"""
    all_news = []
    sources_used = []
    
    # Use MCP tools to fetch from different sources
    if self.newsapi_available:
        newsapi_news = await self._get_newsapi_news(topics)
        all_news.extend(newsapi_news)
        sources_used.append("NewsAPI")
    
    # Yahoo Finance for finance topics
    yahoo_news = await self._get_yahoo_finance_news(topics)
    all_news.extend(yahoo_news)
    sources_used.append("Yahoo Finance")
    
    # RSS feeds for general topics
    rss_news = await self._get_rss_news(topics)
    all_news.extend(rss_news)
    sources_used.append("RSS Feeds")
    
    return {
        "date_fetched": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sources_used": sources_used,
        "news": self._deduplicate_news(all_news)
    }
```

## 5. Tool Execution Examples

### Example 1: Fetching News
```python
# Agent calls the fetch_news tool
tool_call = ToolCall(
    tool_name="fetch_news",
    parameters={
        "topics": ["technology", "AI"],
        "sources": ["newsapi", "yahoo_finance", "rss"]
    }
)

# Tool execution
result = await news_tool.execute(
    topics=["technology", "AI"],
    sources=["newsapi", "yahoo_finance", "rss"]
)

# Result
{
    "success": True,
    "data": {
        "news_count": 15,
        "articles": [...],
        "topics": ["technology", "AI"],
        "sources_used": ["NewsAPI", "Yahoo Finance", "RSS Feeds"]
    }
}
```

### Example 2: Stock Data Analysis
```python
# Agent calls the fetch_stock_data tool
tool_call = ToolCall(
    tool_name="fetch_stock_data",
    parameters={"symbols": ["AAPL", "GOOGL", "MSFT"]}
)

# Tool execution
result = await stock_tool.execute(symbols=["AAPL", "GOOGL", "MSFT"])

# Result
{
    "success": True,
    "data": {
        "stocks": {
            "AAPL": {
                "current_price": 150.25,
                "market_cap": 2500000000000,
                "pe_ratio": 25.5,
                "volume": 50000000,
                "change_percent": 2.5
            },
            "GOOGL": {...},
            "MSFT": {...}
        },
        "timestamp": "2025-01-27T10:30:00"
    }
}
```

### Example 3: Trend Analysis
```python
# Agent calls the analyze_trends tool
tool_call = ToolCall(
    tool_name="analyze_trends",
    parameters={"news_data": news_articles}
)

# Tool execution
result = await trend_tool.execute(news_data=news_articles)

# Result
{
    "success": True,
    "data": {
        "trending_topics": ["technology", "AI", "business", "finance"],
        "trending_keywords": ["artificial intelligence", "startup", "market"],
        "topic_counts": {
            "technology": 8,
            "AI": 6,
            "business": 4,
            "finance": 3
        }
    }
}
```

## 6. Context Passing in MCP

### How Context Flows Between Tools
```python
# Context is passed as parameters between tool calls
async def newsletter_generation_workflow(email: str, topics: List[str]):
    # Step 1: Fetch news (context: topics)
    news_result = await fetch_news_tool.execute(topics=topics)
    
    # Step 2: Analyze trends (context: news_data from step 1)
    trend_result = await analyze_trends_tool.execute(
        news_data=news_result.data["articles"]
    )
    
    # Step 3: Generate template (context: all previous results)
    template_result = await generate_email_template_tool.execute(
        user_topics=topics,
        news_data=news_result.data["articles"],
        trends=trend_result.data["trending_topics"],
        user_name=email.split('@')[0]
    )
    
    return template_result
```

## 7. Error Handling and Fallbacks

### Tool Error Handling
```python
async def execute_tool_with_fallback(self, tool_name: str, **kwargs):
    try:
        # Try primary tool
        result = await self.tool_registry.execute_tool(tool_name, **kwargs)
        if result.success:
            return result
        
        # Fallback to alternative tool
        fallback_tool = self.get_fallback_tool(tool_name)
        if fallback_tool:
            return await fallback_tool.execute(**kwargs)
        
        return ToolResult(
            success=False,
            error=f"Both primary and fallback tools failed for {tool_name}"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error=f"Tool execution error: {str(e)}"
        )
```

## 8. Benefits of MCP Architecture

### 1. **Modularity**: Each tool is self-contained and can be developed/tested independently
### 2. **Reusability**: Tools can be used by multiple agents
### 3. **Scalability**: Easy to add new tools without changing agent logic
### 4. **Context Preservation**: Tools receive relevant context from previous operations
### 5. **Error Isolation**: Tool failures don't crash the entire system
### 6. **Standardization**: Consistent interface for all tools

## 9. Testing MCP Tools

### API Testing
```bash
# Get available tools
curl http://localhost:8000/mcp/tools

# Test news fetching
curl -X POST http://localhost:8000/mcp/test-tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "fetch_news", "parameters": {"topics": ["technology"]}}'

# Test stock data
curl -X POST http://localhost:8000/mcp/test-tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "fetch_stock_data", "parameters": {"symbols": ["AAPL"]}}'
```

### Frontend Integration
The Streamlit frontend provides a user-friendly interface for testing MCP tools and viewing their results in real-time.

## 10. Summary

The MCP architecture in this newsletter system provides:

- **6 specialized tools** for different tasks
- **Multi-agent orchestration** using CrewAI
- **Context-aware tool execution** with parameter passing
- **Robust error handling** and fallback mechanisms
- **Real-time news fetching** from multiple sources
- **Personalized content generation** based on user preferences

This creates a powerful, scalable system where AI agents can effectively use external tools to gather data, analyze trends, and generate personalized newsletters for users. 