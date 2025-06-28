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
        - **📊 Multiple News Sources**: Yahoo Finance, NewsAPI, RSS feeds, and more
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
                "yahoo_finance", "newsapi", "rss"
            ],
            default=["yahoo_finance", "newsapi", "rss"]
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
        if st.button("Test News Fetching"):
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
    
    with col2:
        st.markdown("### 📈 Stock Data Tool")
        if st.button("Test Stock Data"):
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
    
    # Full demo
    st.subheader("🎬 Complete MCP Demo")
    if st.button("Run Full MCP Demo"):
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
        
        # User email
        user_email = st.text_input("Your Email", placeholder="your.email@example.com")
        
        # Topics selection
        topics = st.multiselect(
            "Topics of Interest:",
            ["technology", "business", "finance", "politics", "science", "health", "sports", "entertainment"],
            default=["technology", "business"]
        )
        
        # Quick actions
        st.subheader("🚀 Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📰 Generate Newsletter", use_container_width=True):
                if user_email and topics:
                    generate_newsletter(user_email, topics)
                else:
                    st.error("Please enter email and select topics")
        
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
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
- 📰 Generate personalized newsletters
- 💬 Answer questions about news and topics
- 📧 Send newsletters to your email
- 🔍 Provide insights on specific subjects

**Quick Start:**
1. Configure your email and topics in the sidebar
2. Ask me to generate a newsletter
3. View and send the newsletter to your email

**Try saying:**
- "Generate a technology newsletter"
- "What's the latest in AI news?"
- "Help me understand current events"
- "Send me a business summary"

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
                    
                    # If it's a newsletter response, show additional options
                    if message.get("type") == "newsletter":
                        newsletter_data = message.get("newsletter_data")
                        if newsletter_data:
                            # Newsletter preview
                            with st.expander("📰 View Newsletter"):
                                show_newsletter_preview(newsletter_data)
                            
                            # Email sending option
                            if user_email:
                                if st.button("📧 Send to Email", key=f"send_{len(st.session_state.chat_history)}"):
                                    send_newsletter_email(user_email, newsletter_data)
    
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

def generate_newsletter(email, topics):
    """Generate a newsletter and add to chat history"""
    with st.spinner("🤖 AI agents are generating your newsletter..."):
        try:
            response = requests.post(f"{API_BASE_URL}/test-newsletter", json={
                "email": email,
                "topics": topics
            })
            
            if response.status_code == 200:
                result = response.json()
                newsletter_data = result.get("newsletter", {})
                
                # Create assistant response
                assistant_message = f"""✅ **Newsletter Generated Successfully!**

📊 **Summary:**
- **News Count:** {newsletter_data.get('news_count', 0)} articles
- **Topics:** {', '.join(newsletter_data.get('topics', []))}
- **Generation Method:** {newsletter_data.get('generation_method', 'Unknown')}

📰 **Your personalized newsletter is ready!** 

You can:
- 📖 View the full newsletter content
- 📧 Send it to your email
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
        if email and topics:
            generate_newsletter(email, topics)
        else:
            response = "❌ **Please configure your email and topics in the sidebar first.**"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
    
    # Check for email sending requests
    elif any(keyword in input_lower for keyword in ["send", "email", "mail", "deliver"]):
        if st.session_state.current_newsletter and email:
            send_newsletter_email(email, st.session_state.current_newsletter)
        else:
            response = "❌ **No newsletter available to send. Please generate one first, or configure your email in the sidebar.**"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })
    
    # Check for topic-specific requests
    elif any(keyword in input_lower for keyword in ["technology", "tech", "ai", "software", "programming", "startup"]):
        response = """🤖 **Technology News Available!**

I can help you with:
- 📰 Latest tech news and AI developments
- 🚀 Startup and innovation updates
- 💻 Software and programming trends
- 📱 Mobile and consumer tech
- 🤖 AI and machine learning breakthroughs

**Recent tech highlights:**
- AI developments and ChatGPT updates
- Major tech company announcements
- Startup funding and acquisitions
- New software releases and updates

Would you like me to generate a technology-focused newsletter?"""
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
    
    elif any(keyword in input_lower for keyword in ["business", "finance", "market", "economy", "stocks", "investment"]):
        response = """💼 **Business & Finance News Available!**

