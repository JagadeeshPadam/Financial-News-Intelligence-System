"""
Query Processing Agent - Handles context-aware natural language queries
"""
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from database.vector_store import vector_store
from database.structured_db import structured_db
from database.stock_mapping import COMPANY_TO_SYMBOL, SECTORS
from config import settings
import json
import re

class QueryAgent:
    """Processes natural language queries with context expansion"""
    
    def __init__(self):
        """Initialize embeddings and LLM"""
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            temperature=0
        )
        
        self.query_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial query analyzer. Extract search intent from queries.
Identify:
- Companies mentioned
- Sectors mentioned
- Regulators mentioned
- Topics/themes
- Stock symbols

Return JSON with: {{"companies": [...], "sectors": [...], "regulators": [...], "topics": [...], "symbols": [...]}}
If nothing found for a category, return empty list."""),
            ("human", "Analyze this query: {query}")
        ])
    
    def process_query(
        self,
        query: str,
        n_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Process natural language query and return relevant articles
        
        Args:
            query: Natural language query
            n_results: Maximum number of results
            
        Returns:
            List of relevant articles with metadata
        """
        # 1. Analyze query to extract entities and intent
        query_entities = self._analyze_query(query)
        
        # 2. Hybrid search: semantic + entity-based
        results = self._hybrid_search(query, query_entities, n_results)
        
        # 3. Enrich results with metadata
        enriched_results = self._enrich_results(results)
        
        return enriched_results
    
    def _analyze_query(self, query: str) -> Dict[str, List[str]]:
        """Analyze query to extract entities and intent"""
        try:
            chain = self.query_analysis_prompt | self.llm
            response = chain.invoke({"query": query})
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group())
                return entities
        except Exception as e:
            print(f"Query analysis error: {e}")
        
        # Fallback: simple keyword extraction
        return self._simple_keyword_extraction(query)
    
    def _simple_keyword_extraction(self, query: str) -> Dict[str, List[str]]:
        """Simple keyword extraction as fallback"""
        query_lower = query.lower()
        
        entities = {
            "companies": [],
            "sectors": [],
            "regulators": [],
            "topics": [],
            "symbols": []
        }
        
        # Check for company names
        for company, symbol in COMPANY_TO_SYMBOL.items():
            if company.lower() in query_lower:
                entities["companies"].append(company)
                entities["symbols"].append(symbol)
        
        # Check for sectors
        for sector in SECTORS.keys():
            if sector.lower() in query_lower:
                entities["sectors"].append(sector)
        
        # Check for regulators
        if "rbi" in query_lower or "reserve bank" in query_lower:
            entities["regulators"].append("RBI")
        if "sebi" in query_lower:
            entities["regulators"].append("SEBI")
        
        return entities
    
    def _hybrid_search(
        self,
        query: str,
        query_entities: Dict[str, List[str]],
        n_results: int
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and entity-based search"""
        results = []
        seen_ids = set()
        
        # 1. Entity-based search (companies)
        for company in query_entities.get("companies", []):
            articles = structured_db.search_articles_by_entity(company)
            for article in articles[:n_results]:
                if article["id"] not in seen_ids:
                    article["relevance_reason"] = f"Direct mention: {company}"
                    article["relevance_score"] = 1.0
                    results.append(article)
                    seen_ids.add(article["id"])
        
        # 2. Stock symbol search
        for symbol in query_entities.get("symbols", []):
            articles = structured_db.get_stock_articles(symbol)
            for article in articles[:n_results]:
                if article["id"] not in seen_ids:
                    article["relevance_reason"] = f"Stock impact: {symbol}"
                    article["relevance_score"] = 0.9
                    results.append(article)
                    seen_ids.add(article["id"])
        
        # 3. Sector expansion (context-aware)
        for sector in query_entities.get("sectors", []):
            sector_articles = structured_db.search_articles_by_entity(sector)
            for article in sector_articles[:n_results]:
                if article["id"] not in seen_ids:
                    article["relevance_reason"] = f"Sector-wide: {sector}"
                    article["relevance_score"] = 0.8
                    results.append(article)
                    seen_ids.add(article["id"])
        
        # 4. Semantic search for remaining slots
        if len(results) < n_results:
            query_embedding = self.embeddings.embed_query(query)
            semantic_results = vector_store.search_similar(
                query_embedding=query_embedding,
                n_results=n_results * 2
            )
            
            if semantic_results["ids"] and len(semantic_results["ids"][0]) > 0:
                for i, article_id in enumerate(semantic_results["ids"][0]):
                    if article_id not in seen_ids:
                        article = structured_db.get_article(article_id)
                        if article:
                            # Calculate relevance score from distance
                            distance = semantic_results["distances"][0][i]
                            similarity = 1 - (distance ** 2 / 2)
                            
                            article["relevance_reason"] = "Semantic match"
                            article["relevance_score"] = float(similarity)
                            results.append(article)
                            seen_ids.add(article_id)
                            
                            if len(results) >= n_results:
                                break
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return results[:n_results]
    
    def _enrich_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich results with entities and stock impacts"""
        enriched = []
        
        for article in results:
            # Get entities
            entities = structured_db.get_article_entities(article["id"])
            article["entities"] = entities
            
            # Get stocks
            stocks = structured_db.get_article_stocks(article["id"])
            article["stocks"] = stocks
            
            enriched.append(article)
        
        return enriched

# Global agent instance
query_agent = QueryAgent()
