"""
Deduplication Agent - Identifies and consolidates duplicate articles using semantic similarity
"""
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from config import settings
from database.vector_store import vector_store

class DeduplicationAgent:
    """Detects duplicate articles using semantic embeddings"""
    
    def __init__(self):
        """Initialize embeddings model"""
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        self.similarity_threshold = settings.similarity_threshold
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        return self.embeddings.embed_query(text)
    
    def check_duplicate(
        self,
        article_text: str,
        article_embedding: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Check if article is a duplicate of existing articles
        
        Args:
            article_text: Article text to check
            article_embedding: Pre-computed embedding (optional)
            
        Returns:
            Dictionary with is_duplicate flag and parent_article_id if duplicate
        """
        # Generate embedding if not provided
        if article_embedding is None:
            article_embedding = self.generate_embedding(article_text)
        
        # Search for similar articles in vector store
        if vector_store.count() == 0:
            return {
                "is_duplicate": False,
                "parent_article_id": None,
                "similarity_score": 0.0
            }
        
        results = vector_store.search_similar(
            query_embedding=article_embedding,
            n_results=5
        )
        
        # Check if any result exceeds similarity threshold
        if results["ids"] and len(results["ids"][0]) > 0:
            # Get the closest match
            closest_distance = results["distances"][0][0]
            # Convert distance to similarity (ChromaDB uses L2 distance)
            # For normalized vectors, similarity = 1 - (distance^2 / 2)
            similarity = 1 - (closest_distance ** 2 / 2)
            
            if similarity >= self.similarity_threshold:
                return {
                    "is_duplicate": True,
                    "parent_article_id": results["ids"][0][0],
                    "similarity_score": float(similarity)
                }
        
        return {
            "is_duplicate": False,
            "parent_article_id": None,
            "similarity_score": 0.0
        }
    
    def batch_check_duplicates(
        self,
        articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Batch check multiple articles for duplicates
        
        Args:
            articles: List of articles with 'full_text' field
            
        Returns:
            List of articles with duplicate information added
        """
        results = []
        
        for article in articles:
            # Generate embedding
            embedding = self.generate_embedding(article["full_text"])
            article["embedding"] = embedding
            
            # Check for duplicates
            dup_info = self.check_duplicate(
                article["full_text"],
                article_embedding=embedding
            )
            
            article.update(dup_info)
            results.append(article)
        
        return results

# Global agent instance
deduplication_agent = DeduplicationAgent()
