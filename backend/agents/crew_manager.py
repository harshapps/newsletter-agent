import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import asyncio
import logging
from datetime import datetime
import json
import re

class CrewManager:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize agents without tools for now
        self.researcher_agent = self._create_researcher_agent()
        self.analyst_agent = self._create_analyst_agent()
        self.writer_agent = self._create_writer_agent()
        self.editor_agent = self._create_editor_agent()
    
    def _create_researcher_agent(self) -> Agent:
        """Create the researcher agent for gathering news"""
        return Agent(
            role="News Researcher",
            goal="Gather comprehensive and relevant news from multiple sources",
            backstory="""You are an expert news researcher with years of experience 
            in finding and verifying information from various sources. You have a keen 
            eye for identifying important stories and trends.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_analyst_agent(self) -> Agent:
        """Create the analyst agent for analyzing news content"""
        return Agent(
            role="News Analyst",
            goal="Analyze news content for relevance, impact, and significance",
            backstory="""You are a seasoned news analyst who excels at understanding 
            the context and implications of news stories. You can identify trends, 
            patterns, and the most important aspects of any news item.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_writer_agent(self) -> Agent:
        """Create the writer agent for creating newsletter content"""
        return Agent(
            role="Newsletter Writer",
            goal="Create engaging, informative, and personalized newsletter content",
            backstory="""You are a talented newsletter writer who knows how to 
            transform complex information into clear, engaging content. You have a 
            knack for making news accessible and interesting to readers.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _create_editor_agent(self) -> Agent:
        """Create the editor agent for reviewing and polishing content"""
        return Agent(
            role="Newsletter Editor",
            goal="Review, polish, and ensure the highest quality of newsletter content",
            backstory="""You are a meticulous editor with years of experience in 
            newsletter publishing. You ensure content is clear, accurate, engaging, 
            and follows best practices for email newsletters.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    async def generate_newsletter(self, email: str, topics: List[str], news_data: List[Dict], sources_used=None, date_fetched=None) -> Dict[str, Any]:
        """Generate a personalized newsletter using the multi-agent crew"""
        try:
            print(f"🤖 Starting newsletter generation process...")
            print(f"📧 Email: {email}")
            print(f"📋 Topics: {topics}")
            print(f"📰 News items: {len(news_data)}")
            print(f"🔍 Step 1: Analyzing news data...")
            for i, news in enumerate(news_data[:3], 1):
                print(f"   📄 Article {i}: {news.get('title', 'No title')[:50]}...")
            print(f"✍️ Step 2: Generating newsletter content with LLM...")
            newsletter_content = await self._generate_llm_newsletter(email, topics, news_data, sources_used, date_fetched)
            print(f"📝 Step 3: Creating HTML version...")
            newsletter_content.update({
                "email": email,
                "topics": topics,
                "generated_at": datetime.utcnow().isoformat(),
                "news_count": len(news_data),
                "sources_used": sources_used or [],
                "date_fetched": date_fetched or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            })
            print(f"✅ Newsletter generation completed successfully!")
            print(f"📊 Final stats: {len(newsletter_content.get('content', '').split())} words, {len(news_data)} news items")
            return newsletter_content
        except Exception as e:
            print(f"❌ Error in newsletter generation: {str(e)}")
            logging.error(f"Error in newsletter generation: {str(e)}")
            logging.error(f"Error type: {type(e)}")
            logging.error(f"Error details: {e}")
            return self._generate_fallback_newsletter(email, topics, news_data, sources_used, date_fetched)
    
    async def _generate_llm_newsletter(self, email: str, topics: List[str], news_data: List[Dict], sources_used=None, date_fetched=None) -> Dict[str, Any]:
        """Use the LLM to compose a newsletter from news_data."""
        if not news_data:
            return self._generate_fallback_newsletter(email, topics, news_data, sources_used, date_fetched)
        
        prompt = f"""
You are an expert newsletter writer. Create a personalized daily newsletter for a user interested in: {', '.join(topics)}

News sources used for this summary: {', '.join(sources_used or [])}

IMPORTANT: Each news item below includes a [LINK: URL] format. When you write about these stories, you MUST use these exact URLs when you mention "read more", "check it out", or similar phrases. Do not create generic links or placeholder text.

Here are today's top news stories:

"""
        for i, news in enumerate(news_data, 1):
            url = news.get('url', '')
            url_text = f" [LINK: {url}]" if url else ""
            prompt += f"{i}. {news.get('title', 'No title')}\n   {news.get('summary', 'No summary')}{url_text}\n   Source: {news.get('source', 'Unknown')}\n\n"
        
        prompt += f"""
Write a friendly, engaging newsletter that:
1. Starts with a warm greeting
2. Summarizes the most important news stories in a clear, engaging way
3. Highlights key insights and trends
4. Mentions the sources used in the introduction
5. IMPORTANT: When you mention "read more", "check it out", or similar phrases, you MUST include the actual URL that was provided in the news data above. Do not use generic phrases like "you can check it out here" without the URL.
6. Ends with an encouraging closing message
7. Do NOT include "[Your Name]" or any placeholder text - just end naturally

Make it conversational and informative. Don't use JSON formatting - just write the newsletter content directly.

The newsletter should be about 300-500 words and cover the most relevant stories for someone interested in {', '.join(topics)}.

Remember: Always include the actual URLs when referencing "read more" or similar phrases.
"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(None, lambda: self.llm.invoke(prompt))
            response_str = str(response)
            
            print(f"🔍 Raw LLM response: {response_str[:200]}...")
            
            # Try to parse the response
            try:
                # Clean the raw LLM response
                content = self._clean_llm_response(response_str)

                # Remove any placeholder text like "[Your Name]"
                content = re.sub(r'\[Your Name\]', '', content, flags=re.IGNORECASE)
                content = re.sub(r'\[.*?Name.*?\]', '', content, flags=re.IGNORECASE)
                content = re.sub(r'\[.*?\]', '', content)  # Remove any remaining brackets
                
                # Clean up extra whitespace
                content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Remove excessive line breaks
                content = content.strip()

                # Generate a subject based on topics
                subject = f"Your Daily {', '.join(topics).title()} News Summary"
                
                print(f"✅ Successfully generated newsletter content")
                print(f"📝 Content preview: {content[:100]}...")
                
            except Exception as e:
                print(f"❌ Content processing failed: {e}")
                print(f"🔍 Using fallback newsletter")
                return self._generate_fallback_newsletter(email, topics, news_data, sources_used, date_fetched)
            
            return {
                "subject": subject,
                "content": content,
                "html_content": self._convert_to_html(content),
                "generation_method": "llm_ai",
                "sources_used": sources_used or [],
                "date_fetched": date_fetched or datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            print(f"❌ Error in LLM newsletter generation: {str(e)}")
            return self._generate_fallback_newsletter(email, topics, news_data, sources_used, date_fetched)
    
    def _clean_llm_response(self, response_str: str) -> str:
        """Clean the LLM response to extract proper content"""
        # Remove any metadata or wrapper text
        if "content='" in response_str:
            start = response_str.find("content='") + 9
            end = response_str.find("'", start)
            if end > start:
                response_str = response_str[start:end]
        elif 'content="' in response_str:
            start = response_str.find('content="') + 9
            end = response_str.find('"', start)
            if end > start:
                response_str = response_str[start:end]
        
        # Remove any leading/trailing whitespace and quotes
        response_str = response_str.strip().strip('"\'')
        
        # Fix common formatting issues with robust error handling
        try:
            response_str = re.sub(r'\\n', '\n', response_str)
            response_str = re.sub(r'\\"', '"', response_str)
            response_str = re.sub(r'\\t', '\t', response_str)
            response_str = re.sub(r'\\\\', '\\', response_str)
            response_str = re.sub(r"\\'", "'", response_str)  # Fix escaped single quotes
            # Remove any markdown code blocks
            response_str = re.sub(r'```json\s*', '', response_str)
            response_str = re.sub(r'```\s*$', '', response_str)
            # Remove any remaining response metadata
            response_str = re.sub(r'response_metadata=.*$', '', response_str, flags=re.DOTALL)
            response_str = re.sub(r'id=\'.*$', '', response_str, flags=re.DOTALL)
        except re.error as e:
            logging.error(f"Regex error in _clean_llm_response: {e}")
            return response_str.strip()
        
        return response_str.strip()
    
    def _extract_json_content(self, response_str: str) -> tuple:
        """Extract subject and content from JSON response, handling nested JSON"""
        try:
            # First, try to parse the outer JSON
            result = json.loads(response_str)
            subject = result.get("subject", "Your Daily News Summary")
            content = result.get("content", "")
            
            # Check if content is itself a JSON string
            if isinstance(content, str) and content.strip().startswith("{"):
                try:
                    inner_result = json.loads(content)
                    # Use inner subject if available, otherwise keep outer
                    subject = inner_result.get("subject", subject)
                    content = inner_result.get("content", content)
                except json.JSONDecodeError:
                    # If inner JSON fails, keep the content as is
                    pass
            
            return subject, content
            
        except json.JSONDecodeError:
            # Try to extract JSON using regex
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_str, re.DOTALL)
            
            if json_match:
                try:
                    extracted_json = json_match.group(0)
                    result = json.loads(extracted_json)
                    subject = result.get("subject", "Your Daily News Summary")
                    content = result.get("content", "")
                    
                    # Check for nested JSON in content
                    if isinstance(content, str) and content.strip().startswith("{"):
                        try:
                            inner_result = json.loads(content)
                            subject = inner_result.get("subject", subject)
                            content = inner_result.get("content", content)
                        except json.JSONDecodeError:
                            pass
                    
                    return subject, content
                    
                except json.JSONDecodeError:
                    pass
            
            # If all JSON parsing fails, return the raw response
            return "Your Daily News Summary", response_str
    
    def _parse_crew_result(self, result) -> Dict[str, Any]:
        """Parse the crew result to extract newsletter components"""
        try:
            # The result should contain the final newsletter content
            content = str(result)
            
            # Clean the content - remove any CSS or HTML artifacts
            content = self._clean_content(content)
            
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
                    # Remove quotes if present
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
            # Return a safe fallback
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
    
    async def get_available_mcp_tools(self) -> List[Dict[str, str]]:
        """Get list of available MCP tools"""
        return []
    
    async def test_mcp_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Test a specific MCP tool"""
        return {
            "tool_name": tool_name,
            "success": False,
            "error": f"MCP tools are not available for this operation"
        } 