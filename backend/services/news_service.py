import os
import asyncio
import aiohttp
import yfinance as yf
import feedparser
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
import json
import ssl
import time
import re
import requests
from bs4 import BeautifulSoup

class NewsService:
    def __init__(self):
        # Initialize optional NewsAPI client (if key is available)
        news_api_key = os.getenv('NEWS_API_KEY')
        if news_api_key and news_api_key != 'your-api-key-here':
            try:
                from newsapi import NewsApiClient
                self.newsapi = NewsApiClient(api_key=news_api_key)
                self.newsapi_available = True
                logging.info("✅ NewsAPI client initialized successfully")
            except ImportError:
                self.newsapi = None
                self.newsapi_available = False
                logging.warning("⚠️ NewsAPI package not installed")
        else:
            self.newsapi = None
            self.newsapi_available = False
            logging.info("ℹ️ NewsAPI key not provided, using alternative news sources")
        
        # Define news sources and their configurations
        self.news_sources = {
            "yahoo_finance": {
                "enabled": True,
                "topics": ["stocks", "finance", "business", "economy", "market"]
            },
            "rss_feeds": {
                "enabled": True,
                "feeds": {
                    "tech": "https://feeds.feedburner.com/TechCrunch",
                    "business": "https://feeds.feedburner.com/businessinsider",
                    "science": "https://rss.sciencedaily.com/all.xml",
                    "health": "https://www.medicalnewstoday.com/rss.xml",
                    "sports": "https://www.espn.com/espn/rss/news",
                    "entertainment": "https://feeds.feedburner.com/entertainment-weekly",
                    "politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
                    "world": "https://feeds.bbci.co.uk/news/world/rss.xml",
                    "general": "https://feeds.bbci.co.uk/news/rss.xml",
                    "reuters": "https://feeds.reuters.com/reuters/topNews",
                    "cnn": "http://rss.cnn.com/rss/edition.rss"
                }
            },
            "reddit_news": {
                "enabled": True,
                "subreddits": {
                    "news": "https://www.reddit.com/r/news/.json",
                    "technology": "https://www.reddit.com/r/technology/.json",
                    "sports": "https://www.reddit.com/r/sports/.json",
                    "business": "https://www.reddit.com/r/business/.json",
                    "science": "https://www.reddit.com/r/science/.json"
                }
            },
            "hacker_news": {
                "enabled": True,
                "url": "https://hacker-news.firebaseio.com/v0/topstories.json"
            }
        }
        
        # Topic to keyword mapping
        self.topic_keywords = {
            "technology": ["tech", "software", "AI", "artificial intelligence", "startup", "innovation", "digital", "computer", "internet", "app", "mobile"],
            "business": ["business", "company", "corporate", "market", "economy", "startup", "entrepreneur", "investment", "finance", "trading"],
            "finance": ["finance", "stocks", "investment", "trading", "market", "economy", "banking", "money", "financial", "wall street"],
            "politics": ["politics", "government", "policy", "election", "congress", "senate", "president", "democrat", "republican", "vote"],
            "science": ["science", "research", "study", "discovery", "scientific", "experiment", "laboratory", "university", "academic"],
            "health": ["health", "medical", "medicine", "healthcare", "hospital", "doctor", "patient", "treatment", "disease", "wellness"],
            "sports": ["sports", "football", "basketball", "baseball", "soccer", "tennis", "golf", "olympics", "athlete", "game", "team"],
            "entertainment": ["entertainment", "movie", "music", "celebrity", "film", "actor", "singer", "hollywood", "tv", "show", "concert"]
        }
    
    async def get_news_for_topics(self, topics: List[str], preferred_source: str = "Auto") -> Dict[str, Any]:
        """Get news from multiple sources for given topics. Returns a dict with date, sources, and news."""
        all_news = []
        finance_topics = {"finance", "stocks", "investment", "trading", "market", "business", "economy"}
        sources_used = []
        current_timestamp = datetime.now()
        date_fetched = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate 24 hours ago for filtering
        twenty_four_hours_ago = current_timestamp - timedelta(hours=24)
        
        logging.info(f"📅 Fetching news from {twenty_four_hours_ago.strftime('%Y-%m-%d %H:%M:%S')} to {date_fetched}")
        
        # Determine which news source to use based on user preference
        if preferred_source == "Auto":
            # For Auto mode, try real news sources first, then fallback to LLM
            use_real_sources = True
            use_llm_fallback = True
        elif preferred_source == "Yahoo Finance":
            # Only use Yahoo Finance
            yahoo_news = await self._get_yahoo_finance_news(topics, twenty_four_hours_ago)
            all_news.extend(yahoo_news)
            sources_used.append("Yahoo Finance")
            return {
                "date_fetched": date_fetched,
                "sources_used": sources_used,
                "news": self._deduplicate_news(all_news)[:20]
            }
        elif preferred_source == "Google News":
            # Only use Google News
            google_news = await self._get_google_news(topics, twenty_four_hours_ago)
            all_news.extend(google_news)
            sources_used.append("Google News")
            return {
                "date_fetched": date_fetched,
                "sources_used": sources_used,
                "news": self._deduplicate_news(all_news)[:20]
            }
        elif preferred_source == "LLM (AI Generated)":
            # Only use LLM
            use_real_sources = False
            use_llm_fallback = True
        elif preferred_source == "RSS Feeds":
            # Only use RSS feeds
            rss_news = await self._get_rss_news(topics, twenty_four_hours_ago)
            all_news.extend(rss_news)
            sources_used.append("RSS Feeds")
            return {
                "date_fetched": date_fetched,
                "sources_used": sources_used,
                "news": self._deduplicate_news(all_news)[:20]
            }
        else:
            # Default to Auto behavior
            use_real_sources = True
            use_llm_fallback = True

        # Step 1: Try real news sources first (if enabled and available)
        if use_real_sources:
            # Try Yahoo Finance for finance-related topics
            if any(t in finance_topics for t in topics):
                yahoo_news = await self._get_yahoo_finance_news(topics, twenty_four_hours_ago)
                if yahoo_news:
                    all_news.extend(yahoo_news)
                    sources_used.append("Yahoo Finance")
            
            # Try Reddit news for general topics
            reddit_news = await self._get_reddit_news(topics, twenty_four_hours_ago)
            if reddit_news:
                all_news.extend(reddit_news)
                sources_used.append("Reddit")
            
            # Try Hacker News for technology topics
            if any(t in ["technology", "business", "science"] for t in topics):
                hn_news = await self._get_hacker_news(topics, twenty_four_hours_ago)
                if hn_news:
                    all_news.extend(hn_news)
                    sources_used.append("Hacker News")
            
            # Try RSS feeds for various topics (always available as fallback)
            rss_news = await self._get_rss_news(topics, twenty_four_hours_ago)
            if rss_news:
                all_news.extend(rss_news)
                sources_used.append("RSS Feeds")
            
            # Try NewsAPI if available (optional)
            if self.newsapi_available:
                google_news = await self._get_google_news(topics, twenty_four_hours_ago)
                if google_news:
                    all_news.extend(google_news)
                    sources_used.append("Google News (via NewsAPI)")

        # Step 2: If no real news found, provide helpful message instead of fake news
        if len(all_news) == 0:
            logging.warning("❌ No real news found from any source in the last 24 hours")
            sources_used.append("No Recent News Available")
            
            # Provide a helpful message about the issue
            all_news.append({
                "title": f"No Recent News Available (Last 24 Hours)",
                "summary": f"We couldn't find any recent news for {', '.join(topics)} in the last 24 hours. This might be due to network issues, service maintenance, or limited recent activity on these topics. Please try again later or consider expanding your topic selection.",
                "url": "",
                "source": "System Message",
                "published_at": current_timestamp,
                "relevance_score": 0.5
            })
            
            # Add a helpful tip about API keys
            if not self.newsapi_available:
                all_news.append({
                    "title": "Setup NewsAPI for Better News Coverage",
                    "summary": "To get real-time news from Google News, please add your NewsAPI key to the .env file. Get a free key from https://newsapi.org/",
                    "url": "https://newsapi.org/",
                    "source": "Setup Guide",
                    "published_at": current_timestamp,
                    "relevance_score": 0.3
                })

        # Remove duplicates and sort by relevance
        unique_news = self._deduplicate_news(all_news)
        sorted_news = self._sort_news_by_relevance(unique_news, topics)
        return {
            "date_fetched": date_fetched,
            "sources_used": sources_used,
            "news": sorted_news[:20]
        }
    
    async def _get_yahoo_finance_news(self, topics: List[str], start_time: datetime) -> List[Dict[str, Any]]:
        """Get news from Yahoo Finance with improved error handling"""
        news_items = []
        
        try:
            # Use a smaller set of reliable tickers
            tickers = ["AAPL", "GOOGL", "MSFT"]
            
            logging.info(f"🔍 Fetching Yahoo Finance news (since {start_time.strftime('%Y-%m-%d %H:%M:%S')})")
            
            for ticker in tickers:
                try:
                    # Add delay to avoid rate limiting
                    await asyncio.sleep(0.5)
                    
                    stock = yf.Ticker(ticker)
                    
                    # Try to get news with timeout
                    try:
                        news = stock.news
                    except Exception as e:
                        logging.warning(f"Failed to fetch news for {ticker}: {str(e)}")
                        continue
                    
                    # Validate news data
                    if not news or not isinstance(news, list):
                        logging.warning(f"No valid news data for {ticker}")
                        continue
                    
                    # Process news items
                    for item in news[:2]:  # Limit to 2 items per ticker
                        try:
                            title = item.get("title", "")
                            if not title:
                                continue
                            
                            # Get publication time and filter by start_time
                            publish_time = item.get("providerPublishTime", time.time())
                            publish_date = datetime.fromtimestamp(publish_time)
                            
                            # Skip articles older than 24 hours
                            if publish_date < start_time:
                                continue
                                
                            if self._is_relevant_to_topics(title, topics):
                                news_items.append({
                                    "title": title,
                                    "summary": item.get("summary", "")[:200] + "..." if len(item.get("summary", "")) > 200 else item.get("summary", ""),
                                    "url": item.get("link", ""),
                                    "source": f"Yahoo Finance - {ticker}",
                                    "published_at": publish_date,
                                    "relevance_score": self._calculate_relevance_score(title, topics)
                                })
                        except Exception as e:
                            logging.warning(f"Error processing news item for {ticker}: {str(e)}")
                            continue
                            
                except Exception as e:
                    logging.error(f"Error fetching news for {ticker}: {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"Error in Yahoo Finance news fetching: {str(e)}")
        
        # Always provide fallback content if no news found
        if not news_items:
            logging.info("No Yahoo Finance news found, using fallback content")
            news_items = [
                {
                    "title": "Technology Market Update",
                    "summary": "Stay tuned for the latest technology news and market updates. Our AI is working to bring you the most relevant stories.",
                    "url": "",
                    "source": "System - Fallback",
                    "published_at": datetime.now(),
                    "relevance_score": 0.8
                },
                {
                    "title": "AI and Innovation News",
                    "summary": "Discover the latest developments in artificial intelligence, machine learning, and technological innovation.",
                    "url": "",
                    "source": "System - Fallback",
                    "published_at": datetime.now(),
                    "relevance_score": 0.9
                }
            ]
        
        return news_items
    
    async def _get_google_news(self, topics: List[str], start_time: datetime) -> List[Dict[str, Any]]:
        """Get real news from Google News using NewsAPI and summarize with LLM"""
        news_items = []
        
        # Check if NewsAPI is available
        if not self.newsapi_available or not self.newsapi:
            logging.warning("❌ NewsAPI not available, skipping Google News")
            return news_items
        
        try:
            # Create search queries for each topic
            search_queries = []
            for topic in topics:
                if topic in self.topic_keywords:
                    # Use the most relevant keyword for each topic
                    search_queries.append(self.topic_keywords[topic][0])
                else:
                    search_queries.append(topic)
            
            logging.info(f"🔍 Fetching Google News for topics: {topics}")
            
            # Fetch news for each topic
            for query in search_queries[:3]:  # Limit to 3 topics to avoid rate limits
                try:
                    # Get top headlines from Google News
                    articles = self.newsapi.get_everything(
                        q=query,
                        language='en',
                        page_size=5,  # Get 5 articles per topic
                        from_param=start_time.strftime('%Y-%m-%d'),
                        to=datetime.now().strftime('%Y-%m-%d')
                    )
                    
                    if articles.get('status') == 'ok' and articles.get('articles'):
                        logging.info(f"✅ Found {len(articles['articles'])} articles for '{query}'")
                        
                        for article in articles['articles']:
                            # Only process articles with meaningful content
                            if article.get('title') and len(article['title']) > 10:
                                # Use LLM to summarize the article content
                                summary = await self._summarize_article_with_llm(
                                    article.get('title', ''),
                                    article.get('description', ''),
                                    article.get('content', '')
                                )
                                
                                news_items.append({
                                    "title": article.get('title', ''),
                                    "summary": summary,
                                    "url": article.get('url', ''),
                                    "source": article.get('source', {}).get('name', 'Google News'),
                                    "published_at": datetime.fromisoformat(article.get('publishedAt', datetime.now().isoformat()).replace('Z', '+00:00')),
                                    "relevance_score": self._calculate_relevance_score(article.get('title', ''), topics),
                                    "fetched_at": datetime.now().isoformat(),
                                    "news_source": "Google News (via NewsAPI)"
                                })
                    
                    # Add delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logging.warning(f"❌ Error fetching news for '{query}': {str(e)}")
                    continue
                    
        except Exception as e:
            logging.error(f"❌ Error in Google News fetching: {str(e)}")
        
        # If no real news found, try alternative approach with RSS feeds
        if not news_items:
            logging.info("⚠️ No Google News found via NewsAPI, trying RSS feeds as alternative")
            rss_news = await self._get_rss_news(topics, start_time)
            if rss_news:
                news_items.extend(rss_news)
        
        return news_items
    
    async def _summarize_article_with_llm(self, title: str, description: str, content: str) -> str:
        """Summarize article content using LLM"""
        try:
            from backend.mcp.tools import llm
            
            # Combine available content
            full_content = f"Title: {title}\n"
            if description:
                full_content += f"Description: {description}\n"
            if content:
                # Clean content (remove HTML tags, etc.)
                clean_content = re.sub(r'<[^>]+>', '', content)
                full_content += f"Content: {clean_content[:500]}..."  # Limit content length
            
            prompt = f"""
            Please provide a concise 2-3 sentence summary of this news article:
            
            {full_content}
            
            Focus on the key facts, developments, and implications. Make it engaging and informative.
            """
            
            response = llm.invoke(prompt)
            summary = str(response).strip()
            
            # Clean up the response
            if summary.startswith('"') and summary.endswith('"'):
                summary = summary[1:-1]
            
            return summary if summary else description or "No summary available"
            
        except Exception as e:
            logging.warning(f"❌ Error summarizing article: {str(e)}")
            # Fallback to description or title
            return description or title or "No summary available"
    
    async def _get_rss_news(self, topics: List[str], start_time: datetime) -> List[Dict[str, Any]]:
        """Get news from RSS feeds"""
        news_items = []
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                
                for feed_name, feed_url in self.news_sources["rss_feeds"]["feeds"].items():
                    if self._is_feed_relevant_to_topics(feed_name, topics):
                        tasks.append(self._fetch_rss_feed(session, feed_url, feed_name, start_time))
                
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for result in results:
                        if isinstance(result, list):
                            news_items.extend(result)
                        elif isinstance(result, Exception):
                            logging.error(f"Error fetching RSS feed: {str(result)}")
                            
        except Exception as e:
            logging.error(f"Error in RSS news fetching: {str(e)}")
        
        return news_items
    
    async def _fetch_rss_feed(self, session: aiohttp.ClientSession, feed_url: str, feed_name: str, start_time: datetime) -> List[Dict[str, Any]]:
        """Fetch individual RSS feed"""
        news_items = []
        
        try:
            # Create SSL context that doesn't verify certificates for RSS feeds
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as ssl_session:
                async with ssl_session.get(feed_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        logging.info(f"📰 Processing RSS feed: {feed_name} (since {start_time.strftime('%Y-%m-%d %H:%M:%S')})")
                        
                        for entry in feed.entries[:10]:  # Get top 10 entries for better filtering
                            try:
                                # Try to parse the publication date from the entry
                                published_date = None
                                
                                # Check different date fields that RSS feeds might use
                                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                    # Handle the parsed date tuple properly
                                    parsed = entry.published_parsed
                                    if isinstance(parsed, tuple) and len(parsed) >= 6:
                                        published_date = datetime(*parsed[:6])
                                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                                    # Handle the parsed date tuple properly
                                    parsed = entry.updated_parsed
                                    if isinstance(parsed, tuple) and len(parsed) >= 6:
                                        published_date = datetime(*parsed[:6])
                                elif hasattr(entry, 'published'):
                                    # Try to parse the published string
                                    try:
                                        if isinstance(entry.published, str):
                                            published_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)
                                        else:
                                            published_date = datetime.now()
                                    except:
                                        # If parsing fails, use current date as fallback
                                        published_date = datetime.now()
                                else:
                                    # If no date available, use current date as fallback
                                    published_date = datetime.now()
                                
                                # Skip articles older than 24 hours
                                if published_date and published_date < start_time:
                                    continue
                                
                                news_items.append({
                                    "title": str(entry.get("title", "")),
                                    "summary": str(entry.get("summary", "")),
                                    "url": str(entry.get("link", "")),
                                    "source": f"RSS - {feed_name}",
                                    "published_at": published_date,
                                    "relevance_score": 0.5  # Default relevance for RSS
                                })
                                
                                # Limit to 5 items per feed
                                if len(news_items) >= 5:
                                    break
                                    
                            except Exception as e:
                                logging.warning(f"Error processing RSS entry from {feed_name}: {str(e)}")
                                continue
                    else:
                        logging.warning(f"RSS feed {feed_url} returned status {response.status}")
                        
        except Exception as e:
            logging.error(f"Error fetching RSS feed {feed_url}: {str(e)}")
        
        return news_items
    
    def _is_relevant_to_topics(self, title: str, topics: List[str]) -> bool:
        """Check if a news title is relevant to given topics"""
        title_lower = title.lower()
        
        for topic in topics:
            if topic.lower() in title_lower:
                return True
            
            # Check topic keywords
            if topic in self.topic_keywords:
                for keyword in self.topic_keywords[topic]:
                    if keyword.lower() in title_lower:
                        return True
        
        return False
    
    def _is_feed_relevant_to_topics(self, feed_name: str, topics: List[str]) -> bool:
        """Check if an RSS feed is relevant to given topics"""
        feed_lower = feed_name.lower()
        
        for topic in topics:
            if topic.lower() in feed_lower:
                return True
        
        return False
    
    def _calculate_relevance_score(self, title: str, topics: List[str]) -> float:
        """Calculate relevance score for a news item"""
        score = 0.0
        title_lower = title.lower()
        
        for topic in topics:
            if topic.lower() in title_lower:
                score += 1.0
            
            # Check topic keywords
            if topic in self.topic_keywords:
                for keyword in self.topic_keywords[topic]:
                    if keyword.lower() in title_lower:
                        score += 0.5
        
        return min(score, 5.0)  # Cap at 5.0
    
    def _deduplicate_news(self, news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news items based on title similarity"""
        seen_titles = set()
        unique_news = []
        
        for item in news_items:
            title = item.get("title", "").lower()
            
            # Simple deduplication based on title
            if title not in seen_titles:
                seen_titles.add(title)
                unique_news.append(item)
        
        return unique_news
    
    def _sort_news_by_relevance(self, news_items: List[Dict[str, Any]], topics: List[str]) -> List[Dict[str, Any]]:
        """Sort news items by relevance score and recency"""
        for item in news_items:
            if "relevance_score" not in item:
                item["relevance_score"] = self._calculate_relevance_score(item.get("title", ""), topics)
        
        # Sort by relevance score (descending) and then by published date (descending)
        sorted_news = sorted(
            news_items,
            key=lambda x: (x.get("relevance_score", 0), x.get("published_at", datetime.min)),
            reverse=True
        )
        
        return sorted_news
    
    async def get_trending_topics(self) -> List[str]:
        """Get trending topics based on current news"""
        try:
            # Get recent news to identify trending topics
            result = await self.get_news_for_topics(["technology", "business", "politics", "science"])
            recent_news = result["news"]
            
            # Simple topic extraction from titles
            topic_counts = {}
            for item in recent_news:
                title = item.get("title", "").lower()
                
                for topic, keywords in self.topic_keywords.items():
                    for keyword in keywords:
                        if keyword.lower() in title:
                            topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Return top 5 trending topics
            trending = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            return [topic for topic, count in trending[:5]]
            
        except Exception as e:
            logging.error(f"Error getting trending topics: {str(e)}")
            return ["technology", "business", "finance", "politics", "science"]
    
    async def _get_reddit_news(self, topics: List[str], start_time: datetime) -> List[Dict[str, Any]]:
        """Get news from Reddit subreddits"""
        news_items = []
        
        try:
            # Headers to mimic a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            # Map topics to relevant subreddits
            topic_to_subreddit = {
                "technology": ["technology"],
                "business": ["business"],
                "sports": ["sports"],
                "science": ["science"],
                "politics": ["news"],
                "entertainment": ["news"],
                "health": ["news"],
                "finance": ["business"]
            }
            
            relevant_subreddits = set()
            for topic in topics:
                if topic in topic_to_subreddit:
                    relevant_subreddits.update(topic_to_subreddit[topic])
                else:
                    relevant_subreddits.add("news")  # Default to general news
            
            logging.info(f"🔍 Fetching Reddit news from subreddits: {list(relevant_subreddits)} (since {start_time.strftime('%Y-%m-%d %H:%M:%S')})")
            
            async with aiohttp.ClientSession(connector=connector) as session:
                for subreddit in list(relevant_subreddits)[:3]:  # Limit to 3 subreddits
                    try:
                        url = f"https://www.reddit.com/r/{subreddit}/.json"
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                posts = data.get('data', {}).get('children', [])
                                
                                for post in posts[:5]:  # Get top 5 posts
                                    post_data = post.get('data', {})
                                    title = post_data.get('title', '')
                                    score = post_data.get('score', 0)
                                    created_utc = post_data.get('created_utc', 0)
                                    
                                    # Convert Reddit timestamp to datetime
                                    post_date = datetime.fromtimestamp(created_utc)
                                    
                                    # Skip posts older than 24 hours
                                    if post_date < start_time:
                                        continue
                                    
                                    # Check if title is relevant to topics
                                    if self._is_relevant_to_topics(title, topics):
                                        news_items.append({
                                            "title": title,
                                            "summary": f"Reddit post with {score} upvotes from r/{subreddit}",
                                            "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
                                            "source": f"Reddit - r/{subreddit}",
                                            "published_at": post_date,
                                            "relevance_score": self._calculate_relevance_score(title, topics)
                                        })
                                        
                                        if len(news_items) >= 10:  # Limit total items
                                            break
                            else:
                                logging.warning(f"Reddit subreddit r/{subreddit} returned status {response.status}")
                                
                    except Exception as e:
                        logging.error(f"Error fetching Reddit subreddit r/{subreddit}: {str(e)}")
                        
        except Exception as e:
            logging.error(f"Error in Reddit news fetching: {str(e)}")
        
        return news_items
    
    async def _get_hacker_news(self, topics: List[str], start_time: datetime) -> List[Dict[str, Any]]:
        """Get news from Hacker News"""
        news_items = []
        
        try:
            logging.info(f"🔍 Fetching Hacker News (since {start_time.strftime('%Y-%m-%d %H:%M:%S')})")
            
            # Create SSL context that doesn't verify certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Get top stories
                async with session.get("https://hacker-news.firebaseio.com/v0/topstories.json") as response:
                    if response.status == 200:
                        story_ids = await response.json()
                        
                        # Get details for top 20 stories
                        for story_id in story_ids[:20]:
                            try:
                                async with session.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json") as story_response:
                                    if story_response.status == 200:
                                        story_data = await story_response.json()
                                        
                                        if story_data and story_data.get('type') == 'story':
                                            title = story_data.get('title', '')
                                            score = story_data.get('score', 0)
                                            created_time = story_data.get('time', 0)
                                            
                                            # Convert HN timestamp to datetime
                                            story_date = datetime.fromtimestamp(created_time)
                                            
                                            # Skip stories older than 24 hours
                                            if story_date < start_time:
                                                continue
                                            
                                            # Check if title is relevant to topics
                                            if self._is_relevant_to_topics(title, topics):
                                                news_items.append({
                                                    "title": title,
                                                    "summary": f"Hacker News story with {score} points",
                                                    "url": story_data.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                                                    "source": "Hacker News",
                                                    "published_at": story_date,
                                                    "relevance_score": self._calculate_relevance_score(title, topics)
                                                })
                                                
                                                if len(news_items) >= 10:  # Limit total items
                                                    break
                            except Exception as e:
                                logging.error(f"Error fetching HN story {story_id}: {str(e)}")
                                
        except Exception as e:
            logging.error(f"Error in Hacker News fetching: {str(e)}")
        
        return news_items 