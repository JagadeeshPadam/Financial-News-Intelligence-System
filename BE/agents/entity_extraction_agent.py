"""
Entity Extraction Agent - Extracts financial entities using NER and LLM
"""
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from config import settings
import json
import re

class EntityExtractionAgent:
    """Extracts structured entities from financial news"""
    
    def __init__(self):
        """Initialize LLM for entity extraction"""
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            temperature=0
        )
        
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a financial entity extraction expert. 
Extract the following entity types from financial news:
- Companies: Company names mentioned
- Sectors: Industry sectors (Banking, IT, Pharmaceuticals, etc.)
- Regulators: Regulatory bodies (RBI, SEBI, etc.)
- People: Key people mentioned (CEOs, analysts, etc.)
- Events: Financial events (dividend announcements, policy changes, etc.)

Return ONLY a JSON object with these exact keys: companies, sectors, regulators, people, events.
Each value should be a list of strings. If a category has no entities, return an empty list.

Example:
{{
  "companies": ["HDFC Bank", "ICICI Bank"],
  "sectors": ["Banking", "Financial Services"],
  "regulators": ["RBI"],
  "people": ["John Doe"],
  "events": ["Dividend announcement", "Interest rate hike"]
}}"""),
            ("human", "Extract entities from this financial news:\n\nHeadline: {headline}\n\nContent: {content}")
        ])
    
    def extract_entities(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract entities from article
        
        Args:
            article: Article with headline and content
            
        Returns:
            Article with extracted entities added
        """
        try:
            # Use LLM for entity extraction
            chain = self.extraction_prompt | self.llm
            response = chain.invoke({
                "headline": article.get("headline", ""),
                "content": article.get("content", "")
            })
            
            # Parse JSON response
            entities = self._parse_llm_response(response.content)
            
            # Add entities to article
            article["entities"] = entities
            
            # Flatten entities for easier processing
            article["all_entities"] = self._flatten_entities(entities)
            
        except Exception as e:
            print(f"Entity extraction error: {e}")
            article["entities"] = {
                "companies": [],
                "sectors": [],
                "regulators": [],
                "people": [],
                "events": []
            }
            article["all_entities"] = []
        
        return article
    
    def _parse_llm_response(self, response: str) -> Dict[str, List[str]]:
        """Parse LLM JSON response"""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group())
                # Ensure all expected keys exist
                for key in ["companies", "sectors", "regulators", "people", "events"]:
                    if key not in entities:
                        entities[key] = []
                return entities
        except Exception:
            pass
        
        # Return empty entities if parsing fails
        return {
            "companies": [],
            "sectors": [],
            "regulators": [],
            "people": [],
            "events": []
        }
    
    def _flatten_entities(self, entities: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Flatten entities into a list with types"""
        flattened = []
        for entity_type, entity_list in entities.items():
            for entity_name in entity_list:
                flattened.append({
                    "name": entity_name,
                    "type": entity_type.rstrip('s'),  # Remove plural 's'
                    "confidence": 0.9
                })
        return flattened

# Global agent instance
entity_extraction_agent = EntityExtractionAgent()
