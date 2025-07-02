import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime
import json
import re
from mcp.tools import MCPToolRegistry, ToolCall, ToolResult

class CrewManager:
    def __init__(self):
        """Initialize the CrewManager with MCP tools and agents"""
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key")
        )
        
        # Initialize MCP Tool Registry
        self.mcp_registry = MCPToolRegistry()
        
        # Get actual tool instances
        self.tools = self.mcp_registry.get_all_tools()
        
        # Create agents with MCP tool access
        self.researcher_agent = self._create_researcher_agent()
        self.analyst_agent = self._create_analyst_agent()
        self.writer_agent = self._create_writer_agent()
        self.editor_agent = self._create_editor_agent()
        
        print("🤖 CrewManager initialized with MCP tools")
        print(f"📦 Available MCP tools: {list(self.tools.keys())}")

    def _create_researcher_agent(self) -> Agent:
        """Create the researcher agent with MCP tools for gathering news"""
        return Agent(
            role="News Researcher",
            goal="Analyze news data and provide detailed insights for newsletter creation",
            backstory="""You are an expert news researcher who excels at analyzing news articles 
            and extracting key insights. You provide detailed analysis that helps create engaging 
            newsletter content. You always provide comprehensive analysis with specific details 
            from the news articles provided.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                self.tools["fetch_news"],           # MCP Tool for fetching news
                self.tools["fetch_stock_data"],     # MCP Tool for stock data
                self.tools["analyze_trends"]        # MCP Tool for trend analysis
            ],
            llm=self.llm
        )

    def _create_analyst_agent(self) -> Agent:
        """Create the analyst agent with MCP tools for analyzing content"""
        return Agent(
            role="News Analyst",
            goal="Analyze news content for relevance, impact, and significance using MCP tools",
            backstory="""You are a seasoned news analyst with access to MCP tools for 
            trend analysis and content summarization. You excel at understanding context, 
            identifying patterns, and extracting key insights from news data.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                self.tools["analyze_trends"],       # MCP Tool for trend analysis
                self.tools["summarize_content"]     # MCP Tool for content summarization
            ],
            llm=self.llm
        )

    def _create_writer_agent(self) -> Agent:
        """Create the writer agent with MCP tools for creating content"""
        return Agent(
            role="Newsletter Writer",
            goal="Create engaging, informative, and personalized newsletter content using MCP tools",
            backstory="""You are a talented newsletter writer who specializes in creating 
            engaging, personalized newsletters. You always write complete newsletter content 
            with proper subject lines, greetings, article summaries, and closing messages. 
            You make content conversational and informative, typically 300-500 words. 
            You always include actual URLs when mentioning "read more" or similar phrases.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                self.tools["generate_email_template"],  # MCP Tool for email templates
                self.tools["summarize_content"]         # MCP Tool for content summarization
            ],
            llm=self.llm
        )

    def _create_editor_agent(self) -> Agent:
        """Create the editor agent for reviewing and polishing content"""
        return Agent(
            role="Newsletter Editor",
            goal="Review, polish, and ensure the highest quality of newsletter content",
            backstory="""You are a meticulous editor with years of experience in 
            newsletter publishing. You ensure content is clear, accurate, engaging, 
            and follows best practices for email newsletters. You always provide 
            the final polished newsletter content, not just a status message.""",
            verbose=True,
            allow_delegation=False,
            tools=[
                self.tools["summarize_content"]     # MCP Tool for content review
            ],
            llm=self.llm
        )

    async def generate_newsletter(self, email: str, topics: List[str], news_data: List[Dict], sources_used=None, date_fetched=None) -> Dict[str, Any]:
        """Generate a personalized newsletter using MCP tools and multi-agent crew"""
        try:
            print(f"🤖 Starting MCP-powered newsletter generation...")
            print(f"📧 Email: {email}")
            print(f"📋 Topics: {topics}")
            print(f"📰 News items: {len(news_data)}")
            
            # If no news data, use fallback
            if not news_data:
                print("⚠️ No news data provided, using fallback newsletter")
                return self._generate_fallback_newsletter(email, topics, news_data, sources_used, date_fetched)
            
            # Format news data for agents
            news_summary = ""
            for i, news in enumerate(news_data[:10], 1):  # Limit to 10 articles
                title = news.get('title', 'No title')
                summary = news.get('summary', 'No summary')
                source = news.get('source', 'Unknown')
                url = news.get('url', '')
                news_summary += f"{i}. {title}\n   Summary: {summary}\n   Source: {source}\n   URL: {url}\n\n"
            
            # Try CrewAI first, but have a robust fallback
            try:
                # Create tasks for the crew with MCP tool integration
                tasks = [
                    # Task 1: Generate newsletter content directly
                    Task(
                        description=f"""
                        Create a personalized newsletter for user {email} based on the provided news data.
                        
                        News articles to include:
                        {news_summary}
                        
                        Your task:
                        1. Create an engaging subject line for the newsletter
                        2. Write a warm, personalized greeting
                        3. Summarize the most important news stories in an engaging way
                        4. Include the actual URLs from the news data when mentioning "read more"
                        5. Add a closing message
                        6. Make it conversational and informative (300-500 words)
                        
                        Format your response as:
                        Subject: [Your subject line]
                        
                        [Newsletter content here]
                        
                        Context: Topics: {topics}, User: {email}, Sources: {', '.join(sources_used or [])}, Date: {date_fetched or datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
                        
                        IMPORTANT: Write the complete newsletter content, not just a status message.
                        """,
                        agent=self.writer_agent,
                        expected_output="Complete newsletter with subject and engaging content"
                    )
                ]
                
                # Create and run the crew
                crew = Crew(
                    agents=[self.writer_agent],
                    tasks=tasks,
                    verbose=True
                )
                
                print(f"🚀 Executing crew with MCP tools...")
                result = await asyncio.get_event_loop().run_in_executor(None, lambda: crew.kickoff())
                
                print(f"✅ Crew execution completed")
                
                # Parse the crew result
                newsletter_content = self._parse_crew_result(result)
                
            except Exception as crew_error:
                print(f"⚠️ CrewAI failed: {str(crew_error)}, using direct LLM")
                newsletter_content = self._generate_direct_llm_newsletter(email, topics, news_data, sources_used, date_fetched)
            
            # Add metadata
            newsletter_content.update({
                "email": email,
                "topics": topics,
                "generated_at": datetime.utcnow().isoformat(),
                "news_count": len(news_data),
                "generation_method": "mcp_crew_ai",
                "sources_used": sources_used or [],
                "date_fetched": date_fetched or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            print(f"📊 Final stats: {len(newsletter_content.get('content', '').split())} words, {len(news_data)} news items")
            return newsletter_content
            
        except Exception as e:
            print(f"❌ Error in MCP newsletter generation: {str(e)}")
            logging.error(f"Error in MCP newsletter generation: {str(e)}")
            return self._generate_fallback_newsletter(email, topics, news_data, sources_used, date_fetched)

    def _parse_crew_result(self, result) -> Dict[str, Any]:
        """Parse the result from the crew execution"""
        try:
            # Extract content from crew result
            if hasattr(result, 'raw'):
                content = result.raw
            elif hasattr(result, 'output'):
                content = result.output
            else:
                content = str(result)
            
            # Clean the content
            content = self._clean_content(content)
            
            # Check if we got meaningful content (not just status messages)
            if len(content.strip()) < 100 or any(phrase in content.lower() for phrase in [
                "final polished newsletter ready for delivery",
                "proceed without using a tool",
                "unfortunately, there was an unexpected error",
                "will proceed without using a tool"
            ]):
                print("⚠️ CrewAI didn't generate proper content, using LLM fallback")
                return self._generate_llm_newsletter_fallback(content, result)
            
            # Try to extract subject line and content
            lines = content.split('\n')
            subject_line = ""
            newsletter_body = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for subject line indicators
                if any(keyword in line.lower() for keyword in ["subject:", "title:", "subject line:", "newsletter title:"]):
                    subject_line = line.split(':', 1)[-1].strip()
                    subject_line = subject_line.strip('"\'')
                else:
                    newsletter_body += line + '\n'
            
            # If no subject found, create a default one
            if not subject_line:
                subject_line = "Your Daily News Summary"
            
            # Clean up the newsletter body
            newsletter_body = newsletter_body.strip()
            
            return {
                "subject": subject_line,
                "content": newsletter_body,
                "html_content": self._convert_to_html(newsletter_body)
            }
            
        except Exception as e:
            logging.error(f"Error parsing crew result: {str(e)}")
            return {
                "subject": "Your Daily News Summary",
                "content": "We're experiencing some technical difficulties. Please try again later.",
                "html_content": self._convert_to_html("We're experiencing some technical difficulties. Please try again later.")
            }

    def _clean_content(self, content: str) -> str:
        """Clean content by removing CSS, HTML tags, and other artifacts"""
        # Remove CSS blocks
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove CSS properties that might cause issues
        content = re.sub(r'font-family[^;]*;?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'color[^;]*;?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'background[^;]*;?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'font-size[^;]*;?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'font-weight[^;]*;?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'text-align[^;]*;?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'margin[^;]*;?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'padding[^;]*;?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'border[^;]*;?', '', content, flags=re.IGNORECASE)
        
        # Remove any remaining CSS-like patterns
        content = re.sub(r'{[^}]*}', '', content)
        
        # Remove CSS selectors
        content = re.sub(r'\.[a-zA-Z0-9_-]+\s*{', '', content)
        content = re.sub(r'#[a-zA-Z0-9_-]+\s*{', '', content)
        content = re.sub(r'[a-zA-Z0-9_-]+\s*{', '', content)
        
        # Remove any remaining semicolons that might be from CSS
        content = re.sub(r';\s*', ' ', content)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove any remaining problematic patterns
        content = re.sub(r'font-family\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'color\s*:', '', content, flags=re.IGNORECASE)
        content = re.sub(r'background\s*:', '', content, flags=re.IGNORECASE)
        
        return content.strip()

    def _convert_to_html(self, content: str) -> str:
        """Convert plain text content to HTML format"""
        html_content = content

        # 1. Convert URLs to clickable links - handle "Read more:" format first
        html_content = re.sub(
            r'Read more: (https?://[^\s\)\]\>\<\*]+)',
            r'<a href="\1" target="_blank" style="color: #0066cc; text-decoration: underline;">Read more</a>',
            html_content
        )
        # 2. Handle the new [LINK: URL] format
        html_content = re.sub(
            r'\[LINK: (https?://[^\s\]\>\<\*]+)\]',
            r'<a href="\1" target="_blank" style="color: #0066cc; text-decoration: underline;">Read more</a>',
            html_content
        )
        # 3. Then convert any remaining standalone URLs (but not already converted ones)
        html_content = re.sub(
            r'(?<!href=")(https?://[^\s\)\]\>\<\*]+)(?!")',
            r'<a href="\1" target="_blank" style="color: #0066cc; text-decoration: underline;">\1</a>',
            html_content
        )
        # 4. Convert bold text (**text** to <strong>text</strong>)
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        # 5. Convert italic text (*text* to <em>text</em>)
        html_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html_content)
        # 6. Convert line breaks to HTML
        html_content = html_content.replace('\n', '<br>')
        # 7. Remove any accidental HTML tags inside links
        html_content = re.sub(r'(</?(em|strong)>)((https?://[^\s\)\]\>\<]+))', r'\3', html_content)
        # Simple HTML wrapper without extra styling
        html_template = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            {html_content}
        </div>
        """
        return html_template

    def _generate_fallback_newsletter(self, email: str, topics: List[str], news_data: List[Dict], sources_used=None, date_fetched=None) -> Dict[str, Any]:
        """Generate a simple newsletter as fallback"""
        subject = f"Your Daily News Summary - {', '.join(topics)}"
        
        # Create a proper greeting
        greeting = f"Good morning{f', {email.split('@')[0] if '@' in email else ''}' if email else ''}! 🌅"
        
        content = f"""
{greeting}

I hope this email finds you well and ready for an exciting update on your favorite topics: {', '.join(topics)}!

Here's your personalized news summary for today:

"""
        
        if news_data:
            content += f"📰 **Top Stories ({len(news_data)} articles):**\n\n"
            
            for i, news in enumerate(news_data[:8], 1):  # Limit to 8 news items
                title = news.get('title', 'No title available')
                summary = news.get('summary', 'No summary available')
                source = news.get('source', 'Unknown source')
                url = news.get('url', '')
                
                # Clean up the summary
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                
                content += f"**{i}. {title}**\n"
                content += f"{summary}\n"
                if url:
                    content += f"*Source: {source} | Read more: {url}*\n\n"
                else:
                    content += f"*Source: {source}*\n\n"
        else:
            content += "📰 **Today's News:**\n\n"
            content += "We're currently gathering the latest news for your selected topics. "
            content += "Please check back later for updates, or try refreshing the page.\n\n"
        
        content += f"""
📊 **Summary:**
• Topics covered: {', '.join(topics)}
• News articles: {len(news_data)}
• Generated: {date_fetched or datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}
• Sources used: {', '.join(sources_used) if sources_used else 'N/A'}

Stay informed and have a great day! 

Best regards,
Your AI Newsletter Agent 🤖
(Powered by Multi-Agent AI and MCP Tools)
        """
        
        return {
            "subject": subject,
            "content": content.strip(),
            "html_content": self._convert_to_html(content.strip()),
            "email": email,
            "topics": topics,
            "generated_at": datetime.utcnow().isoformat(),
            "news_count": len(news_data),
            "generation_method": "fallback_ai",
            "sources_used": sources_used or [],
            "date_fetched": date_fetched or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _generate_llm_newsletter_fallback(self, crew_output: str, crew_result) -> Dict[str, Any]:
        """Generate newsletter using direct LLM when CrewAI fails"""
        try:
            # Extract news data from the crew result context
            # This is a simplified approach - in a real implementation, you'd pass news_data through
            prompt = f"""
You are an expert newsletter writer. Create a personalized daily newsletter.

Based on the crew analysis: {crew_output[:500]}...

Create a newsletter that:
1. Has an engaging subject line
2. Starts with a warm greeting
3. Summarizes the most important news stories
4. Is conversational and informative (300-500 words)
5. Ends with an encouraging closing message

Format your response as:
Subject: [Your subject line]

[Newsletter content here]

Make it engaging and informative.
"""
            
            response = asyncio.get_event_loop().run_in_executor(None, lambda: self.llm.invoke(prompt))
            response_str = str(response)
            
            # Clean the response
            content = self._clean_content(response_str)
            
            # Extract subject and content
            lines = content.split('\n')
            subject_line = "Your Daily News Summary"
            newsletter_body = content
            
            # Look for subject line
            for line in lines:
                if line.lower().startswith('subject:'):
                    subject_line = line.split(':', 1)[-1].strip()
                    newsletter_body = '\n'.join(lines[1:])  # Remove subject line from body
                    break
            
            return {
                "subject": subject_line,
                "content": newsletter_body.strip(),
                "html_content": self._convert_to_html(newsletter_body.strip())
            }
            
        except Exception as e:
            logging.error(f"Error in LLM fallback: {str(e)}")
            return {
                "subject": "Your Daily News Summary",
                "content": "We're experiencing some technical difficulties. Please try again later.",
                "html_content": self._convert_to_html("We're experiencing some technical difficulties. Please try again later.")
            }

    def _generate_direct_llm_newsletter(self, email: str, topics: List[str], news_data: List[Dict], sources_used=None, date_fetched=None) -> Dict[str, Any]:
        """Generate newsletter using direct LLM when CrewAI fails"""
        try:
            # Format news data for the prompt
            news_summary = ""
            for i, news in enumerate(news_data[:8], 1):  # Limit to 8 articles
                title = news.get('title', 'No title')
                summary = news.get('summary', 'No summary')
                source = news.get('source', 'Unknown')
                url = news.get('url', '')
                news_summary += f"{i}. {title}\n   Summary: {summary}\n   Source: {source}\n   URL: {url}\n\n"
            
            prompt = f"""
You are an expert newsletter writer. Create a personalized daily newsletter for a user interested in: {', '.join(topics)}

News sources used for this summary: {', '.join(sources_used or [])}

Here are today's top news stories:

{news_summary}

Write a friendly, engaging newsletter that:
1. Starts with a warm greeting
2. Summarizes the most important news stories in a clear, engaging way
3. Highlights key insights and trends
4. Mentions the sources used in the introduction
5. IMPORTANT: When you mention "read more", "check it out", or similar phrases, you MUST include the actual URL that was provided in the news data above.
6. Ends with an encouraging closing message
7. Do NOT include "[Your Name]" or any placeholder text - just end naturally

Make it conversational and informative. Don't use JSON formatting - just write the newsletter content directly.

The newsletter should be about 300-500 words and cover the most relevant stories for someone interested in {', '.join(topics)}.

Format your response as:
Subject: [Your subject line]

[Newsletter content here]

Remember: Always include the actual URLs when referencing "read more" or similar phrases.
"""
            
            response = asyncio.get_event_loop().run_in_executor(None, lambda: self.llm.invoke(prompt))
            response_str = str(response)
            
            # Clean the response
            content = self._clean_content(response_str)
            
            # Extract subject and content
            lines = content.split('\n')
            subject_line = f"Your Daily {', '.join(topics).title()} News Summary"
            newsletter_body = content
            
            # Look for subject line
            for line in lines:
                if line.lower().startswith('subject:'):
                    subject_line = line.split(':', 1)[-1].strip()
                    newsletter_body = '\n'.join(lines[1:])  # Remove subject line from body
                    break
            
            return {
                "subject": subject_line,
                "content": newsletter_body.strip(),
                "html_content": self._convert_to_html(newsletter_body.strip())
            }
            
        except Exception as e:
            logging.error(f"Error in direct LLM newsletter: {str(e)}")
            return self._generate_fallback_newsletter(email, topics, news_data, sources_used, date_fetched)

    async def get_available_mcp_tools(self) -> List[Dict[str, str]]:
        """Get list of available MCP tools"""
        tools = self.mcp_registry.list_tools()
        return tools

    async def test_mcp_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Test a specific MCP tool"""
        try:
            tool = self.mcp_registry.get_tool(tool_name)
            if tool:
                result = await tool._arun(**kwargs)
                return {
                    "tool_name": tool_name,
                    "success": True,
                    "data": result,
                    "error": None
                }
            else:
                return {
                    "tool_name": tool_name,
                    "success": False,
                    "error": f"Tool {tool_name} not found"
                }
        except Exception as e:
            return {
                "tool_name": tool_name,
                "success": False,
                "error": f"Error testing tool {tool_name}: {str(e)}"
            } 