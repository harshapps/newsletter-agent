import os
import asyncio
import aiohttp
import yfinance as yf
from newsapi import NewsApiClient
import feedparser
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta
import json
import ssl
import time

class NewsService:
    def __init__(self):
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.news_api = NewsApiClient(api_key=self.news_api_key) if self.news_api_key else None
        
        # Define news sources and their configurations
        self.news_sources = {
            "yahoo_finance": {
                "enabled": True,
                "topics": ["stocks", "finance", "business", "economy", "market"]
            },
            "newsapi": {
                "enabled": bool(self.news_api_key),
                "topics": ["technology", "business", "politics", "science", "health"]
            },
            "rss_feeds": {
                "enabled": True,
                "feeds": {
                    "tech": "https://feeds.feedburner.com/TechCrunch",
                    "business": "https://feeds.feedburner.com/businessinsider",
                    "science": "https://rss.sciencedaily.com/all.xml",
                    "health": "https://www.medicalnewstoday.com/rss.xml"
                }
            }
        }
        
        # Topic to keyword mapping
        self.topic_keywords = {
            "technology": ["tech", "software", "AI", "artificial intelligence", "startup", "innovation"],
            "business": ["business", "company", "corporate", "market", "economy"],
            "finance": ["finance", "stocks", "investment", "trading", "market"],
            "politics": ["politics", "government", "policy", "election"],
            "science": ["science", "research", "study", "discovery"],
            "health": ["health", "medical", "medicine", "healthcare"],
            "sports": ["sports", "football", "basketball", "baseball", "soccer"],
            "entertainment": ["entertainment", "movie", "music", "celebrity"]
        }
    
    async def get_news_for_topics(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Get news from multiple sources for given topics"""
        all_news = []
        
        # Create tasks for each news source
        tasks = []
        
        for source_name, source_config in self.news_sources.items():
            if source_config.get("enabled", False):
                if source_name == "yahoo_finance":
                    tasks.append(self._get_yahoo_finance_news(topics))
                elif source_name == "newsapi":
                    tasks.append(self._get_newsapi_news(topics))
                elif source_name == "rss_feeds":
                    tasks.append(self._get_rss_news(topics))
        
        # Execute all tasks concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_news.extend(result)
                elif isinstance(result, Exception):
                    logging.error(f"Error fetching news: {str(result)}")
        
        # Remove duplicates and sort by relevance
        unique_news = self._deduplicate_news(all_news)
        sorted_news = self._sort_news_by_relevance(unique_news, topics)
        
        return sorted_news[:20]  # Return top 20 news items
    
    async def _get_yahoo_finance_news(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Get news from Yahoo Finance with improved error handling"""
        news_items = []
        
        try:
            # Use a smaller set of reliable tickers
            tickers = ["AAPL", "GOOGL", "MSFT"]
            
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
                                
                            if self._is_relevant_to_topics(title, topics):
                                news_items.append({
                                    "title": title,
                                    "summary": item.get("summary", "")[:200] + "..." if len(item.get("summary", "")) > 200 else item.get("summary", ""),
                                    "url": item.get("link", ""),
                                    "source": f"Yahoo Finance - {ticker}",
                                    "published_at": datetime.fromtimestamp(item.get("providerPublishTime", time.time())),
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
    
    async def _get_newsapi_news(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Get news from NewsAPI"""
        news_items = []
        
        if not self.news_api:
            return news_items
        
        try:
            # Get keywords for topics
            keywords = []
            for topic in topics:
                if topic in self.topic_keywords:
                    keywords.extend(self.topic_keywords[topic])
            
            # Search for news
            query = " OR ".join(keywords[:5])  # Limit to 5 keywords
            response = self.news_api.get_everything(
                q=query,
                language='en',
                sort_by='relevancy',
                page_size=20
            )
            
            for article in response.get("articles", []):
                if self._is_relevant_to_topics(article.get("title", ""), topics):
                    news_items.append({
                        "title": article.get("title", ""),
                        "summary": article.get("description", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", "NewsAPI"),
                        "published_at": datetime.fromisoformat(article.get("publishedAt", "").replace("Z", "+00:00")),
                        "relevance_score": self._calculate_relevance_score(article.get("title", ""), topics)
                    })
                    
        except Exception as e:
            logging.error(f"Error in NewsAPI news fetching: {str(e)}")
        
        return news_items
    
    async def _get_rss_news(self, topics: List[str]) -> List[Dict[str, Any]]:
        """Get news from RSS feeds"""
        news_items = []
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                
                for feed_name, feed_url in self.news_sources["rss_feeds"]["feeds"].items():
                    if self._is_feed_relevant_to_topics(feed_name, topics):
                        tasks.append(self._fetch_rss_feed(session, feed_url, feed_name))
                
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
    
    async def _fetch_rss_feed(self, session: aiohttp.ClientSession, feed_url: str, feed_name: str) -> List[Dict[str, Any]]:
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
                        
                        for entry in feed.entries[:5]:  # Get top 5 entries
                            news_items.append({
                                "title": entry.get("title", ""),
                                "summary": entry.get("summary", ""),
                                "url": entry.get("link", ""),
                                "source": f"RSS - {feed_name}",
                                "published_at": datetime.now(),  # RSS doesn't always have reliable dates
                                "relevance_score": 0.5  # Default relevance for RSS
                            })
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
            recent_news = await self.get_news_for_topics(["technology", "business", "politics", "science"])
            
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