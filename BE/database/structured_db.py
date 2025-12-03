"""
SQLite structured database for entities, stocks, and relationships
"""
import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from config import settings
import json

class StructuredDB:
    """Manages SQLite database for structured data"""
    
    def __init__(self):
        """Initialize database and create tables"""
        self.db_path = settings.sqlite_db_path
        self.init_tables()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_tables(self):
        """Create database tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                headline TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                timestamp DATETIME,
                is_duplicate BOOLEAN DEFAULT 0,
                parent_article_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_article_id) REFERENCES articles(id)
            )
        """)
        
        # Entities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                confidence REAL,
                UNIQUE(name, type)
            )
        """)
        
        # Stocks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                sector TEXT
            )
        """)
        
        # Article-Entity junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS article_entities (
                article_id TEXT,
                entity_id INTEGER,
                PRIMARY KEY (article_id, entity_id),
                FOREIGN KEY (article_id) REFERENCES articles(id),
                FOREIGN KEY (entity_id) REFERENCES entities(id)
            )
        """)
        
        # Article-Stock junction table with confidence
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS article_stocks (
                article_id TEXT,
                stock_symbol TEXT,
                confidence REAL,
                impact_type TEXT,
                PRIMARY KEY (article_id, stock_symbol),
                FOREIGN KEY (article_id) REFERENCES articles(id),
                FOREIGN KEY (stock_symbol) REFERENCES stocks(symbol)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_article(
        self,
        article_id: str,
        headline: str,
        content: str,
        source: str,
        timestamp: datetime,
        is_duplicate: bool = False,
        parent_article_id: Optional[str] = None
    ):
        """Add a new article to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO articles 
            (id, headline, content, source, timestamp, is_duplicate, parent_article_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (article_id, headline, content, source, timestamp, is_duplicate, parent_article_id))
        
        conn.commit()
        conn.close()
    
    def add_entity(self, name: str, entity_type: str, confidence: float = 1.0) -> int:
        """Add an entity and return its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO entities (name, type, confidence)
            VALUES (?, ?, ?)
        """, (name, entity_type, confidence))
        
        cursor.execute("""
            SELECT id FROM entities WHERE name = ? AND type = ?
        """, (name, entity_type))
        
        entity_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        return entity_id
    
    def link_article_entity(self, article_id: str, entity_id: int):
        """Link an article to an entity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR IGNORE INTO article_entities (article_id, entity_id)
            VALUES (?, ?)
        """, (article_id, entity_id))
        
        conn.commit()
        conn.close()
    
    def add_stock(self, symbol: str, name: str, sector: str):
        """Add a stock to the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO stocks (symbol, name, sector)
            VALUES (?, ?, ?)
        """, (symbol, name, sector))
        
        conn.commit()
        conn.close()
    
    def link_article_stock(
        self,
        article_id: str,
        stock_symbol: str,
        confidence: float,
        impact_type: str
    ):
        """Link an article to a stock with confidence and impact type"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO article_stocks 
            (article_id, stock_symbol, confidence, impact_type)
            VALUES (?, ?, ?, ?)
        """, (article_id, stock_symbol, confidence, impact_type))
        
        conn.commit()
        conn.close()
    
    def get_article(self, article_id: str) -> Optional[Dict]:
        """Get an article by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM articles WHERE id = ?
        """, (article_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_article_entities(self, article_id: str) -> List[Dict]:
        """Get all entities for an article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.* FROM entities e
            JOIN article_entities ae ON e.id = ae.entity_id
            WHERE ae.article_id = ?
        """, (article_id,))
        
        entities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entities
    
    def get_article_stocks(self, article_id: str) -> List[Dict]:
        """Get all stocks for an article"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.*, ast.confidence, ast.impact_type 
            FROM stocks s
            JOIN article_stocks ast ON s.symbol = ast.stock_symbol
            WHERE ast.article_id = ?
            ORDER BY ast.confidence DESC
        """, (article_id,))
        
        stocks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return stocks
    
    def get_stock_articles(self, stock_symbol: str) -> List[Dict]:
        """Get all articles for a stock"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.*, ast.confidence, ast.impact_type 
            FROM articles a
            JOIN article_stocks ast ON a.id = ast.article_id
            WHERE ast.stock_symbol = ? AND a.is_duplicate = 0
            ORDER BY a.timestamp DESC
        """, (stock_symbol,))
        
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return articles
    
    def get_all_entities(self) -> List[Dict]:
        """Get all entities"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM entities")
        entities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return entities
    
    def search_articles_by_entity(self, entity_name: str) -> List[Dict]:
        """Search articles by entity name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT a.* FROM articles a
            JOIN article_entities ae ON a.id = ae.article_id
            JOIN entities e ON ae.entity_id = e.id
            WHERE e.name LIKE ? AND a.is_duplicate = 0
            ORDER BY a.timestamp DESC
        """, (f"%{entity_name}%",))
        
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return articles

# Global database instance
structured_db = StructuredDB()
