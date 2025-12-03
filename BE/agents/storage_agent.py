"""
Storage & Indexing Agent - Persists articles to databases
"""
from typing import Dict, Any
from database.vector_store import vector_store
from database.structured_db import structured_db
from database.stock_mapping import SYMBOL_TO_SECTORS

class StorageAgent:
    """Handles storage of articles in vector and structured databases"""
    
    def store_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store article in both vector and structured databases
        
        Args:
            article: Processed article with all metadata
            
        Returns:
            Article with storage confirmation
        """
        article_id = article["id"]
        
        # Skip storage if it's a duplicate
        if article.get("is_duplicate", False):
            # Still store reference to parent
            structured_db.add_article(
                article_id=article_id,
                headline=article["headline"],
                content=article["content"],
                source=article["source"],
                timestamp=article["timestamp"],
                is_duplicate=True,
                parent_article_id=article.get("parent_article_id")
            )
            article["stored"] = True
            article["storage_type"] = "duplicate_reference"
            return article
        
        # 1. Store in vector database
        vector_store.add_article(
            article_id=article_id,
            embedding=article["embedding"],
            metadata={
                "source": article["source"],
                "timestamp": article["timestamp"].isoformat(),
                "headline": article["headline"]
            },
            text=article["full_text"]
        )
        
        # 2. Store in structured database
        structured_db.add_article(
            article_id=article_id,
            headline=article["headline"],
            content=article["content"],
            source=article["source"],
            timestamp=article["timestamp"],
            is_duplicate=False
        )
        
        # 3. Store entities
        for entity in article.get("all_entities", []):
            entity_id = structured_db.add_entity(
                name=entity["name"],
                entity_type=entity["type"],
                confidence=entity.get("confidence", 1.0)
            )
            structured_db.link_article_entity(article_id, entity_id)
        
        # 4. Store stock impacts
        for stock in article.get("impacted_stocks", []):
            # Add stock if not exists
            sectors = SYMBOL_TO_SECTORS.get(stock["symbol"], [])
            sector = sectors[0] if sectors else "Unknown"
            
            structured_db.add_stock(
                symbol=stock["symbol"],
                name=stock["symbol"],  # We could enhance this with full names
                sector=sector
            )
            
            # Link article to stock
            structured_db.link_article_stock(
                article_id=article_id,
                stock_symbol=stock["symbol"],
                confidence=stock["confidence"],
                impact_type=stock["impact_type"]
            )
        
        article["stored"] = True
        article["storage_type"] = "full"
        return article
    
    def get_article_with_metadata(self, article_id: str) -> Dict[str, Any]:
        """Retrieve article with all metadata from databases"""
        # Get from structured DB
        article = structured_db.get_article(article_id)
        if not article:
            return None
        
        # Get entities
        article["entities"] = structured_db.get_article_entities(article_id)
        
        # Get stocks
        article["stocks"] = structured_db.get_article_stocks(article_id)
        
        return article

# Global agent instance
storage_agent = StorageAgent()
