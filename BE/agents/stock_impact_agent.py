"""
Stock Impact Analysis Agent - Maps entities to impacted stocks with confidence scores
"""
from typing import List, Dict, Any
from database.stock_mapping import (
    COMPANY_TO_SYMBOL,
    SECTORS,
    SYMBOL_TO_SECTORS,
    is_regulator
)

class StockImpactAgent:
    """Maps news to impacted stocks with confidence scores"""
    
    def analyze_impact(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze stock impact based on extracted entities
        
        Args:
            article: Article with extracted entities
            
        Returns:
            Article with impacted_stocks added
        """
        entities = article.get("entities", {})
        impacted_stocks = []
        seen_symbols = set()
        
        # 1. Direct company mentions (confidence = 1.0)
        for company in entities.get("companies", []):
            symbol = self._get_stock_symbol(company)
            if symbol and symbol not in seen_symbols:
                impacted_stocks.append({
                    "symbol": symbol,
                    "confidence": 1.0,
                    "impact_type": "direct",
                    "reason": f"Direct mention: {company}"
                })
                seen_symbols.add(symbol)
        
        # 2. Sector-wide impact (confidence = 0.7)
        for sector in entities.get("sectors", []):
            sector_stocks = SECTORS.get(sector, [])
            for symbol in sector_stocks:
                if symbol not in seen_symbols:
                    impacted_stocks.append({
                        "symbol": symbol,
                        "confidence": 0.7,
                        "impact_type": "sector",
                        "reason": f"Sector impact: {sector}"
                    })
                    seen_symbols.add(symbol)
        
        # 3. Regulatory impact (confidence = 0.6)
        for regulator in entities.get("regulators", []):
            if is_regulator(regulator):
                # RBI affects banking sector
                if "RBI" in regulator or "Reserve Bank" in regulator:
                    banking_stocks = SECTORS.get("Banking", [])
                    for symbol in banking_stocks:
                        if symbol not in seen_symbols:
                            impacted_stocks.append({
                                "symbol": symbol,
                                "confidence": 0.6,
                                "impact_type": "regulatory",
                                "reason": f"Regulatory impact: {regulator}"
                            })
                            seen_symbols.add(symbol)
                
                # SEBI affects all listed companies - limit to mentioned sectors
                elif "SEBI" in regulator:
                    for sector in entities.get("sectors", []):
                        sector_stocks = SECTORS.get(sector, [])
                        for symbol in sector_stocks:
                            if symbol not in seen_symbols:
                                impacted_stocks.append({
                                    "symbol": symbol,
                                    "confidence": 0.5,
                                    "impact_type": "regulatory",
                                    "reason": f"Regulatory impact: {regulator}"
                                })
                                seen_symbols.add(symbol)
        
        # Sort by confidence (highest first)
        impacted_stocks.sort(key=lambda x: x["confidence"], reverse=True)
        
        article["impacted_stocks"] = impacted_stocks
        return article
    
    def _get_stock_symbol(self, company_name: str) -> str:
        """Get stock symbol for company name"""
        # Try exact match
        if company_name in COMPANY_TO_SYMBOL:
            return COMPANY_TO_SYMBOL[company_name]
        
        # Try partial match (case-insensitive)
        company_lower = company_name.lower()
        for name, symbol in COMPANY_TO_SYMBOL.items():
            if company_lower in name.lower() or name.lower() in company_lower:
                return symbol
        
        return None

# Global agent instance
stock_impact_agent = StockImpactAgent()