I can help you with:
- 📈 Market updates and stock news
- 🏢 Corporate developments and earnings
- 💰 Financial trends and analysis
- 🌍 Global business news
- 📊 Economic indicators and reports

**Recent business highlights:**
- Stock market movements and trends
- Company earnings and financial reports
- Mergers and acquisitions
- Economic policy changes

Would you like me to generate a business-focused newsletter?"""
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
    
    elif any(keyword in input_lower for keyword in ["science", "research", "discovery", "study"]):
        response = """🔬 **Science News Available!**

I can help you with:
- 🧬 Latest scientific discoveries
- 🔬 Research breakthroughs
- 🌍 Environmental and climate science
- 🚀 Space exploration updates
- 🏥 Medical and health research

**Recent science highlights:**
- Breakthrough research findings
- Space missions and discoveries
- Medical advancements
- Environmental studies

Would you like me to generate a science-focused newsletter?"""
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
    
    # Check for help requests
    elif any(keyword in input_lower for keyword in ["help", "what can you do", "how", "?", "assist"]):
        response = """🤖 **I'm your AI Newsletter Assistant!**

Here's what I can do for you:

📰 **Newsletter Generation:**
- Generate personalized newsletters
- Focus on specific topics (tech, business, science, etc.)
- Include latest news from multiple sources
- Create both text and HTML versions

💬 **Chat Features:**
- Answer questions about current events
- Provide news summaries and insights
- Help you discover interesting topics
- Intelligent topic-based responses

📧 **Email Features:**
- Send newsletters directly to your email
- Customize delivery preferences
- Beautiful HTML email formatting

**Try asking me:**
- "Generate a technology newsletter"
- "What's the latest in AI news?"
- "Create a business summary"
- "Send the newsletter to my email"
- "Tell me about recent tech developments"

**Quick Actions:**
- Use the sidebar to configure your email and topics
- Click "Generate Newsletter" for instant creation
- Use "Clear Chat" to start fresh

What would you like to explore?"""
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
    
    # Check for status or current newsletter requests
    elif any(keyword in input_lower for keyword in ["status", "current", "latest", "what do you have", "show me"]):
        if st.session_state.current_newsletter:
            newsletter_data = st.session_state.current_newsletter
            response = f"""📰 **Current Newsletter Status:**

**Subject:** {newsletter_data.get('subject', 'No subject')}
**Topics:** {', '.join(newsletter_data.get('topics', []))}
**Articles:** {newsletter_data.get('news_count', 0)} items
**Generated:** {newsletter_data.get('generated_at', 'Unknown')}

You can:
- 📖 View the full newsletter content
- 📧 Send it to your email
- 🔄 Generate a new one with different topics
- 💬 Ask me to modify it

What would you like to do?"""
        else:
            response = "📭 **No newsletter generated yet.**\n\nI can help you create one! Just ask me to generate a newsletter or use the sidebar to configure your preferences."
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
    
    # Default response for other inputs
    else:
        response = f"""🤖 **I understand you're asking about: "{user_input}"**

I can help you with:
- 📰 Generating newsletters on this topic
- 🔍 Finding related news and information
- 💬 Discussing current events
- 📧 Sending content to your email

**Quick suggestions:**
- "Generate a newsletter about this topic"
- "What's the latest news on this?"
- "Send me a summary"
- "Tell me more about this"

Would you like me to generate a newsletter covering this topic, or do you have a specific question?"""
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })

def show_newsletter_preview(newsletter_data):
    """Display newsletter preview in chat"""
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📝 Text", "🎨 HTML", "📊 Details"])
    
    with tab1:
        st.text_area(
            "Newsletter Content",
            value=newsletter_data.get("content", "No content"),
            height=300,
            disabled=True
        )
    
    with tab2:
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
    
    with tab3:
        st.markdown(f"**Subject:** {newsletter_data.get('subject', 'No subject')}")
        st.markdown(f"**Topics:** {', '.join(newsletter_data.get('topics', []))}")
        st.markdown(f"**Generated:** {newsletter_data.get('generated_at', 'Unknown')}")
        st.markdown(f"**Method:** {newsletter_data.get('generation_method', 'Unknown')}")

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

if __name__ == "__main__":
    main() 