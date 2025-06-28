# 🤖 Newsletter Agent MCP

An intelligent AI-powered newsletter system that combines Multi-Agent Systems (CrewAI) and Model Context Protocol (MCP) to deliver personalized news summaries via email.

## 🚀 Features

### 🤖 Multi-Agent AI System
- **Researcher Agent**: Fetches news from multiple sources using MCP tools
- **Analyst Agent**: Analyzes trends and summarizes content
- **Writer Agent**: Creates personalized newsletter content
- **Editor Agent**: Polishes and formats the final newsletter

### 🔧 Model Context Protocol (MCP) Integration
- **News Fetching Tools**: Yahoo Finance, NewsAPI, RSS feeds
- **Trend Analysis**: Identifies trending topics and keywords
- **Content Summarization**: Creates concise summaries
- **Email Template Generation**: Builds personalized email templates

### 💬 Interactive AI Chatbot
- **Natural Language Interface**: Chat with AI agents to generate newsletters
- **Topic Detection**: Intelligent responses based on user interests
- **Real-time Generation**: Instant newsletter creation
- **Email Integration**: Send newsletters directly to your inbox

### 📰 News Sources
- **Yahoo Finance**: Stock news and market updates
- **NewsAPI**: General news and current events
- **RSS Feeds**: TechCrunch, Business Insider, Science Daily
- **Custom Sources**: Easily extensible for additional sources

