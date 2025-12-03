"""
Configuration management for the Financial News Intelligence System
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    openai_api_key: str
    
    # Database paths
    chroma_db_path: str = "./data/chroma_db"
    sqlite_db_path: str = "./data/news_intelligence.db"
    
    # Model configuration
    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o-mini"
    similarity_threshold: float = 0.85
    
    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create data directories if they don't exist
        Path(self.chroma_db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.sqlite_db_path).parent.mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()
