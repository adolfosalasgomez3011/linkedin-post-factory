"""
News Service - Fetch trending news from NewsAPI
"""
import requests
import os
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class NewsService:
    """Fetch trending and relevant news articles"""
    
    def __init__(self):
        self.api_key = os.getenv("NEWSAPI_KEY")
        self.base_url = "https://newsapi.org/v2"
        
        # Reputable sources only
        self.trusted_sources = [
            "techcrunch", "wired", "the-verge", "ars-technica",
            "bbc-news", "cnn", "reuters", "the-wall-street-journal",
            "bloomberg", "financial-times", "business-insider",
            "the-washington-post", "the-new-york-times"
        ]
    
    def search_trending_news(
        self,
        query: str,
        pillar: str = None,
        max_results: int = 5
    ) -> List[Dict]:
        """
        Search for trending news articles
        
        Args:
            query: Search keywords
            pillar: Content pillar for context (AI & Innovation, etc.)
            max_results: Number of articles to return
            
        Returns:
            List of article dictionaries with title, description, url, image, source, publishedAt
        """
        if not self.api_key:
            raise Exception("NEWSAPI_KEY not configured")
        
        # Build query based on pillar
        if pillar:
            pillar_keywords = {
                "AI & Innovation": "artificial intelligence OR machine learning OR AI OR innovation",
                "Leadership": "leadership OR management OR business strategy",
                "Career Growth": "career OR professional development OR job market",
                "Tech & Tools": "technology OR software OR tools OR apps"
            }
            search_query = pillar_keywords.get(pillar, query) if not query else query
        else:
            search_query = query
        
        # Get articles from last 7 days, sorted by popularity
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        params = {
            "q": search_query,
            "from": from_date,
            "sortBy": "popularity",  # Most viral
            "language": "en",
            "apiKey": self.api_key,
            "pageSize": max_results * 2  # Get extra to filter
        }
        
        # Add sources filter if available
        if self.trusted_sources:
            params["sources"] = ",".join(self.trusted_sources)
        
        try:
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            
            # Filter and format
            results = []
            for article in articles[:max_results]:
                # Skip if no image
                if not article.get("urlToImage"):
                    continue
                
                results.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "image_url": article.get("urlToImage", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", ""),
                    "author": article.get("author", "")
                })
            
            return results
        
        except requests.exceptions.RequestException as e:
            print(f"NewsAPI error: {e}")
            return []
    
    def get_top_headlines(self, category: str = "technology", max_results: int = 5) -> List[Dict]:
        """
        Get top headlines by category
        
        Args:
            category: business, entertainment, general, health, science, sports, technology
            max_results: Number of articles
            
        Returns:
            List of formatted articles
        """
        if not self.api_key:
            raise Exception("NEWSAPI_KEY not configured")
        
        params = {
            "category": category,
            "language": "en",
            "apiKey": self.api_key,
            "pageSize": max_results
        }
        
        try:
            response = requests.get(f"{self.base_url}/top-headlines", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            results = []
            
            for article in articles:
                if not article.get("urlToImage"):
                    continue
                
                results.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "image_url": article.get("urlToImage", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "published_at": article.get("publishedAt", "")
                })
            
            return results
        
        except requests.exceptions.RequestException as e:
            print(f"NewsAPI error: {e}")
            return []


# Global instance
news_service = NewsService()
