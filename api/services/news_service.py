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
                "Tech Leadership": "leadership OR management OR business strategy OR technology leadership",
                "Career Growth": "career OR professional development OR job market",
                "Industry Insights": "industry trends OR market analysis OR business insights",
                "Personal Brand": "personal branding OR professional presence OR thought leadership"
            }
            
            # Sector filter: Weight results heavily towards mining, energy, construction (60% target)
            sector_keywords = "mining OR minerals OR energy OR construction OR extraction OR oil and gas OR mining technology OR mining operations OR renewable energy OR infrastructure OR mining equipment OR mineral resources"
            
            # Regional filter: Weight South America/Peru (30-40% target)
            regional_keywords = "South America OR Latin America OR Peru OR Chile OR Brazil OR Argentina OR Colombia OR Peruvian OR Sudamerica OR Latinoamerica"
            
            # Combine pillar + sector + regional keywords to weight search results
            base_query = pillar_keywords.get(pillar, pillar)
            search_query = f"({base_query}) AND (({sector_keywords}) OR ({regional_keywords}))"
            
            if query:
                search_query = f"{search_query} AND {query}"
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
            "pageSize": 100  # Get many articles from all sources for diversity
        }
        
        # Don't filter by sources - get from all reputable sources for broader coverage
        
        try:
            response = requests.get(f"{self.base_url}/everything", params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            
            # Filter and format with source diversity
            results = []
            source_count = {}
            
            # First pass: strict diversity (max 2 per source, require image)
            for article in articles:
                if len(results) >= max_results:
                    break
                    
                if not article.get("urlToImage"):
                    continue
                
                source_name = article.get("source", {}).get("name", "Unknown")
                
                # Limit articles per source to ensure diversity (max 2 per source)
                if source_count.get(source_name, 0) >= 2:
                    continue
                
                results.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "image_url": article.get("urlToImage", ""),
                    "source": source_name,
                    "published_at": article.get("publishedAt", ""),
                    "author": article.get("author", "")
                })
                
                source_count[source_name] = source_count.get(source_name, 0) + 1
            
            # Second pass: if we don't have enough, relax constraints
            if len(results) < max_results:
                for article in articles:
                    if len(results) >= max_results:
                        break
                    
                    # Skip if already added
                    if article.get("url") in [r["url"] for r in results]:
                        continue
                    
                    # Accept articles without images if needed
                    source_name = article.get("source", {}).get("name", "Unknown")
                    
                    results.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "image_url": article.get("urlToImage", ""),
                        "source": source_name,
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
