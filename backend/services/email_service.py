import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from jinja2 import Template
import aiofiles

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("EMAIL_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.from_email = self.email_user
        
        # Email templates
        self.html_template = self._load_html_template()
        self.text_template = self._load_text_template()
    
    def _load_html_template(self) -> Template:
        """Load HTML email template"""
        template_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }
                .container {
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid #3498db;
                }
                .header h1 {
                    color: #2c3e50;
                    margin: 0;
                    font-size: 28px;
                }
                .header p {
                    color: #7f8c8d;
                    margin: 10px 0 0 0;
                    font-size: 16px;
                }
                .greeting {
                    font-size: 18px;
                    color: #2c3e50;
                    margin-bottom: 25px;
                }
                .news-section {
                    margin-bottom: 30px;
                }
                .news-section h2 {
                    color: #34495e;
                    border-left: 4px solid #3498db;
                    padding-left: 15px;
                    margin-bottom: 20px;
                }
                .news-item {
                    background: #f8f9fa;
                    padding: 20px;
                    margin: 15px 0;
                    border-radius: 8px;
                    border-left: 4px solid #3498db;
                }
                .news-title {
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                    font-size: 16px;
                }
                .news-summary {
                    color: #555;
                    margin-bottom: 10px;
                    line-height: 1.5;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                    white-space: pre-wrap;
                }
                .news-source {
                    color: #7f8c8d;
                    font-size: 12px;
                    font-style: italic;
                }
                .news-link {
                    color: #3498db;
                    text-decoration: none;
                    font-weight: bold;
                }
                .news-link:hover {
                    text-decoration: underline;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 14px;
                }
                .footer p {
                    margin: 5px 0;
                }
                .unsubscribe {
                    color: #e74c3c;
                    text-decoration: none;
                }
                .unsubscribe:hover {
                    text-decoration: underline;
                }
                .stats {
                    background: #ecf0f1;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                    text-align: center;
                }
                .stats p {
                    margin: 5px 0;
                    color: #2c3e50;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📰 Your Daily News Summary</h1>
                    <p>AI-powered news curation for {{ topics|join(', ') }}</p>
                </div>
                
                <div class="greeting">
                    Good morning! 🌅
                </div>
                
                <div class="stats">
                    <p><strong>📊 Today's Summary</strong></p>
                    <p>Topics: {{ topics|join(', ') }}</p>
                    <p>News items: {{ news_count }}</p>
                    <p>Generated: {{ generated_at }}</p>
                    <p>News fetched on: {{ date_fetched }}</p>
                    <p>Sources used: {{ sources_used|join(', ') }}</p>
                </div>
                
                <div class="news-section">
                    <h2>📰 Top Stories</h2>
                    {% for item in news_items %}
                    <div class="news-item">
                        <div class="news-title">{{ item.title }}</div>
                        <div class="news-summary">{{ item.summary }}</div>
                        <div class="news-source">Source: {{ item.source }}</div>
                        {% if item.url %}
                        <a href="{{ item.url }}" class="news-link" target="_blank">Read more →</a>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                
                <div class="footer">
                    <p>🤖 Generated by Newsletter Agent MCP</p>
                    <p>Powered by AI and Multi-Agent Systems</p>
                    <p>This newsletter was personalized for your interests</p>
                    <p><a href="#" class="unsubscribe">Unsubscribe</a> | <a href="#" class="unsubscribe">Update Preferences</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        return Template(template_content)
    
    def _load_text_template(self) -> Template:
        """Load plain text email template"""
        template_content = """
Your Daily News Summary
=======================

Good morning!

Topics: {{ topics|join(', ') }}
News items: {{ news_count }}
Generated: {{ generated_at }}
News fetched on: {{ date_fetched }}
Sources used: {{ sources_used|join(', ') }}

TOP STORIES:
{% for item in news_items %}
{{ loop.index }}. {{ item.title }}
   {{ item.summary }}
   Source: {{ item.source }}
   {% if item.url %}Read more: {{ item.url }}{% endif %}

{% endfor %}

---
Generated by Newsletter Agent MCP
Powered by AI and Multi-Agent Systems
        """
        return Template(template_content)
    
    async def send_newsletter(self, to_email: str, newsletter_data: Dict[str, Any]) -> bool:
        """Send newsletter email to user"""
        try:
            # Prepare email content
            subject_val = newsletter_data.get("subject")
            if not subject_val:
                subject_val = "Your Daily News Summary"
            subject_val = str(subject_val)
            
            # Extract news items from the content
            news_items = self._extract_news_items(newsletter_data.get("content", ""))
            
            # Prepare template variables
            generated_at_val = newsletter_data.get("generated_at")
            if not generated_at_val:
                generated_at_val = datetime.now().isoformat()
            generated_at_val = str(generated_at_val)

            date_fetched_val = newsletter_data.get("date_fetched")
            if not date_fetched_val:
                date_fetched_val = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_fetched_val = str(date_fetched_val)

            template_vars = {
                "subject": subject_val,
                "topics": newsletter_data.get("topics", []),
                "news_count": newsletter_data.get("news_count", 0),
                "generated_at": generated_at_val,
                "date_fetched": date_fetched_val,
                "sources_used": newsletter_data.get("sources_used", []),
                "news_items": news_items
            }
            
            # Generate HTML and text content
            html_content = self.html_template.render(**template_vars)
            text_content = self.text_template.render(**template_vars)
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject_val
            message["From"] = self.from_email or self.email_user or "newsletter@example.com"
            message["To"] = str(to_email)
            
            # Add text and HTML parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Send email
            success = await self._send_email(message)
            
            if success:
                logging.info(f"Newsletter sent successfully to {to_email}")
            else:
                logging.error(f"Failed to send newsletter to {to_email}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error sending newsletter to {to_email}: {str(e)}")
            return False
    
    async def _send_email(self, message: MIMEMultipart) -> bool:
        """Send email using SMTP with robust SSL handling"""
        try:
            if not self.email_user or not self.email_password:
                logging.error("Email credentials not configured")
                return False
            
            # Create SSL context with certificate verification disabled for development
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # For Gmail, we need to handle SSL properly
            if self.smtp_host == "smtp.gmail.com":
                logging.info("Using Gmail SMTP configuration")
                
                # Check if using app password (Gmail app passwords are 16 characters)
                if len(self.email_password) != 16:
                    logging.error("Gmail requires an App Password (16 characters). Please:")
                    logging.error("1. Enable 2-Factor Authentication on your Google account")
                    logging.error("2. Generate an App Password at: https://myaccount.google.com/apppasswords")
                    logging.error("3. Use the App Password instead of your regular password")
                    return False
                
                if self.smtp_port == 587:
                    # Use STARTTLS
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                    server.starttls(context=context)
                elif self.smtp_port == 465:
                    # Use SSL
                    server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context, timeout=30)
                else:
                    logging.error(f"Unsupported port {self.smtp_port} for Gmail. Use 587 (STARTTLS) or 465 (SSL)")
                    return False
            else:
                # For other providers, try STARTTLS
                server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                server.starttls(context=context)
            
            # Login and send
            logging.info(f"Attempting to login to {self.smtp_host} with user: {self.email_user or 'Unknown'}")
            server.login(self.email_user, self.email_password)
            server.send_message(message)
            server.quit()
            
            to_email = message.get('To', 'Unknown')
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logging.error(f"SMTP Authentication failed: {str(e)}")
            if self.smtp_host == "smtp.gmail.com":
                logging.error("For Gmail, please ensure you're using an App Password:")
                logging.error("1. Enable 2-Factor Authentication: https://myaccount.google.com/security")
                logging.error("2. Generate App Password: https://myaccount.google.com/apppasswords")
                logging.error("3. Use the 16-character App Password in EMAIL_PASSWORD")
            return False
        except smtplib.SMTPException as e:
            logging.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Email sending error: {str(e)}")
            return False
    
    def _extract_news_items(self, content: str) -> list:
        """Extract news items from newsletter content"""
        news_items = []
        
        try:
            # If the content is a single newsletter article, create one item
            if len(content) > 100 and not any(line.strip().startswith(str(i) + '.') for i in range(1, 10) for line in content.split('\n')):
                # This looks like a single newsletter article, not a list of news items
                news_items = [{
                    "title": "Daily News Summary",
                    "summary": content,  # Use the full content, don't truncate
                    "source": "Newsletter Agent",
                    "url": ""
                }]
            else:
                # Try to parse numbered news items
                lines = content.split('\n')
                current_item = {}
                
                for line in lines:
                    line = line.strip()
                    
                    # Look for numbered items (1., 2., etc.)
                    if line and line[0].isdigit() and '. ' in line:
                        if current_item:
                            news_items.append(current_item)
                        
                        # Start new item
                        title = line.split('. ', 1)[1] if '. ' in line else line
                        current_item = {
                            "title": title,
                            "summary": "",
                            "source": "News Source",
                            "url": ""
                        }
                    
                    # Look for source information
                    elif line.lower().startswith("source:"):
                        if current_item:
                            current_item["source"] = line.split(":", 1)[1].strip()
                    
                    # Look for URLs
                    elif line.startswith("http"):
                        if current_item:
                            current_item["url"] = line.strip()
                    
                    # Add to summary if not empty and not a special line
                    elif line and not line.startswith("Source:") and not line.startswith("http"):
                        if current_item and "summary" in current_item:
                            current_item["summary"] += " " + line
                        elif current_item:
                            current_item["summary"] = line
                
                # Add the last item
                if current_item:
                    news_items.append(current_item)
                
                # If no items found, create a simple one
                if not news_items:
                    news_items = [{
                        "title": "Daily News Summary",
                        "summary": content,  # Use the full content, don't truncate
                        "source": "Newsletter Agent",
                        "url": ""
                    }]
            
        except Exception as e:
            logging.error(f"Error extracting news items: {str(e)}")
            # Fallback - use the full content
            news_items = [{
                "title": "Daily News Summary",
                "summary": content,  # Use the full content, don't truncate
                "source": "Newsletter Agent",
                "url": ""
            }]
        
        return news_items  # Remove the limit to 10 items
    
    async def send_test_email(self, to_email: str) -> bool:
        """Send a test email"""
        try:
            test_data = {
                "subject": "Test Newsletter - Newsletter Agent MCP",
                "content": """
1. Test News Item 1
   This is a test news summary for demonstration purposes.
   Source: Test Source

2. Test News Item 2
   Another test news item to verify email functionality.
   Source: Test Source 2
                """,
                "topics": ["technology", "business"],
                "news_count": 2,
                "generated_at": datetime.now().isoformat()
            }
            
            return await self.send_newsletter(to_email, test_data)
            
        except Exception as e:
            logging.error(f"Error sending test email: {str(e)}")
            return False
    
    async def send_welcome_email(self, to_email: str, topics: list) -> bool:
        """Send welcome email to new subscribers"""
        try:
            welcome_data = {
                "subject": "Welcome to Newsletter Agent MCP! 🤖",
                "content": f"""
1. Welcome to Your AI Newsletter
   Thank you for subscribing to our AI-powered newsletter service. You'll receive daily summaries on: {', '.join(topics)}
   Source: Newsletter Agent MCP

2. What to Expect
   - Daily news summaries at 9 AM
   - Personalized content based on your interests
   - AI-curated stories from multiple sources
   - Easy-to-read format
   Source: Newsletter Agent MCP
                """,
                "topics": topics,
                "news_count": 2,
                "generated_at": datetime.now().isoformat()
            }
            
            return await self.send_newsletter(to_email, welcome_data)
            
        except Exception as e:
            logging.error(f"Error sending welcome email: {str(e)}")
            return False 