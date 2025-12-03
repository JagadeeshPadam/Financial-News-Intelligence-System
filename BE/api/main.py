"""
FastAPI application for Financial News Intelligence System
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.langgraph_pipeline import news_pipeline
from agents.query_agent import query_agent
from agents.storage_agent import storage_agent

# Create FastAPI app
app = FastAPI(
    title="Financial News Intelligence API",
    description="AI-powered multi-agent system for financial news processing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class NewsArticle(BaseModel):
    headline: str
    content: str
    source: str
    timestamp: Optional[str] = None

class NewsArticleResponse(BaseModel):
    id: str
    headline: str
    content: str
    source: str
    timestamp: str
    is_duplicate: bool
    entities: Optional[dict] = None
    impacted_stocks: Optional[List[dict]] = None

class QueryRequest(BaseModel):
    query: str
    n_results: Optional[int] = 10

# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial News Intelligence API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/news/ingest")
async def ingest_news(article: NewsArticle):
    """
    Ingest a new news article
    
    Processes the article through the multi-agent pipeline:
    1. Ingestion & normalization
    2. Deduplication check
    3. Entity extraction
    4. Stock impact analysis
    5. Storage & indexing
    """
    try:
        # Convert Pydantic model to dict
        raw_article = {
            "headline": article.headline,
            "content": article.content,
            "source": article.source,
            "timestamp": article.timestamp or datetime.now().isoformat()
        }
        
        # Process through pipeline
        result = news_pipeline.process_article(raw_article)
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Extract processed article
        processed = result.get("normalized_article", {})
        
        return {
            "success": True,
            "article_id": processed.get("id"),
            "is_duplicate": result.get("is_duplicate", False),
            "parent_article_id": result.get("parent_article_id"),
            "entities": result.get("entities", {}),
            "impacted_stocks": result.get("impacted_stocks", []),
            "stored": result.get("stored", False)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/query")
async def query_news(
    q: str = Query(..., description="Natural language query"),
    limit: int = Query(10, description="Maximum number of results")
):
    """
    Query news articles using natural language
    
    Supports context-aware queries:
    - Company mentions: "HDFC Bank news"
    - Sector queries: "Banking sector update"
    - Regulator queries: "RBI policy changes"
    - Theme queries: "Interest rate impact"
    """
    try:
        results = query_agent.process_query(q, n_results=limit)
        
        return {
            "query": q,
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/{article_id}")
async def get_article(article_id: str):
    """Get a specific article by ID"""
    try:
        article = storage_agent.get_article_with_metadata(article_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stocks/{symbol}/news")
async def get_stock_news(
    symbol: str,
    limit: int = Query(20, description="Maximum number of results")
):
    """Get news for a specific stock symbol"""
    try:
        from database.structured_db import structured_db
        
        articles = structured_db.get_stock_articles(symbol.upper())
        
        # Enrich with metadata
        enriched = []
        for article in articles[:limit]:
            article["entities"] = structured_db.get_article_entities(article["id"])
            article["stocks"] = structured_db.get_article_stocks(article["id"])
            enriched.append(article)
        
        return {
            "symbol": symbol.upper(),
            "total_results": len(enriched),
            "results": enriched
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/entities")
async def get_entities():
    """Get all extracted entities"""
    try:
        from database.structured_db import structured_db
        
        entities = structured_db.get_all_entities()
        
        # Group by type
        grouped = {}
        for entity in entities:
            entity_type = entity["type"]
            if entity_type not in grouped:
                grouped[entity_type] = []
            grouped[entity_type].append({
                "name": entity["name"],
                "confidence": entity["confidence"]
            })
        
        return grouped
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/news/batch-ingest")
async def batch_ingest(articles: List[NewsArticle]):
    """Batch ingest multiple articles"""
    try:
        raw_articles = [
            {
                "headline": article.headline,
                "content": article.content,
                "source": article.source,
                "timestamp": article.timestamp or datetime.now().isoformat()
            }
            for article in articles
        ]
        
        results = news_pipeline.batch_process_articles(raw_articles)
        
        return {
            "success": True,
            "total_processed": len(results),
            "results": [
                {
                    "article_id": r.get("normalized_article", {}).get("id"),
                    "is_duplicate": r.get("is_duplicate", False),
                    "stored": r.get("stored", False)
                }
                for r in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )
