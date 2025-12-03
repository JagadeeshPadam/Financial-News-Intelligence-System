"""
News Ingestion Agent - Validates and normalizes incoming articles
"""
from typing import Dict, Any
from datetime import datetime
import hashlib
import re

class NewsIngestionAgent:
    """Handles ingestion and normalization of news articles"""
    
    def process(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and normalize incoming article
        
        Args:
            article: Raw article data with headline, content, source, timestamp
            
        Returns:
            Normalized article with generated ID and cleaned data
        """
        # Generate unique article ID
        article_id = self._generate_article_id(
            article.get("headline", ""),
            article.get("source", ""),
            article.get("timestamp", "")
        )
        
        # Normalize timestamp
        timestamp = self._normalize_timestamp(article.get("timestamp"))
        
        # Clean and normalize text
        headline = self._clean_text(article.get("headline", ""))
        content = self._clean_text(article.get("content", ""))
        
        return {
            "id": article_id,
            "headline": headline,
            "content": content,
            "source": article.get("source", "Unknown"),
            "timestamp": timestamp,
            "full_text": f"{headline}. {content}"
        }
    
    def _generate_article_id(self, headline: str, source: str, timestamp: str) -> str:
        """Generate unique ID for article"""
        combined = f"{headline}_{source}_{timestamp}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _normalize_timestamp(self, timestamp: Any) -> datetime:
        """Normalize timestamp to datetime object"""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except Exception:
                return datetime.now()
        else:
            return datetime.now()
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:\-\'\"()]', '', text)
        return text.strip()

# Global agent instance
news_ingestion_agent = NewsIngestionAgent()