### 📧 Email Features
- **Beautiful HTML Templates**: Professional newsletter formatting
- **Personalized Content**: Tailored to user interests
- **Scheduled Delivery**: Automated daily delivery at 9 AM
- **Multiple Formats**: Text and HTML versions

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (Streamlit)   │◄──►│   (FastAPI)     │◄──►│   (MongoDB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Chatbot    │    │   CrewAI        │    │   User Data     │
│   Interface     │    │   Agents        │    │   & Settings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Newsletter    │    │   MCP Tools     │    │   Email         │
│   Generation    │    │   Integration   │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **AI Framework**: CrewAI
- **Protocol**: Model Context Protocol (MCP)
- **Email**: SMTP with HTML templates
- **News Sources**: Yahoo Finance, NewsAPI, RSS feeds

## 📋 Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- OpenAI API key
- Email credentials (Gmail recommended)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/harshapps/newsletter-agent.git
cd newsletter-agent
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/newsletter_agent

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here

# News API Configuration
NEWS_API_KEY=your_newsapi_key_here

# Application Configuration
LOG_LEVEL=INFO
```

### 5. Start MongoDB
```bash
# Local MongoDB
brew install mongodb-community  # macOS
brew services start mongodb-community

# Or use MongoDB Atlas (cloud)
```

### 6. Run the Application

#### Start the Backend
```bash
python start_backend.py
```
Backend will be available at: http://localhost:8000

#### Start the Frontend
```bash
python start_frontend.py
```
Frontend will be available at: http://localhost:8501

## 🎯 Usage

### 1. User Registration
1. Navigate to the "📝 Register" page
2. Enter your email and select topics of interest
3. Choose preferred news sources
4. Set delivery time (default: 9 AM)

### 2. AI Chatbot Interface
1. Go to "🤖 AI Chatbot" page
2. Configure your email and topics in the sidebar
3. Start chatting with the AI assistant:
   - "Generate a technology newsletter"
   - "What's the latest in AI news?"
   - "Send the newsletter to my email"
   - "Help me understand current events"

### 3. Newsletter Generation
- **Automatic**: Daily newsletters sent at scheduled time
- **On-demand**: Generate newsletters through the chatbot
- **Custom**: Request specific topics or sources

### 4. Email Delivery
- Beautiful HTML newsletters
- Personalized content based on interests
- Multiple news sources combined
- Professional formatting and styling

## 🔧 API Endpoints

### User Management
- `POST /register` - Register new user
- `GET /users` - Get all users
- `PUT /users/{email}` - Update user preferences

### Newsletter Generation
- `POST /test-newsletter` - Generate test newsletter
- `POST /generate-newsletter` - Generate newsletter for user
- `POST /send-newsletter` - Send newsletter via email

### System Information
- `GET /stats` - System statistics
- `GET /health` - Health check
- `GET /mcp/tools` - Available MCP tools

## 🏆 Hackathon Ready Features

- **Multi-Agent Architecture**: Demonstrates advanced AI coordination
- **MCP Integration**: Shows tool integration capabilities
- **Real-time Data**: Live news and stock data
- **Personalization**: AI-driven content curation
- **Interactive Chatbot**: Natural language interface
- **Scalable Design**: Production-ready architecture
- **Modern UI**: Beautiful Streamlit interface

Perfect for impressing hackathon judges! 🎯

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) for multi-agent framework
- [Model Context Protocol](https://modelcontextprotocol.io/) for tool integration
- [Streamlit](https://streamlit.io/) for the web interface
- [FastAPI](https://fastapi.tiangolo.com/) for the backend API

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints

---

**Built with ❤️ using AI and Multi-Agent Systems**

## Google News Functionality

The system now properly scrapes real news from Google News using the NewsAPI service, then uses an LLM to summarize the articles. This replaces the previous fake news generation.

### How it works:
1. **Real Data Fetching**: Uses NewsAPI to get actual Google News articles
2. **LLM Summarization**: Sends real article content to GPT-4 for intelligent summarization
3. **Fallback Sources**: If Google News fails, falls back to RSS feeds
4. **No Fake News**: Never generates fake content - only works with real news

### Testing Google News

Run the test script to verify Google News functionality:

```bash
python test_google_news.py
```

This will test both the news fetching and LLM summarization capabilities.

## Project Structure

```
newsletter-agent-mcp/
├── backend/
│   ├── agents/
│   │   └── crew_manager.py
│   ├── database/
│   │   └── mongodb.py
│   ├── main.py
│   ├── mcp/
│   │   └── tools.py
│   └── services/
│       ├── email_service.py
│       └── news_service.py
├── frontend/
│   └── app.py
├── requirements.txt
├── start_backend.py
├── start_frontend.py
└── test_google_news.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License 

## Features

- **Multi-Agent AI System**: Uses CrewAI for intelligent news curation and content generation
- **Model Context Protocol (MCP)**: Implements MCP tools for news fetching, stock data, trend analysis, and more
- **Real News Sources**: Fetches real news from multiple free sources including Reddit, Hacker News, RSS feeds, and Yahoo Finance
- **AI-Powered Summarization**: Uses LLM to summarize real news articles
- **Personalized Newsletters**: Customized content based on user preferences
- **Modern UI**: Streamlit frontend for easy user interaction
- **Database Storage**: MongoDB for storing user preferences and newsletter history

## Tech Stack

- **Backend**: FastAPI, CrewAI, MongoDB
- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT-4, LangChain
- **News Sources**: Reddit, Hacker News, RSS feeds, Yahoo Finance, NewsAPI (optional)
- **Email**: SMTP with HTML templates
- **Database**: MongoDB with Motor (async driver)

## Setup

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd newsletter-agent-mcp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI API Key (required for LLM functionality)
OPENAI_API_KEY=your_openai_api_key_here

# NewsAPI Key (optional - for additional news sources)
NEWS_API_KEY=your_newsapi_key_here

# MongoDB Connection (optional, defaults to localhost)
MONGODB_URI=mongodb://localhost:27017

# Email Configuration (optional, for sending newsletters)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### 3. API Keys Setup

#### OpenAI API Key (Required)
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an account and get your API key
3. Add it to your `.env` file

#### NewsAPI Key (Optional)
1. Go to [NewsAPI](https://newsapi.org/)
2. Sign up for a free account (1000 requests/day)
3. Get your API key
4. Add it to your `.env` file
5. **Note**: The system works perfectly without this key using free sources

## News Sources

The system now uses multiple **free** news sources:

### 🆓 **Free Sources (No API Key Required):**
- **Reddit**: r/news, r/technology, r/sports, r/business, r/science
- **Hacker News**: Top stories from the tech community
- **RSS Feeds**: BBC, Reuters, CNN, TechCrunch, ESPN, and more
- **Yahoo Finance**: Stock market and financial news

### 🔑 **Optional Sources (API Key Required):**
- **NewsAPI**: Additional news aggregation (1000 free requests/day)

### How it works:
1. **Real Data Fetching**: Uses multiple free sources to get actual news articles
2. **LLM Summarization**: Sends real article content to GPT-4 for intelligent summarization
3. **Multiple Fallbacks**: If one source fails, others continue working
4. **No Fake News**: Never generates fake content - only works with real news 