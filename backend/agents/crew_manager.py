import os
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from typing import List, Dict, Any
import asyncio
import logging
from datetime import datetime

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
    
    async def generate_newsletter(self, email: str, topics: List[str], news_data: List[Dict]) -> Dict[str, Any]:
        """Generate a personalized newsletter using the multi-agent crew"""
        
        try:
            # For now, let's use a simplified approach to avoid CrewAI parsing issues
            # We'll generate a newsletter directly without using the crew
            newsletter_content = self._generate_simple_newsletter(email, topics, news_data)
            
            # Add metadata
            newsletter_content.update({
                "email": email,
                "topics": topics,
                "generated_at": datetime.utcnow().isoformat(),
                "news_count": len(news_data)
            })
            
            return newsletter_content
            
        except Exception as e:
            logging.error(f"Error in newsletter generation: {str(e)}")
            logging.error(f"Error type: {type(e)}")
            logging.error(f"Error details: {e}")
            
            # Fallback to simple newsletter generation
            return self._generate_fallback_newsletter(email, topics, news_data)
    
    def _generate_simple_newsletter(self, email: str, topics: List[str], news_data: List[Dict]) -> Dict[str, Any]:
        """Generate a simple newsletter without using CrewAI"""
        subject = f"Your Daily News Summary - {', '.join(topics)}"
        
        content = f"""
Good morning!

Here's your personalized news summary for today covering: {', '.join(topics)}

"""
        
        if news_data:
            content += "📰 Top Stories:\n\n"
            for i, news in enumerate(news_data[:8], 1):  # Limit to 8 news items
                title = news.get('title', 'No title')
                summary = news.get('summary', 'No summary available')
                source = news.get('source', 'Unknown')
                
                content += f"{i}. {title}\n"
                content += f"   {summary[:200]}...\n"
                content += f"   Source: {source}\n\n"
        else:
            content += "No news articles found for your topics today.\n\n"
        
        content += """
Stay informed and have a great day!

Best regards,
Your AI Newsletter Agent (Powered by MCP)
        """
        
        return {
            "subject": subject,
            "content": content.strip(),
            "html_content": self._convert_to_html(content.strip()),
            "generation_method": "simple_ai"
        }
    
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
        import re
        
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
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Daily Newsletter</title>
        </head>
        <body>
            {content}
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666;">
                <p>Generated by Newsletter Agent MCP - AI-powered news curation with MCP tools</p>
            </div>
        </body>
        </html>
        """
        
        formatted_content = content.replace('\n', '<br>')
        return html_template.format(content=formatted_content)
    
    def _generate_fallback_newsletter(self, email: str, topics: List[str], news_data: List[Dict]) -> Dict[str, Any]:
        """Generate a simple newsletter as fallback"""
        subject = f"Your Daily News Summary - {', '.join(topics)}"
        
        content = f"""
        Good morning!

        Here's your personalized news summary for today covering: {', '.join(topics)}

        """
        
        for i, news in enumerate(news_data[:10], 1):  # Limit to 10 news items
            content += f"""
        {i}. {news.get('title', 'No title')}
           {news.get('summary', 'No summary available')}
           Source: {news.get('source', 'Unknown')}
            
        """
        
        content += """
        Stay informed and have a great day!

        Best regards,
        Your AI Newsletter Agent (Powered by MCP)
        """
        
        return {
            "subject": subject,
            "content": content.strip(),
            "html_content": self._convert_to_html(content.strip()),
            "email": email,
            "topics": topics,
            "generated_at": datetime.utcnow().isoformat(),
            "news_count": len(news_data),
            "mcp_tools_used": ["fallback_mode"]
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