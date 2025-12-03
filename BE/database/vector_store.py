"""
Vector database using ChromaDB for semantic search
"""
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
from config import settings

class VectorStore:
    """Manages ChromaDB vector store for article embeddings"""
    
    def __init__(self):
        """Initialize ChromaDB client"""
        self.client = chromadb.PersistentClient(
            path=settings.chroma_db_path,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collection for articles
        self.collection = self.client.get_or_create_collection(
            name="news_articles",
            metadata={"description": "Financial news articles with embeddings"}
        )
    
    def add_article(
        self,
        article_id: str,
        embedding: List[float],
        metadata: Dict,
        text: str
    ):
        """
        Add an article embedding to the vector store
        
        Args:
            article_id: Unique article identifier
            embedding: Article embedding vector
            metadata: Article metadata (source, timestamp, etc.)
            text: Article text content
        """
        self.collection.add(
            ids=[article_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[text]
        )
    
    def search_similar(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar articles using vector similarity
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filters
            
        Returns:
            Dictionary with ids, distances, metadatas, and documents
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )
        return results
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Get a specific article by ID"""
        try:
            result = self.collection.get(
                ids=[article_id],
                include=["metadatas", "documents", "embeddings"]
            )
            if result["ids"]:
                return {
                    "id": result["ids"][0],
                    "metadata": result["metadatas"][0],
                    "document": result["documents"][0],
                    "embedding": result["embeddings"][0]
                }
            return None
        except Exception:
            return None
    
    def delete_article(self, article_id: str):
        """Delete an article from the vector store"""
        self.collection.delete(ids=[article_id])
    
    def get_all_articles(self) -> List[Dict]:
        """Get all articles from the vector store"""
        result = self.collection.get(
            include=["metadatas", "documents"]
        )
        articles = []
        for i, article_id in enumerate(result["ids"]):
            articles.append({
                "id": article_id,
                "metadata": result["metadatas"][i],
                "document": result["documents"][i]
            })
        return articles
    
    def count(self) -> int:
        """Get total number of articles in the store"""
        return self.collection.count()

# Global vector store instance
vector_store = VectorStore()
