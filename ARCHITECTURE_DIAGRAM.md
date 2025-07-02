# Newsletter Agent MCP - Detailed Architecture Diagram

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    USER INTERFACE LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   Streamlit     │    │   FastAPI       │    │   Email Client  │                  │
│  │   Frontend      │◄──►│   Backend       │◄──►│   (Gmail/SMTP)  │                  │
│  │   (Port 8501)   │    │   (Port 8000)   │    │                 │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    API GATEWAY LAYER                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   User Auth &   │    │   Newsletter    │    │   MCP Tools     │                  │
│  │   Registration  │    │   Generation    │    │   Management    │                  │
│  │   Endpoints     │    │   Endpoints     │    │   Endpoints     │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    CORE SERVICES LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   CrewManager   │    │   NewsService   │    │   EmailService  │                  │
│  │   (Multi-Agent) │◄──►│   (Data Fetch)  │◄──►│   (SMTP/Email)  │                  │
│  │                 │    │                 │    │                 │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    MCP TOOLS LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   NewsTool      │    │   StockDataTool │    │   TrendAnalysis │                  │
│  │   (fetch_news)  │    │   (fetch_stock) │    │   Tool          │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   ContentSum    │    │   EmailTemplate │    │   WeatherTool   │                  │
│  │   (summarize)   │    │   Tool          │    │   (fetch_weather)│                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    EXTERNAL DATA LAYER                              │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   NewsAPI       │    │   Yahoo Finance │    │   RSS Feeds     │                  │
│  │   (News Data)   │    │   (Stock Data)  │    │   (Tech/Business)│                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   Reddit API    │    │   Hacker News   │    │   MongoDB       │                  │
│  │   (Community)   │    │   (Tech News)   │    │   (User Data)   │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 🤖 Multi-Agent System Architecture (CrewAI)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    CREW MANAGER                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │  Researcher     │    │   Analyst       │    │   Writer        │                  │
│  │   Agent         │───►│   Agent         │───►│   Agent         │                  │
│  │                 │    │                 │    │                 │                  │
│  │ • Gather news   │    │ • Analyze       │    │ • Create        │                  │
│  │ • Verify sources│    │ • Identify      │    │ • Write content │                  │
│  │ • Filter data   │    │ • Trends        │    │ • Personalize   │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│                                    │                                                │
│                                    ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              Editor Agent                                       │ │
│  │                                                                                 │ │
│  │ • Review content                                                               │ │
│  │ • Polish writing                                                               │ │
│  │ • Ensure quality                                                               │ │
│  │ • Final formatting                                                             │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 MCP (Model Context Protocol) Tools Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    MCP TOOL REGISTRY                                │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   Tool Registry │    │   Tool Executor │    │   Result Handler│                  │
│  │                 │    │                 │    │                 │                  │
│  │ • Register tools│    │ • Execute calls │    │ • Process results│                  │
│  │ • Validate      │    │ • Handle errors │    │ • Format output │                  │
│  │ • Route calls   │    │ • Manage async  │    │ • Cache results │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│                                    │                                                │
│                                    ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              AVAILABLE TOOLS                                   │ │
│  │                                                                                 │ │
│  │ • fetch_news: Get news from multiple sources                                   │ │
│  │ • fetch_stock_data: Real-time stock information                               │ │
│  │ • analyze_trends: Identify trending topics                                     │ │
│  │ • summarize_content: AI-powered content summarization                          │ │
│  │ • generate_email_template: Create personalized email templates                 │ │
│  │ • fetch_weather: Location-based weather data                                  │ │
│  └─────────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 User Interaction Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───►│   Frontend      │───►│   Backend API   │───►│   Agent Crew    │
│                 │    │   (Streamlit)   │    │   (FastAPI)     │    │   (CrewAI)      │
│ • Select topics │    │                 │    │                 │    │                 │
│ • Choose source │    │ • Validate      │    │ • Route request │    │ • Research      │
│ • Generate      │    │ • Format data   │    │ • Call services │    │ • Analyze       │
│ • Send email    │    │ • Display UI    │    │ • Process       │    │ • Write         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │                        │
                                ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Newsletter    │◄───│   Response      │◄───│   Newsletter    │◄───│   MCP Tools     │
