import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure the page
st.set_page_config(
    page_title="Newsletter Agent MCP - AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

def main():
    # Header
    st.title("🤖 Newsletter Agent MCP")
    st.markdown("**AI-powered newsletter agent using Multi-Agent Systems and Model Context Protocol (MCP)**")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["🏠 Home", "📝 Register", "🔧 MCP Tools Demo", "📊 System Stats", "🤖 AI Chatbot"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "📝 Register":
        show_register_page()
    elif page == "🔧 MCP Tools Demo":
        show_mcp_demo_page()
    elif page == "📊 System Stats":
        show_stats_page()
    elif page == "🤖 AI Chatbot":
        show_ai_chatbot_page()

def show_home_page():
    """Display the home page with project overview"""
    st.header("🚀 Welcome to Newsletter Agent MCP")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### What is Newsletter Agent MCP?
        
        This is an intelligent newsletter system that combines cutting-edge AI technologies:
        
        - **🤖 Multi-Agent AI System (CrewAI)**: Multiple specialized AI agents work together
        - **🔧 Model Context Protocol (MCP)**: Agents use powerful tools to fetch and analyze data
        - **📰 Personalized News Curation**: Tailored content based on your interests
        - **⏰ Automated Delivery**: Daily emails at 9 AM
        - **📊 Multiple News Sources**: Yahoo Finance, Google News, RSS feeds, and more
        - **💬 Interactive AI Chatbot**: Chat with AI agents to generate newsletters and ask questions
        
        ### How it Works
        
        1. **User Registration**: Enter your email and select topics of interest
        2. **AI Chatbot**: Chat with our AI agents to generate newsletters or ask questions
        3. **News Gathering**: AI agents fetch news from multiple sources using MCP tools
        4. **Content Analysis**: Agents analyze and summarize the news
        5. **Newsletter Creation**: Personalized newsletter is generated
        6. **Email Delivery**: Beautiful email sent to your inbox at 9 AM daily
        """)
    
    with col2:
        st.markdown("""
        ### 🏆 Hackathon Ready Features
        
        - **Multi-Agent Architecture**: Demonstrates advanced AI coordination
        - **MCP Integration**: Shows tool integration capabilities
        - **Real-time Data**: Live news and stock data
        - **Personalization**: AI-driven content curation
        - **Interactive Chatbot**: Natural language interface for newsletter generation
        - **Scalable Design**: Production-ready architecture
        - **Modern UI**: Beautiful Streamlit interface
        
        Perfect for impressing hackathon judges! 🎯
        """)
    
    # Quick stats
    st.subheader("📈 Quick Stats")
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Users", stats.get("database_stats", {}).get("total_users", 0))
            with col2:
                st.metric("Active Users", stats.get("database_stats", {}).get("active_users", 0))
            with col3:
                st.metric("Newsletters Sent", stats.get("database_stats", {}).get("total_newsletters", 0))
            with col4:
                st.metric("MCP Tools", stats.get("mcp_tools_count", 0))
        else:
            st.warning("⚠️ Backend not running. Start the FastAPI server to see live stats.")
    except:
        st.warning("⚠️ Backend not running. Start the FastAPI server to see live stats.")

def show_register_page():
    """Display the user registration page"""
    st.header("📝 Register for Daily Newsletters")
    
    with st.form("registration_form"):
        st.markdown("### Enter Your Information")
        
        # Email input
        email = st.text_input("Email Address", placeholder="your.email@example.com")
        
        # Topic selection
        st.markdown("### Select Your Topics of Interest")
        topics = st.multiselect(
            "Choose topics (select multiple):",
            [
                "technology", "business", "finance", "politics", 
                "science", "health", "sports", "entertainment"
            ],
            default=["technology", "business"]
        )
        
        # News source selection
        st.markdown("### Choose News Sources")
        news_sources = st.multiselect(
            "Select preferred news sources:",
            [
                "yahoo_finance", "google_news", "rss"
            ],
            default=["yahoo_finance", "google_news", "rss"]
        )
        
        # Delivery time
        delivery_time = st.selectbox(
            "Preferred delivery time:",
            ["09:00", "08:00", "10:00", "07:00"],
            index=0
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Register for Newsletter")
        
        if submitted:
            if not email:
                st.error("❌ Please enter your email address")
                return
            
            if not topics:
                st.error("❌ Please select at least one topic")
                return
            
            # Prepare registration data
            registration_data = {
                "email": email,
                "topics": topics,
                "news_sources": news_sources,
                "delivery_time": delivery_time
            }
            
            # Send registration request
            try:
                response = requests.post(f"{API_BASE_URL}/register", json=registration_data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ {result.get('message', 'Registration successful!')}")
                    st.info(f"📧 You'll receive daily newsletters at {delivery_time} covering: {', '.join(topics)}")
                    
                    # Show what happens next
                    st.markdown("### What happens next?")
                    st.markdown("""
                    1. **🤖 AI Agents**: Our multi-agent system will start gathering news for your topics
                    2. **🔧 MCP Tools**: Agents will use various tools to fetch and analyze content
                    3. **📰 Newsletter Creation**: A personalized newsletter will be generated
                    4. **📧 Daily Delivery**: You'll receive your first newsletter tomorrow at 9 AM
                    """)
                else:
                    st.error(f"❌ Registration failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
                st.info("💡 Make sure the FastAPI backend is running on localhost:8000")

def show_mcp_demo_page():
    """Display MCP tools demonstration page"""
    st.header("🔧 MCP Tools Demonstration")
    st.markdown("**Model Context Protocol (MCP) allows AI agents to use powerful tools for enhanced capabilities**")
    
    # Available tools
    st.subheader("🛠️ Available MCP Tools")
    try:
        response = requests.get(f"{API_BASE_URL}/mcp/tools")
        if response.status_code == 200:
            tools_data = response.json()
            tools = tools_data.get("tools", [])
            
            for tool in tools:
                with st.expander(f"🔧 {tool['name']}"):
                    st.markdown(f"**Description:** {tool['description']}")
        else:
            st.warning("⚠️ Could not fetch MCP tools")
    except:
        st.warning("⚠️ Backend not running. Start the FastAPI server to see MCP tools.")
    
    # Interactive tool testing
    st.subheader("🧪 Test MCP Tools")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📰 News Fetching Tool")
        if st.button("Test News Fetching", key="test_news_fetch"):
            test_news_fetching()
    
    with col2:
        st.markdown("### 📈 Stock Data Tool")
        if st.button("Test Stock Data", key="test_stock_data"):
            test_stock_data()
    
    # Full demo
    st.subheader("🎬 Complete MCP Demo")
    if st.button("Run Full MCP Demo", key="run_mcp_demo"):
        run_full_mcp_demo()

def show_stats_page():
    """Display system statistics page"""
    st.header("📊 System Statistics")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            
            # Database stats
            st.subheader("🗄️ Database Statistics")
            db_stats = stats.get("database_stats", {})
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Users", db_stats.get("total_users", 0))
            with col2:
                st.metric("Active Users", db_stats.get("active_users", 0))
            with col3:
                st.metric("Total Newsletters", db_stats.get("total_newsletters", 0))
            with col4:
                st.metric("Today's Newsletters", db_stats.get("today_newsletters", 0))
            
            # MCP tools stats
            st.subheader("🔧 MCP Tools Statistics")
            st.metric("Available MCP Tools", stats.get("mcp_tools_count", 0))
            
            # List available tools
            tools = stats.get("available_mcp_tools", [])
            if tools:
                st.markdown("**Available MCP Tools:**")
                for tool in tools:
                    st.markdown(f"- 🔧 {tool}")
            
            # System status
            st.subheader("⚙️ System Status")
            st.success(f"✅ Status: {stats.get('system_status', 'Unknown')}")
            st.info(f"🕒 Last Updated: {stats.get('last_updated', 'Unknown')}")
            
        else:
            st.error("❌ Failed to fetch statistics")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Make sure the FastAPI backend is running on localhost:8000")

def show_ai_chatbot_page():
    """Display interactive AI chatbot for newsletter generation and news queries"""
    st.header("🤖 AI Newsletter Chatbot")
    st.markdown("**Chat with our AI agents to generate personalized newsletters and ask questions**")
    
    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "current_newsletter" not in st.session_state:
        st.session_state.current_newsletter = None
    
    # Sidebar for configuration
    with st.sidebar:
        st.subheader("⚙️ Configuration")
        
        # User email (optional)
        user_email = st.text_input("Your Email (Optional)", placeholder="your.email@example.com", help="Add your email to send newsletters directly to your inbox")
        
        # Store email in session state
        st.session_state.user_email = user_email
        
        # Topics selection
        topics = st.multiselect(
            "Topics of Interest:",
            ["technology", "business", "finance", "politics", "science", "health", "sports", "entertainment"],
            default=["technology", "business"]
        )
        
        # News source selection
        news_source = st.selectbox(
            "News Source:",
            ["Auto", "Yahoo Finance", "Google News", "RSS Feeds"],
            help="Choose your preferred news source. 'Auto' will select the best source based on your topics."
        )
        
        # Store the selected news source in session state
        st.session_state.selected_news_source = news_source
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📰 Generate Newsletter", use_container_width=True, key="generate_newsletter"):
                if topics:
                    generate_newsletter(topics, user_email, news_source)
                else:
                    st.error("Please select at least one topic")
        
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
                st.session_state.chat_history = []
                st.session_state.current_newsletter = None
                st.rerun()
    
    # Main chat interface
    st.subheader("💬 Chat with AI Agents")
    
    # Display welcome message if chat is empty
    if not st.session_state.chat_history:
        welcome_message = """🤖 **Welcome to your AI Newsletter Assistant!**

I'm here to help you create personalized newsletters and answer your questions about current events.

**What I can do:**
- 📰 Generate personalized newsletters (no email required!)
- 💬 Answer questions about news and topics
- 📧 Send newsletters to your email (optional)
- 🔍 Provide insights on specific subjects
- 🎯 Choose your preferred news source (LLM, Yahoo Finance, NewsAPI, RSS)

**Quick Start:**
1. Select your topics of interest in the sidebar
2. Choose your preferred news source (or leave as "Auto")
3. Click "Generate Newsletter" or ask me to create one
4. View the generated newsletter content
5. Optionally add your email to send it to your inbox

**News Sources:**
- **Auto**: Smart selection based on your topics
- **Yahoo Finance**: Real financial and stock news
- **Google News**: Latest news from Google's news aggregation
- **RSS Feeds**: Curated feeds from trusted sources

**Try saying:**
- "Generate a technology newsletter"
- "Create a business summary"
- "What's the latest in AI news?"
- "Help me understand current events"
- "Send me a business summary" (if you add your email)

What would you like to explore today?"""
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": welcome_message
        })
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # If it's a newsletter response, show the newsletter content directly
                    if message.get("type") == "newsletter":
                        newsletter_data = message.get("newsletter_data")
                        if newsletter_data:
                            # Show newsletter preview directly
                            show_newsletter_preview(newsletter_data)
    
    # Chat input
    user_input = st.chat_input("Ask me anything about news, generate a newsletter, or request specific topics...")
    
    if user_input:
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Process user input and generate response
        process_user_input(user_input, user_email, topics)
        
        # Rerun to update the chat display
        st.rerun()

def generate_newsletter(topics, user_email, news_source):
    """Generate a newsletter and add to chat history"""
    with st.spinner(f"🤖 AI agents are generating your newsletter from {news_source}..."):
        try:
            # Use the new endpoint that doesn't require email
            response = requests.post(f"{API_BASE_URL}/generate-newsletter-content", json={
                "topics": topics,
                "email": user_email if user_email else None,
                "news_source": news_source
            })
            
            if response.status_code == 200:
                result = response.json()
                newsletter_data = result.get("newsletter", {})
                
                # Get current timestamp
                current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
                
                # Create assistant response with actual content and source info
                assistant_message = f"""✅ **Newsletter Generated Successfully!**

📊 **Summary:**
- **Topics:** {', '.join(topics)}
- **News Source:** {news_source}
- **News Count:** {result.get('news_count', 0)} articles
- **Generated:** {current_time}
- **Generation Method:** AI-powered multi-agent system

📰 **Your personalized newsletter is ready!** 

The newsletter content is displayed below. You can:
- 📖 Read the full newsletter content
- 📧 Send it to your email (if you added your email in the sidebar)
- 💬 Ask me to modify or regenerate it
- 🔍 Ask questions about specific topics

What would you like to do next?"""
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "type": "newsletter",
                    "newsletter_data": newsletter_data
                })
                
                st.session_state.current_newsletter = newsletter_data
                
            else:
                error_message = f"❌ **Newsletter generation failed:** {response.text}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_message
                })
                
        except Exception as e:
            error_message = f"❌ **Error:** {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message
            })

def process_user_input(user_input, email, topics):
    """Process user input and generate appropriate response"""
    input_lower = user_input.lower()
    
    # Check for newsletter generation requests
    if any(keyword in input_lower for keyword in ["generate", "create", "make", "newsletter", "summary", "send me"]):
        if topics:
            # Get the current news source from session state or default to Auto
            news_source = st.session_state.get("selected_news_source", "Auto")
            generate_newsletter(topics, email, news_source)
        else:
            response = "❌ **Please select at least one topic in the sidebar first.**"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
    
    # Check for email sending requests
    elif any(keyword in input_lower for keyword in ["send", "email", "mail", "deliver"]):
        if st.session_state.current_newsletter and email:
            send_newsletter_email(email, st.session_state.current_newsletter)
        else:
            if not email:
                response = "❌ **Please add your email in the sidebar to send newsletters.**"
            else:
                response = "❌ **No newsletter available to send. Please generate one first.**"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
    
    # Check for topic-specific requests
    elif any(keyword in input_lower for keyword in ["technology", "tech", "ai", "software", "programming", "startup"]):
        response = """🤖 **Technology News Available!**

I can help you with technology-related content:

**Available Topics:**
- 🤖 Artificial Intelligence & Machine Learning
- 💻 Software Development & Programming
- 🚀 Startups & Innovation
- 📱 Mobile & Web Technologies
- 🔒 Cybersecurity & Privacy
- ☁️ Cloud Computing & DevOps

**Quick Actions:**
- Generate a technology newsletter
- Ask about specific tech topics
- Get the latest AI news
- Learn about new programming trends

What specific technology topic interests you?"""
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
    
    elif any(keyword in input_lower for keyword in ["business", "finance", "economy", "market", "stock", "investment"]):
        response = """🤖 **Business & Finance News Available!**

I can help you with business and financial content:

**Available Topics:**
- 💼 Business Strategy & Management
- 📈 Stock Market & Investments
- 🏦 Banking & Financial Services
- 🌍 Global Economy & Trade
- 🏢 Corporate News & Earnings
- 💰 Cryptocurrency & Fintech

**Quick Actions:**
- Generate a business newsletter
- Get market insights
- Learn about investment opportunities
- Track economic trends

What business or finance topic would you like to explore?"""
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
    
    # General help and information
    elif any(keyword in input_lower for keyword in ["help", "what can you do", "how does this work", "guide"]):
        response = """🤖 **How I Can Help You**

I'm your AI newsletter assistant! Here's what I can do:

**📰 Newsletter Generation:**
- Create personalized newsletters on any topic
- No email required - just select your topics
- Real-time news gathering and AI-powered content creation

**💬 News & Information:**
- Answer questions about current events
- Provide insights on specific topics
- Share the latest news and trends

**📧 Email Features:**
- Send newsletters directly to your inbox (optional)
- Save and share newsletter content
- Customize delivery preferences

**🔧 How to Use:**
1. Select topics in the sidebar
2. Click "Generate Newsletter" or ask me to create one
3. View the content and optionally send to your email
4. Ask follow-up questions or request modifications

**Try saying:**
- "Generate a technology newsletter"
- "What's happening in AI today?"
- "Create a business summary"
- "Help me understand current events"

What would you like to explore?"""
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
    
    # Default response for unrecognized input
    else:
        response = f"""🤖 **I understand you're asking about: "{user_input}"**

I can help you with:
- 📰 Generating newsletters on your topics
- 💬 Answering questions about news and current events
- 📧 Sending content to your email (if you add it)

**Quick Actions:**
- Use the sidebar to configure your topics
- Click "Generate Newsletter" for instant creation
- Use "Clear Chat" to start fresh

Would you like me to generate a newsletter on your selected topics, or do you have a specific question about current events?"""
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

def show_newsletter_preview(newsletter_data):
    """Display newsletter preview in chat"""
    # Show the raw newsletter content
    st.subheader("📰 Newsletter Content")
    
    # Display the main content
    content = newsletter_data.get("content", "No content available")
    st.text_area(
        "Newsletter Content",
        value=content,
        height=400,
        help="This is the raw newsletter content generated by our AI agents"
    )
    
    # Show newsletter details
    with st.expander("📊 Newsletter Details"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Subject:** {newsletter_data.get('subject', 'No subject')}")
            st.markdown(f"**Topics:** {', '.join(newsletter_data.get('topics', []))}")
            st.markdown(f"**Generated:** {newsletter_data.get('generated_at', 'Unknown')}")
            st.markdown(f"**Method:** {newsletter_data.get('generation_method', 'Unknown')}")
        
        with col2:
            # Show news source information
            news_count = newsletter_data.get('news_count', 0)
            st.markdown(f"**News Articles:** {news_count}")
            
            # Show detailed news source info if available
            if newsletter_data.get('news_source'):
                st.markdown(f"**Primary Source:** {newsletter_data.get('news_source')}")
            
            # Show timestamp information
            if newsletter_data.get('fetched_at'):
                st.markdown(f"**Data Fetched:** {newsletter_data.get('fetched_at')}")
            
            # Show if this is from a specific source vs auto-selected
            if newsletter_data.get('generation_method') == 'llm_ai':
                st.info("🤖 Generated using AI with real news data")
            elif newsletter_data.get('generation_method') == 'fallback_ai':
                st.warning("⚠️ Used fallback content (real news sources may be unavailable)")
    
    # Email sending section
    st.subheader("📧 Send Newsletter")
    
    # Check if user has provided email
    user_email = st.session_state.get('user_email', '')
    
    if user_email:
        st.info(f"📧 Ready to send to: {user_email}")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if st.button("📧 Send Newsletter", type="primary", use_container_width=True, key="send_newsletter"):
                send_newsletter_email(user_email, newsletter_data)
        
        with col2:
            st.markdown("The newsletter will be sent as a beautiful HTML email to your inbox.")
    else:
        st.warning("⚠️ To send this newsletter via email, please add your email address in the sidebar.")
        st.markdown("**How to send via email:**")
        st.markdown("1. Add your email address in the sidebar")
        st.markdown("2. Click 'Send Newsletter' button above")
        st.markdown("3. Check your inbox for the beautiful formatted newsletter")
    
    # HTML preview option (collapsed by default)
    with st.expander("🎨 View HTML Version"):
        html_content = newsletter_data.get("html_content", "")
        if html_content:
            # Add styling for better preview
            styled_html = f"""
            <div style="
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 15px; 
                background-color: #f9f9f9;
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                font-size: 14px;
            ">
                {html_content}
            </div>
            """
            st.markdown(styled_html, unsafe_allow_html=True)
        else:
            st.warning("No HTML content available")

def send_newsletter_email(email, newsletter_data):
    """Send newsletter via email"""
    with st.spinner("📧 Sending newsletter to your email..."):
        try:
            response = requests.post(f"{API_BASE_URL}/send-newsletter", json={
                "email": email,
                "newsletter_data": newsletter_data
            })
            
            if response.status_code == 200:
                result = response.json()
                success_message = f"✅ **Newsletter sent successfully to {email}!**\n\nCheck your inbox for the beautiful newsletter."
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": success_message
                })
            else:
                error_message = f"❌ **Email sending failed:** {response.text}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_message
                })
                
        except Exception as e:
            error_message = f"❌ **Error sending email:** {str(e)}"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_message
            })

def test_news_fetching():
    """Test news fetching functionality"""
    with st.spinner("Fetching news..."):
        try:
            response = requests.post(f"{API_BASE_URL}/mcp/test-tool", json={
                "tool_name": "fetch_news",
                "parameters": {"topics": ["technology"]}
            })
            
            if response.status_code == 200:
                result = response.json()
                if result["result"]["success"]:
                    data = result["result"]["data"]
                    st.success(f"✅ Fetched {data['news_count']} articles")
                    
                    # Show sample articles
                    for i, article in enumerate(data["articles"][:3]):
                        st.markdown(f"**{i+1}. {article.get('title', 'No title')}**")
                        st.markdown(f"*Source: {article.get('source', 'Unknown')}*")
                else:
                    st.error(f"❌ {result['result']['error']}")
            else:
                st.error("❌ Tool test failed")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def test_stock_data():
    """Test stock data functionality"""
    with st.spinner("Fetching stock data..."):
        try:
            response = requests.post(f"{API_BASE_URL}/mcp/test-tool", json={
                "tool_name": "fetch_stock_data",
                "parameters": {"symbols": ["AAPL", "GOOGL", "MSFT"]}
            })
            
            if response.status_code == 200:
                result = response.json()
                if result["result"]["success"]:
                    data = result["result"]["data"]
                    st.success("✅ Stock data fetched successfully")
                    
                    # Show stock data
                    for symbol, info in data["stocks"].items():
                        if "error" not in info:
                            st.markdown(f"**{symbol}**: ${info.get('current_price', 'N/A')}")
                else:
                    st.error(f"❌ {result['result']['error']}")
            else:
                st.error("❌ Tool test failed")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def run_full_mcp_demo():
    """Run complete MCP demonstration"""
    with st.spinner("Running complete MCP demonstration..."):
        try:
            response = requests.get(f"{API_BASE_URL}/mcp/demo")
            
            if response.status_code == 200:
                demo_data = response.json()
                st.success("✅ MCP Demo completed successfully!")
                
                # Display demo results
                demos = demo_data.get("demos", {})
                
                for demo_name, demo_result in demos.items():
                    with st.expander(f"📊 {demo_name.replace('_', ' ').title()}"):
                        if demo_result.get("success"):
                            st.success("✅ Tool executed successfully")
                            data = demo_result.get("data", {})
                            st.json(data)
                        else:
                            st.error(f"❌ {demo_result.get('error', 'Unknown error')}")
            else:
                st.error("❌ Demo failed")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 