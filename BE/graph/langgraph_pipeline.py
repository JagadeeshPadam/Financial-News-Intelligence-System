"""
LangGraph Pipeline - Orchestrates multi-agent workflow
"""
from typing import TypedDict, Annotated, List, Any
from langgraph.graph import StateGraph, END
from datetime import datetime

# Import agents
from agents.news_ingestion_agent import news_ingestion_agent
from agents.deduplication_agent import deduplication_agent
from agents.entity_extraction_agent import entity_extraction_agent
from agents.stock_impact_agent import stock_impact_agent
from agents.storage_agent import storage_agent

class NewsProcessingState(TypedDict):
    """State schema for news processing pipeline"""
    raw_article: dict
    normalized_article: dict
    is_duplicate: bool
    parent_article_id: str
    entities: dict
    impacted_stocks: list
    stored: bool
    error: str

class NewsIntelligencePipeline:
    """LangGraph-based multi-agent pipeline for news processing"""
    
    def __init__(self):
        """Initialize the pipeline graph"""
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        # Create graph
        workflow = StateGraph(NewsProcessingState)
        
        # Add nodes (agents)
        workflow.add_node("ingest", self._ingest_node)
        workflow.add_node("deduplicate", self._deduplicate_node)
        workflow.add_node("extract_entities", self._extract_entities_node)
        workflow.add_node("analyze_impact", self._analyze_impact_node)
        workflow.add_node("store", self._store_node)
        
        # Define edges (flow)
        workflow.set_entry_point("ingest")
        workflow.add_edge("ingest", "deduplicate")
        
        # Conditional edge: if duplicate, skip to storage
        workflow.add_conditional_edges(
            "deduplicate",
            self._should_process_full,
            {
                True: "extract_entities",
                False: "store"
            }
        )
        
        workflow.add_edge("extract_entities", "analyze_impact")
        workflow.add_edge("analyze_impact", "store")
        workflow.add_edge("store", END)
        
        return workflow
    
    def _ingest_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Ingestion agent node"""
        try:
            normalized = news_ingestion_agent.process(state["raw_article"])
            state["normalized_article"] = normalized
        except Exception as e:
            state["error"] = f"Ingestion error: {str(e)}"
        return state
    
    def _deduplicate_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Deduplication agent node"""
        try:
            article = state["normalized_article"]
            
            # Generate embedding
            embedding = deduplication_agent.generate_embedding(article["full_text"])
            article["embedding"] = embedding
            
            # Check for duplicates
            dup_info = deduplication_agent.check_duplicate(
                article["full_text"],
                article_embedding=embedding
            )
            
            state["is_duplicate"] = dup_info["is_duplicate"]
            state["parent_article_id"] = dup_info.get("parent_article_id")
            
            # Update article with duplicate info
            article.update(dup_info)
            state["normalized_article"] = article
            
        except Exception as e:
            state["error"] = f"Deduplication error: {str(e)}"
        return state
    
    def _extract_entities_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Entity extraction agent node"""
        try:
            article = state["normalized_article"]
            article = entity_extraction_agent.extract_entities(article)
            state["normalized_article"] = article
            state["entities"] = article.get("entities", {})
        except Exception as e:
            state["error"] = f"Entity extraction error: {str(e)}"
        return state
    
    def _analyze_impact_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Stock impact analysis agent node"""
        try:
            article = state["normalized_article"]
            article = stock_impact_agent.analyze_impact(article)
            state["normalized_article"] = article
            state["impacted_stocks"] = article.get("impacted_stocks", [])
        except Exception as e:
            state["error"] = f"Impact analysis error: {str(e)}"
        return state
    
    def _store_node(self, state: NewsProcessingState) -> NewsProcessingState:
        """Storage agent node"""
        try:
            article = state["normalized_article"]
            article = storage_agent.store_article(article)
            state["stored"] = article.get("stored", False)
        except Exception as e:
            state["error"] = f"Storage error: {str(e)}"
        return state
    
    def _should_process_full(self, state: NewsProcessingState) -> bool:
        """Decide whether to process full pipeline or skip duplicates"""
        return not state.get("is_duplicate", False)
    
    def process_article(self, raw_article: dict) -> dict:
        """
        Process a single article through the pipeline
        
        Args:
            raw_article: Raw article data
            
        Returns:
            Final processed state
        """
        initial_state = {
            "raw_article": raw_article,
            "normalized_article": {},
            "is_duplicate": False,
            "parent_article_id": None,
            "entities": {},
            "impacted_stocks": [],
            "stored": False,
            "error": None
        }
        
        # Run the graph
        final_state = self.app.invoke(initial_state)
        
        return final_state
    
    def batch_process_articles(self, articles: List[dict]) -> List[dict]:
        """Process multiple articles"""
        results = []
        for article in articles:
            result = self.process_article(article)
            results.append(result)
        return results

# Global pipeline instance
news_pipeline = NewsIntelligencePipeline()