│   Display       │    │   Processing    │    │   Generation    │    │   Execution     │
│                 │    │                 │    │                 │    │                 │
│ • Show content  │    │ • Format data   │    │ • Create HTML   │    │ • Fetch news    │
│ • Email option  │    │ • Add metadata  │    │ • Generate text │    │ • Get stock data│
│ • Copy content  │    │ • Error handling│    │ • Personalize   │    │ • Analyze trends│
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📊 Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   External      │───►│   NewsService   │───►│   CrewManager   │───►│   Newsletter    │
│   APIs          │    │                 │    │                 │    │   Output        │
│                 │    │                 │    │                 │    │                 │
│ • NewsAPI       │    │ • Aggregate     │    │ • Process       │    │ • HTML Email    │
│ • Yahoo Finance │    │ • Filter        │    │ • Analyze       │    │ • Plain Text    │
│ • RSS Feeds     │    │ • Deduplicate   │    │ • Generate      │    │ • Metadata      │
│ • Reddit        │    │ • Sort          │    │ • Format        │    │ • Links          │
│ • Hacker News   │    │ • Cache         │    │ • Personalize   │    │ • Images         │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Tools     │    │   Database      │    │   Email Service │    │   User          │
│   Cache         │    │   (MongoDB)     │    │   (SMTP)        │    │   Interface     │
│                 │    │                 │    │                 │    │                 │
│ • Tool results  │    │ • User profiles │    │ • Send emails   │    │ • View content  │
│ • API responses │    │ • Preferences   │    │ • Templates     │    │ • Interact      │
│ • Rate limiting │    │ • History       │    │ • Tracking      │    │ • Generate      │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 Security & Authentication Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                    SECURITY LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   API Keys      │    │   Environment   │    │   CORS          │                  │
│  │   Management    │    │   Variables     │    │   Protection    │                  │
│  │                 │    │                 │    │                 │                  │
│  │ • NewsAPI Key   │    │ • .env file     │    │ • Frontend      │                  │
│  │ • OpenAI Key    │    │ • Secure config │    │ • Backend       │                  │
│  │ • SMTP Config   │    │ • No hardcoding │    │ • Cross-origin  │                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
│                                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                  │
│  │   Rate Limiting │    │   Error         │    │   Logging       │                  │
│  │   & Throttling  │    │   Handling      │    │   & Monitoring  │                  │
│  │                 │    │                 │    │                 │                  │
│  │ • API calls     │    │ • Graceful      │    │ • Debug logs    │                  │
│  │ • User requests │    │ • Fallbacks     │    │ • Performance   │                  │
│  │ • Tool execution│    │ • User feedback │    │ • Error tracking│                  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Key Features & Capabilities

### **Multi-Agent System (CrewAI)**
- **Researcher Agent**: Gathers and verifies news from multiple sources
- **Analyst Agent**: Analyzes content for relevance and trends
- **Writer Agent**: Creates engaging, personalized newsletter content
- **Editor Agent**: Reviews and polishes final content

### **MCP Tools Integration**
- **News Fetching**: Real-time news from NewsAPI, Yahoo Finance, RSS feeds
- **Stock Data**: Live financial information via Yahoo Finance API
- **Trend Analysis**: AI-powered trend identification and analysis
- **Content Summarization**: Intelligent content summarization
- **Email Templates**: Dynamic email template generation
- **Weather Data**: Location-based weather for personalization

### **User Experience**
- **Interactive Chatbot**: Natural language interface for newsletter generation
- **Real-time Generation**: Instant newsletter creation without registration
- **Multiple Sources**: Choose from Auto, NewsAPI, Yahoo Finance, RSS feeds
- **Email Integration**: Send beautiful HTML newsletters directly to inbox
- **Content Preview**: Full content display with copy functionality

### **Technical Stack**
- **Backend**: FastAPI with async/await for high performance
- **Frontend**: Streamlit for interactive web interface
- **AI/ML**: OpenAI GPT-4 for content generation and analysis
- **Database**: MongoDB for user data and preferences
- **Email**: SMTP integration with Gmail/App Password
- **APIs**: NewsAPI, Yahoo Finance, Reddit, Hacker News, RSS feeds

## 🔄 Request-Response Flow Example

```
1. User selects "technology" topic and "NewsAPI" source
   ↓
2. Frontend sends POST to /generate-newsletter-content
   ↓
3. Backend calls NewsService.get_news_for_topics()
   ↓
4. NewsService fetches from NewsAPI using MCP tools
   ↓
5. CrewManager processes news data through agent pipeline
   ↓
6. LLM generates personalized newsletter content
   ↓
7. Content is formatted as HTML and plain text
   ↓
8. Response sent back to frontend with full newsletter
   ↓
9. Frontend displays content in enhanced UI with copy options
```

This architecture demonstrates a modern, scalable system that combines multi-agent AI, MCP tools, and real-time data integration to create personalized newsletters with a seamless user experience. 