"""
Stock symbol mapping and sector relationships for Indian markets
"""

# Company name to stock symbol mapping
COMPANY_TO_SYMBOL = {
    # Banking
    "HDFC Bank": "HDFCBANK",
    "HDFC": "HDFCBANK",
    "ICICI Bank": "ICICIBANK",
    "ICICI": "ICICIBANK",
    "State Bank of India": "SBIN",
    "SBI": "SBIN",
    "Axis Bank": "AXISBANK",
    "Kotak Mahindra Bank": "KOTAKBANK",
    "Kotak Bank": "KOTAKBANK",
    "Yes Bank": "YESBANK",
    "IndusInd Bank": "INDUSINDBK",
    "Bank of Baroda": "BANKBARODA",
    "Punjab National Bank": "PNB",
    "Canara Bank": "CANBK",
    
    # IT Services
    "Tata Consultancy Services": "TCS",
    "TCS": "TCS",
    "Infosys": "INFY",
    "Wipro": "WIPRO",
    "HCL Technologies": "HCLTECH",
    "HCL": "HCLTECH",
    "Tech Mahindra": "TECHM",
    "LTI Mindtree": "LTIM",
    "Mphasis": "MPHASIS",
    
    # Automobiles
    "Maruti Suzuki": "MARUTI",
    "Maruti": "MARUTI",
    "Tata Motors": "TATAMOTORS",
    "Mahindra & Mahindra": "M&M",
    "M&M": "M&M",
    "Bajaj Auto": "BAJAJ-AUTO",
    "Hero MotoCorp": "HEROMOTOCO",
    "Eicher Motors": "EICHERMOT",
    
    # Pharmaceuticals
    "Sun Pharmaceutical": "SUNPHARMA",
    "Sun Pharma": "SUNPHARMA",
    "Dr. Reddy's Laboratories": "DRREDDY",
    "Dr Reddy's": "DRREDDY",
    "Cipla": "CIPLA",
    "Lupin": "LUPIN",
    "Aurobindo Pharma": "AUROPHARMA",
    "Divi's Laboratories": "DIVISLAB",
    
    # FMCG
    "Hindustan Unilever": "HINDUNILVR",
    "HUL": "HINDUNILVR",
    "ITC": "ITC",
    "Nestle India": "NESTLEIND",
    "Britannia": "BRITANNIA",
    "Dabur": "DABUR",
    
    # Energy
    "Reliance Industries": "RELIANCE",
    "Reliance": "RELIANCE",
    "ONGC": "ONGC",
    "Indian Oil": "IOC",
    "BPCL": "BPCL",
    "HPCL": "HPCL",
    
    # Telecom
    "Bharti Airtel": "BHARTIARTL",
    "Airtel": "BHARTIARTL",
    "Reliance Jio": "RELIANCE",
    "Jio": "RELIANCE",
}

# Sector definitions
SECTORS = {
    "Banking": [
        "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK",
        "YESBANK", "INDUSINDBK", "BANKBARODA", "PNB", "CANBK"
    ],
    "Financial Services": [
        "HDFCBANK", "ICICIBANK", "SBIN", "AXISBANK", "KOTAKBANK"
    ],
    "IT": [
        "TCS", "INFY", "WIPRO", "HCLTECH", "TECHM", "LTIM", "MPHASIS"
    ],
    "Automobiles": [
        "MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "HEROMOTOCO", "EICHERMOT"
    ],
    "Pharmaceuticals": [
        "SUNPHARMA", "DRREDDY", "CIPLA", "LUPIN", "AUROPHARMA", "DIVISLAB"
    ],
    "FMCG": [
        "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR"
    ],
    "Energy": [
        "RELIANCE", "ONGC", "IOC", "BPCL", "HPCL"
    ],
    "Telecom": [
        "BHARTIARTL", "RELIANCE"
    ]
}

# Stock symbol to sector mapping
SYMBOL_TO_SECTORS = {}
for sector, symbols in SECTORS.items():
    for symbol in symbols:
        if symbol not in SYMBOL_TO_SECTORS:
            SYMBOL_TO_SECTORS[symbol] = []
        SYMBOL_TO_SECTORS[symbol].append(sector)

# Regulatory bodies
REGULATORS = [
    "Reserve Bank of India",
    "RBI",
    "SEBI",
    "Securities and Exchange Board of India",
    "Ministry of Finance",
    "Finance Ministry",
    "Government of India"
]

def get_stock_symbol(company_name: str) -> str:
    """Get stock symbol for a company name"""
    return COMPANY_TO_SYMBOL.get(company_name)

def get_sector_stocks(sector: str) -> list:
    """Get all stock symbols in a sector"""
    return SECTORS.get(sector, [])

def get_stock_sectors(symbol: str) -> list:
    """Get all sectors for a stock symbol"""
    return SYMBOL_TO_SECTORS.get(symbol, [])

def is_regulator(entity: str) -> bool:
    """Check if entity is a regulatory body"""
    return entity in REGULATORS
